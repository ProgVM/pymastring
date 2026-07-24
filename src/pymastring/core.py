import array
import builtins
import ctypes
import gc
import json
import math

ALL_METHODS = [
    "add", "radd", "sub", "rsub", "mul", "rmul", "truediv", "rtruediv",
    "floordiv", "rfloordiv", "mod", "rmod", "divmod", "rdivmod",
    "pow", "rpow", "matmul", "rmatmul", "len", "getitem",
    "neg", "invert", "abs", "int", "float", "round",
    "lshift", "rlshift", "rshift", "rrshift",
    "and", "rand", "or", "ror", "xor", "rxor",
    "gt", "lt", "ge", "le", "eq", "ne",
    "iter", "reversed"
]

# Try importing numpy for SIMD vector acceleration if available
try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

# Save original builtin string descriptors BEFORE patch_strings runs
_ORIGINAL_STR_ADD = str.__dict__["__add__"]
_ORIGINAL_STR_MUL = str.__dict__["__mul__"]
_ORIGINAL_STR_GETITEM = str.__dict__["__getitem__"]
_ORIGINAL_STR_EQ = str.__dict__["__eq__"]

# Save original types
_ORIG_INT_TYPE = builtins.int
_ORIG_FLOAT_TYPE = builtins.float

# Direct references to native CPython C-API functions
_PyUnicode_Format = ctypes.pythonapi.PyUnicode_Format
_PyUnicode_Format.argtypes = [ctypes.py_object, ctypes.py_object]
_PyUnicode_Format.restype = ctypes.py_object

_PyUnicode_GetLength = ctypes.pythonapi.PyUnicode_GetLength
_PyUnicode_GetLength.argtypes = [ctypes.py_object]
_PyUnicode_GetLength.restype = ctypes.c_ssize_t

_PyLong_FromUnicodeObject = ctypes.pythonapi.PyLong_FromUnicodeObject
_PyLong_FromUnicodeObject.argtypes = [ctypes.py_object, ctypes.c_int, ctypes.c_int]
_PyLong_FromUnicodeObject.restype = ctypes.py_object

_PyFloat_FromString = ctypes.pythonapi.PyFloat_FromString
_PyFloat_FromString.argtypes = [ctypes.py_object]
_PyFloat_FromString.restype = ctypes.py_object

_PyType_Modified = ctypes.pythonapi.PyType_Modified
_PyType_Modified.argtypes = [ctypes.py_object]
_PyType_Modified.restype = None

_PyErr_Clear = ctypes.pythonapi.PyErr_Clear

# Global reference anchor to prevent C-struct GC deallocation
_gc_protection = []


# --- High-Performance Vectorized Buffer Helpers ---

def _str_to_codes(s):
    if _HAS_NUMPY:
        return np.frombuffer(s.encode('utf-32-le'), dtype=np.uint32).astype(np.int64)
    return array.array('I', s.encode('utf-32-le'))


def _codes_to_str(codes):
    if _HAS_NUMPY and isinstance(codes, np.ndarray):
        bounded = (codes % 1114112).astype(np.uint32)
        return bounded.tobytes().decode('utf-32-le')
    elif isinstance(codes, array.array):
        bounded = array.array('I', (int(x) % 1114112 for x in codes))
        return bounded.tobytes().decode('utf-32-le')
    else:
        arr = array.array('I', (int(x) % 1114112 for x in codes))
        return arr.tobytes().decode('utf-32-le')


# --- Metaclasses for Universal Type Compatibility ---

class _PatchedIntMeta(type):
    def __instancecheck__(cls, instance):
        return isinstance(instance, _ORIG_INT_TYPE)

    def __subclasscheck__(cls, subclass):
        return issubclass(subclass, _ORIG_INT_TYPE)


class _PatchedFloatMeta(type):
    def __instancecheck__(cls, instance):
        return isinstance(instance, _ORIG_FLOAT_TYPE)

    def __subclasscheck__(cls, subclass):
        return issubclass(subclass, _ORIG_FLOAT_TYPE)


# --- Subclassed Numeric Types with Direct C-API Casting ---

class _PatchedInt(_ORIG_INT_TYPE, metaclass=_PatchedIntMeta):
    def __new__(cls, val=0, *args, **kwargs):
        if isinstance(val, str):
            try:
                base = kwargs.get("base", 10)
                res = _PyLong_FromUnicodeObject(val, 0, base)
                if res is not None:
                    return res
            except Exception:
                pass
            _PyErr_Clear()
            return _ORIG_INT_TYPE.__new__(cls, sum(ord(c) for c in val))
        return _ORIG_INT_TYPE.__new__(cls, val, *args, **kwargs)


class _PatchedFloat(_ORIG_FLOAT_TYPE, metaclass=_PatchedFloatMeta):
    def __new__(cls, val=0.0):
        if isinstance(val, str):
            try:
                res = _PyFloat_FromString(val)
                if res is not None:
                    return res
            except Exception:
                pass
            _PyErr_Clear()
            return _ORIG_FLOAT_TYPE.__new__(cls, float(sum(ord(c) for c in val)))
        return _ORIG_FLOAT_TYPE.__new__(cls, val)


# --- Universal Recursive Weight Evaluation Helper ---

def _get_weight(obj):
    if obj is None:
        return 0.0
    if isinstance(obj, str):
        if isinstance(obj, MathChar):
            return string_len(obj)
        return float(sum(ord(c) for c in obj))
    elif isinstance(obj, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE, bool)):
        return float(obj)
    elif isinstance(obj, complex):
        return abs(obj)
    elif isinstance(obj, (bytes, bytearray, memoryview)):
        return float(sum(obj))
    elif hasattr(obj, "items"):
        try:
            return float(sum(_get_weight(k) + _get_weight(v) for k, v in obj.items()))
        except Exception:
            pass
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        try:
            return float(sum(_get_weight(item) for item in obj))
        except Exception:
            pass
    try:
        return float(len(obj))
    except Exception:
        pass
    try:
        return float(sum(ord(c) for c in str(obj)))
    except Exception:
        return 0.0


# --- Custom String Elements for Advanced Iteration & Indexing ---

class MathChar(str):
    """
    A single-character string wrapper that retains all custom mathematical properties 
    when extracting or iterating over string elements.
    """
    pass


class StringMathIterator:
    """
    Custom iterator to yield MathChar instances instead of standard primitive strings.
    """
    def __init__(self, text):
        self.text = str(text)
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < _PyUnicode_GetLength(self.text):
            char = self.text[self.index]
            self.index += 1
            return MathChar(char)
        raise StopIteration


# --- Custom JSON Serialization Support ---

class MathJSONEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder to ensure MathChar objects and heavily mutated strings 
    serialize safely into standard JSON representations without metadata corruption.
    """
    def default(self, obj):
        if isinstance(obj, MathChar):
            return str(obj)
        return super().default(obj)


# --- Core Mathematical Operators (Vectorized) ---

def string_add(self, other):
    if isinstance(other, str):
        return _ORIGINAL_STR_ADD(self, other)
    elif isinstance(other, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE, bool)):
        codes = _str_to_codes(self)
        shift = int(other)
        return _codes_to_str(codes + shift)
    return string_add(self, _get_weight(other))


def string_radd(self, other):
    return string_add(self, other)


def string_pow(self, power, modulo=None):
    if not isinstance(power, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE)):
        power = _get_weight(power)
    codes = _str_to_codes(self)
    return _codes_to_str([int(int(x) ** power) for x in codes])


def string_rpow(self, base):
    if not isinstance(base, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE)):
        base = _get_weight(base)
    codes = _str_to_codes(self)
    return _codes_to_str([int(base ** int(x)) for x in codes])


def string_mul(self, other):
    if isinstance(other, _ORIG_INT_TYPE):
        return _ORIGINAL_STR_MUL(self, other)
    elif isinstance(other, _ORIG_FLOAT_TYPE):
        codes = _str_to_codes(self)
        return _codes_to_str([int(x * other) for x in codes])
    elif isinstance(other, str):
        raw_self_len = _PyUnicode_GetLength(self)
        raw_other_len = _PyUnicode_GetLength(other)
        max_len = max(raw_self_len, raw_other_len)
        s1 = self.ljust(max_len, '\x00')
        s2 = other.ljust(max_len, '\x00')
        c1 = _str_to_codes(s1)
        c2 = _str_to_codes(s2)
        return _codes_to_str(c1 * c2)
    return string_mul(self, _get_weight(other))


def string_rmul(self, other):
    return string_mul(self, other)


def string_truediv(self, divisor):
    if not isinstance(divisor, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE)):
        divisor = _get_weight(divisor)
    if divisor == 0:
        raise ZeroDivisionError("string division by zero")
    codes = _str_to_codes(self)
    return _codes_to_str([int(x / divisor) for x in codes])


def string_rtruediv(self, dividend):
    if not isinstance(dividend, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE)):
        dividend = _get_weight(dividend)
    codes = _str_to_codes(self)
    res = []
    for x in codes:
        if x == 0:
            raise ZeroDivisionError("division by zero character code")
        res.append(int(dividend / x))
    return _codes_to_str(res)


def string_floordiv(self, divisor):
    if not isinstance(divisor, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE)):
        divisor = int(_get_weight(divisor))
    if divisor == 0:
        raise ZeroDivisionError("string integer division by zero")
    codes = _str_to_codes(self)
    return _codes_to_str([x // int(divisor) for x in codes])


def string_rfloordiv(self, dividend):
    if not isinstance(dividend, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE)):
        dividend = int(_get_weight(dividend))
    codes = _str_to_codes(self)
    res = []
    for x in codes:
        if x == 0:
            raise ZeroDivisionError("integer division by zero character code")
        res.append(int(dividend) // x)
    return _codes_to_str(res)


def string_sub(self, other):
    if isinstance(other, str):
        result = self
        for char in other:
            result = result.replace(char, "")
        return result
    elif isinstance(other, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE)):
        codes = _str_to_codes(self)
        shift = int(other)
        return _codes_to_str(codes - shift)
    return string_sub(self, _get_weight(other))


def string_rsub(self, other):
    if isinstance(other, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE)):
        val = int(other)
        codes = _str_to_codes(self)
        return _codes_to_str([val - x for x in codes])
    return string_rsub(self, _get_weight(other))


def string_mod(self, other):
    if isinstance(other, (tuple, dict)) or "%s" in self or "%d" in self or "%f" in self:
        return _PyUnicode_Format(self, other)
        
    if not isinstance(other, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE)):
        other = _get_weight(other)
        
    if other == 0:
        raise ZeroDivisionError("string modulo by zero")
        
    codes = _str_to_codes(self)
    return _codes_to_str([int(x % other) for x in codes])


def string_rmod(self, other):
    if not isinstance(other, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE)):
        other = _get_weight(other)
    codes = _str_to_codes(self)
    res = []
    for x in codes:
        if x == 0:
            raise ZeroDivisionError("modulo by zero character code")
        res.append(int(other % x))
    return _codes_to_str(res)


def string_divmod(self, other):
    return (string_floordiv(self, other), string_mod(self, other))


def string_rdivmod(self, other):
    return (string_rfloordiv(self, other), string_rmod(self, other))


# --- Matrix Multiplication (@) ---

def string_matmul(self, other):
    if isinstance(other, (_ORIG_INT_TYPE, _ORIG_FLOAT_TYPE)):
        return sum(ord(c) * other for c in self)
    if isinstance(other, (list, tuple)):
        return sum(ord(c) * _get_weight(elem) for c, elem in zip(self, other))
    if not isinstance(other, str):
        return sum(ord(c) * _get_weight(other) for c in self)
    
    raw_self_len = _PyUnicode_GetLength(self)
    raw_other_len = _PyUnicode_GetLength(other)
    
    max_len = max(raw_self_len, raw_other_len)
    s1 = self.ljust(max_len, '\x00')
    s2 = other.ljust(max_len, '\x00')
    c1 = _str_to_codes(s1)
    c2 = _str_to_codes(s2)
    return int(sum(c1 * c2))


def string_rmatmul(self, other):
    return string_matmul(self, other)


# --- Custom Advanced Length & Indexing Hooks ---

def string_len(self):
    if isinstance(self, MathChar):
        total_weight = 0
        raw_len = _PyUnicode_GetLength(self)
        for i in range(raw_len):
            total_weight += ord(self[i])
        return total_weight
    return _PyUnicode_GetLength(self)


def string_getitem(self, index):
    res = _ORIGINAL_STR_GETITEM(self, index)
    if isinstance(res, str) and _PyUnicode_GetLength(res) == 1 and not isinstance(index, slice):
        return MathChar(res)
    return res


# --- Unary Operators & Mathematical Casting ---

def string_neg(self):
    return self[::-1]


def string_invert(self):
    codes = _str_to_codes(self)
    return _codes_to_str([~x for x in codes])


def string_abs(self):
    codes = _str_to_codes(self)
    square_sum = sum(int(x) ** 2 for x in codes)
    return math.sqrt(square_sum)


def string_int(self, base=10):
    return _PatchedInt(self)


def string_float(self):
    return _PatchedFloat(self)


def string_round(self, ndigits=None):
    return round(string_float(self), ndigits)


# --- Bitwise Operators (<<, >>, &, |, ^) ---

def string_lshift(self, shift):
    if not isinstance(shift, _ORIG_INT_TYPE):
        shift = int(_get_weight(shift))
    codes = _str_to_codes(self)
    return _codes_to_str(codes << shift)


def string_rlshift(self, other):
    val = int(_get_weight(other))
    codes = _str_to_codes(self)
    return _codes_to_str([val << int(x) for x in codes])


def string_rshift(self, shift):
    if not isinstance(shift, _ORIG_INT_TYPE):
        shift = int(_get_weight(shift))
    codes = _str_to_codes(self)
    return _codes_to_str(codes >> shift)


def string_rrshift(self, other):
    val = int(_get_weight(other))
    codes = _str_to_codes(self)
    return _codes_to_str([val >> int(x) for x in codes])


def _bitwise_base(self, other, op_func, op_symbol):
    raw_self_len = _PyUnicode_GetLength(self)
    if isinstance(other, str):
        raw_other_len = _PyUnicode_GetLength(other)
        max_len = max(raw_self_len, raw_other_len)
        s1 = self.ljust(max_len, '\x00')
        s2 = other.ljust(max_len, '\x00')
        c1 = _str_to_codes(s1)
        c2 = _str_to_codes(s2)
        return _codes_to_str(op_func(c1, c2))
    else:
        val = int(_get_weight(other))
        codes = _str_to_codes(self)
        return _codes_to_str(op_func(codes, val))


def string_and(self, other): return _bitwise_base(self, other, lambda x, y: x & y, '&')
def string_rand(self, other): return _bitwise_base(self, other, lambda x, y: y & x, '&')

def string_or(self, other):  return _bitwise_base(self, other, lambda x, y: x | y, '|')
def string_ror(self, other):  return _bitwise_base(self, other, lambda x, y: y | x, '|')

def string_xor(self, other): return _bitwise_base(self, other, lambda x, y: x ^ y, '^')
def string_rxor(self, other): return _bitwise_base(self, other, lambda x, y: y ^ x, '^')


# --- Logical Comparison Operators & Iteration ---

def _compare_strings(self, other, op):
    return op(_get_weight(self), _get_weight(other))


def string_gt(self, other): return _compare_strings(self, other, lambda x, y: x > y)
def string_lt(self, other): return _compare_strings(self, other, lambda x, y: x < y)
def string_ge(self, other): return _compare_strings(self, other, lambda x, y: x >= y)
def string_le(self, other): return _compare_strings(self, other, lambda x, y: x <= y)


def string_eq(self, other):
    if isinstance(other, str):
        return _ORIGINAL_STR_EQ(self, other)
    return _get_weight(self) == _get_weight(other)


def string_ne(self, other):
    return not string_eq(self, other)


def string_iter(self):
    return StringMathIterator(self)


def string_reversed(self):
    return StringMathIterator(self[::-1])


# --- Advanced CPython Type Flag Hack and Slot Overwriter ---

def patch_strings():
    """
    Modifies C-level slots for native 'str' and 'MathChar' classes.
    """
    class PyTypeObject(ctypes.Structure):
        pass

    PyTypeObject._fields_ = [
        ("ob_refcnt", ctypes.c_ssize_t),
        ("ob_type", ctypes.c_void_p),
        ("ob_size", ctypes.c_ssize_t),
        ("tp_name", ctypes.c_char_p),
        ("tp_basicsize", ctypes.c_ssize_t),
        ("tp_itemsize", ctypes.c_ssize_t),
        ("tp_dealloc", ctypes.c_void_p),
        ("tp_vectorcall_offset", ctypes.c_ssize_t),
        ("tp_getattr", ctypes.c_void_p),
        ("tp_setattr", ctypes.c_void_p),
        ("tp_as_async", ctypes.c_void_p),
        ("tp_repr", ctypes.c_void_p),
        ("tp_as_number", ctypes.c_void_p),
        ("tp_as_sequence", ctypes.c_void_p),
        ("tp_as_mapping", ctypes.c_void_p),
        ("tp_hash", ctypes.c_void_p),
        ("tp_call", ctypes.c_void_p),
        ("tp_str", ctypes.c_void_p),
        ("tp_getattro", ctypes.c_void_p),
        ("tp_setattro", ctypes.c_void_p),
        ("tp_as_buffer", ctypes.c_void_p),
        ("tp_flags", ctypes.c_ulong),
        ("tp_doc", ctypes.c_char_p),
        ("tp_traverse", ctypes.c_void_p),
        ("tp_clear", ctypes.c_void_p),
        ("tp_richcompare", ctypes.c_void_p),
        ("tp_weaklistoffset", ctypes.c_ssize_t),
        ("tp_iter", ctypes.c_void_p),
        ("tp_iternext", ctypes.c_void_p),
    ]

    str_struct = PyTypeObject.from_address(id(str))
    mathchar_struct = PyTypeObject.from_address(id(MathChar))

    referents = gc.get_referents(str.__dict__)
    target_dict = next(obj for obj in referents if type(obj) is dict)

    methods = {
        "__add__": string_add, "__radd__": string_radd,
        "__sub__": string_sub, "__rsub__": string_rsub,
        "__mul__": string_mul, "__rmul__": string_rmul,
        "__truediv__": string_truediv, "__rtruediv__": string_rtruediv,
        "__floordiv__": string_floordiv, "__rfloordiv__": string_rfloordiv,
        "__mod__": string_mod, "__rmod__": string_rmod,
        "__divmod__": string_divmod, "__rdivmod__": string_rdivmod,
        "__pow__": string_pow, "__rpow__": string_rpow,
        "__matmul__": string_matmul, "__rmatmul__": string_rmatmul,
        "__len__": string_len, "__getitem__": string_getitem,
        "__neg__": string_neg, "__invert__": string_invert,
        "__abs__": string_abs, "__int__": string_int, "__float__": string_float,
        "__round__": string_round,
        "__lshift__": string_lshift, "__rlshift__": string_rlshift,
        "__rshift__": string_rshift, "__rrshift__": string_rrshift,
        "__and__": string_and, "__rand__": string_rand,
        "__or__": string_or, "__ror__": string_ror,
        "__xor__": string_xor, "__rxor__": string_rxor,
        "__gt__": string_gt, "__lt__": string_lt, "__ge__": string_ge, "__le__": string_le,
        "__eq__": string_eq, "__ne__": string_ne,
        "__iter__": string_iter, "__reversed__": string_reversed
    }

    orig_flags = str_struct.tp_flags
    str_struct.tp_flags = (orig_flags & ~0x00001000) | 0x00000200

    try:
        for name, func in methods.items():
            target_dict[name] = func
    finally:
        str_struct.tp_flags = orig_flags

    class PatchBridge(str):
        pass

    for name, func in methods.items():
        setattr(PatchBridge, name, func)

    bridge_struct = PyTypeObject.from_address(id(PatchBridge))

    # Protect PatchBridge and bridge_struct from CPython Garbage Collection
    _gc_protection.append(PatchBridge)
    _gc_protection.append(bridge_struct)

    # Assign C-slots for str struct
    str_struct.tp_as_number = bridge_struct.tp_as_number
    str_struct.tp_as_sequence = bridge_struct.tp_as_sequence
    str_struct.tp_as_mapping = bridge_struct.tp_as_mapping
    str_struct.tp_richcompare = bridge_struct.tp_richcompare
    str_struct.tp_iter = bridge_struct.tp_iter

    # Assign C-slots for MathChar struct as well
    mathchar_struct.tp_as_number = bridge_struct.tp_as_number
    mathchar_struct.tp_as_sequence = bridge_struct.tp_as_sequence
    mathchar_struct.tp_as_mapping = bridge_struct.tp_as_mapping
    mathchar_struct.tp_richcompare = bridge_struct.tp_richcompare
    mathchar_struct.tp_iter = bridge_struct.tp_iter

    # Transparently patch builtins.int and builtins.float with metaclass-enabled type subclasses
    if not getattr(builtins, "_pymastring_patched", False):
        builtins.int = _PatchedInt
        builtins.float = _PatchedFloat
        builtins._pymastring_patched = True

    for method in ALL_METHODS:
        func_name = f"string_{method}"
        if func_name in globals():
            setattr(MathChar, f"__{method}__", globals()[func_name])

    _PyType_Modified(MathChar)
    _PyType_Modified(str)

for method in ALL_METHODS:
    func_name = f"string_{method}"
    if func_name in globals():
        setattr(MathChar, f"__{method}__", globals()[func_name])
