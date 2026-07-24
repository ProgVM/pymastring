import ctypes
import gc
import json
import math

# Save original builtin string descriptors BEFORE patch_strings runs
_ORIGINAL_STR_ADD = str.__dict__["__add__"]
_ORIGINAL_STR_MUL = str.__dict__["__mul__"]
_ORIGINAL_STR_GETITEM = str.__dict__["__getitem__"]

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

_PyErr_Clear = ctypes.pythonapi.PyErr_Clear

# Global reference anchor to prevent C-struct GC deallocation
_gc_protection = []


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


# --- Core Mathematical Operators ---

def string_add(self, other):
    if isinstance(other, str):
        return _ORIGINAL_STR_ADD(self, other)
    elif isinstance(other, (int, float)):
        result_chars = []
        for char in self:
            final_code = int(ord(char) + int(other)) % 1114112
            result_chars.append(chr(final_code))
        return "".join(result_chars)
    return NotImplemented


def string_radd(self, other):
    if isinstance(other, (int, float)):
        return string_add(self, other)
    return NotImplemented


def string_pow(self, power, modulo=None):
    if not isinstance(power, (int, float)):
        raise TypeError(f"unsupported operand type(s) for ** or pow(): '{type(self).__name__}' and '{type(power).__name__}'")
    result_chars = []
    for char in self:
        final_code = int(ord(char) ** power) % 1114112
        result_chars.append(chr(final_code))
    return "".join(result_chars)


def string_mul(self, other):
    if isinstance(other, int):
        return _ORIGINAL_STR_MUL(self, other)
    elif isinstance(other, float):
        result_chars = []
        for char in self:
            final_code = int(ord(char) * other) % 1114112
            result_chars.append(chr(final_code))
        return "".join(result_chars)
    elif isinstance(other, str):
        raw_self_len = _PyUnicode_GetLength(self)
        raw_other_len = _PyUnicode_GetLength(other)
        max_len = max(raw_self_len, raw_other_len)
        s1 = self.ljust(max_len, '\x00')
        s2 = other.ljust(max_len, '\x00')
        result_chars = []
        for c1, c2 in zip(s1, s2):
            final_code = (ord(c1) * ord(c2)) % 1114112
            result_chars.append(chr(final_code))
        return "".join(result_chars)
    return NotImplemented


def string_truediv(self, divisor):
    if not isinstance(divisor, (int, float)):
        raise TypeError(f"unsupported operand type(s) for /: '{type(self).__name__}' and '{type(divisor).__name__}'")
    if divisor == 0:
        raise ZeroDivisionError("string division by zero")
    result_chars = []
    for char in self:
        final_code = int(ord(char) / divisor) % 1114112
        result_chars.append(chr(final_code))
    return "".join(result_chars)


def string_floordiv(self, divisor):
    if not isinstance(divisor, int):
        raise TypeError(f"unsupported operand type(s) for //: '{type(self).__name__}' and '{type(divisor).__name__}'")
    if divisor == 0:
        raise ZeroDivisionError("string integer division by zero")
    result_chars = []
    for char in self:
        final_code = (ord(char) // divisor) % 1114112
        result_chars.append(chr(final_code))
    return "".join(result_chars)


def string_sub(self, other):
    if isinstance(other, str):
        result = self
        for char in other:
            result = result.replace(char, "")
        return result
    elif isinstance(other, (int, float)):
        result_chars = []
        for char in self:
            final_code = int(ord(char) - int(other)) % 1114112
            result_chars.append(chr(final_code))
        return "".join(result_chars)
    raise TypeError(f"unsupported operand type(s) for -: '{type(self).__name__}' and '{type(other).__name__}'")


def string_rsub(self, other):
    if isinstance(other, (int, float)):
        result_chars = []
        for char in self:
            final_code = int(int(other) - ord(char)) % 1114112
            result_chars.append(chr(final_code))
        return "".join(result_chars)
    return NotImplemented


def string_mod(self, other):
    if isinstance(other, (tuple, dict)) or "%s" in self or "%d" in self or "%f" in self:
        return _PyUnicode_Format(self, other)
        
    if not isinstance(other, (int, float)):
        raise TypeError(f"unsupported operand type(s) for %: '{type(self).__name__}' and '{type(other).__name__}'")
        
    if other == 0:
        raise ZeroDivisionError("string modulo by zero")
        
    result_chars = []
    for char in self:
        final_code = int(ord(char) % other) % 1114112
        result_chars.append(chr(final_code))
    return "".join(result_chars)


def string_divmod(self, other):
    return (string_floordiv(self, other), string_mod(self, other))


def string_rdivmod(self, other):
    return (string_rsub(self, other), string_mod(self, other))


# --- Matrix Multiplication (@) ---

def string_matmul(self, other):
    if not isinstance(other, str):
        raise TypeError(f"unsupported operand type(s) for @: '{type(self).__name__}' and '{type(other).__name__}'")
    
    raw_self_len = _PyUnicode_GetLength(self)
    raw_other_len = _PyUnicode_GetLength(other)
    
    max_len = max(raw_self_len, raw_other_len)
    s1 = self.ljust(max_len, '\x00')
    s2 = other.ljust(max_len, '\x00')
    return sum(ord(c1) * ord(c2) for c1, c2 in zip(s1, s2))


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
    result_chars = []
    for char in self:
        final_code = (~ord(char)) % 1114112
        result_chars.append(chr(final_code))
    return "".join(result_chars)


def string_abs(self):
    square_sum = sum(ord(char) ** 2 for char in self)
    return math.sqrt(square_sum)


def string_int(self, base=10):
    try:
        res = _PyLong_FromUnicodeObject(self, 0, base)
        if res is not None:
            return res
    except Exception:
        pass
    _PyErr_Clear()
    return sum(ord(char) for char in self)


def string_float(self):
    try:
        res = _PyFloat_FromString(self)
        if res is not None:
            return res
    except Exception:
        pass
    _PyErr_Clear()
    return float(sum(ord(char) for char in self))


def string_round(self, ndigits=None):
    return round(string_float(self), ndigits)


# --- Bitwise Operators (<<, >>, &, |, ^) ---

def string_lshift(self, shift):
    if not isinstance(shift, int):
        raise TypeError(f"unsupported operand type(s) for <<: '{type(self).__name__}' and '{type(shift).__name__}'")
    result_chars = []
    for char in self:
        final_code = (ord(char) << shift) % 1114112
        result_chars.append(chr(final_code))
    return "".join(result_chars)


def string_rshift(self, shift):
    if not isinstance(shift, int):
        raise TypeError(f"unsupported operand type(s) for >>: '{type(self).__name__}' and '{type(shift).__name__}'")
    result_chars = []
    for char in self:
        final_code = (ord(char) >> shift) % 1114112
        result_chars.append(chr(final_code))
    return "".join(result_chars)


def _bitwise_base(self, other, op_func, op_symbol):
    raw_self_len = _PyUnicode_GetLength(self)
    if isinstance(other, int):
        result_chars = []
        for char in self:
            final_code = op_func(ord(char), other) % 1114112
            result_chars.append(chr(final_code))
        return "".join(result_chars)
    elif isinstance(other, str):
        raw_other_len = _PyUnicode_GetLength(other)
        max_len = max(raw_self_len, raw_other_len)
        s1 = self.ljust(max_len, '\x00')
        s2 = other.ljust(max_len, '\x00')
        result_chars = []
        for c1, c2 in zip(s1, s2):
            final_code = op_func(ord(c1), ord(c2)) % 1114112
            result_chars.append(chr(final_code))
        return "".join(result_chars)
    raise TypeError(f"unsupported operand type(s) for {op_symbol}: '{type(self).__name__}' and '{type(other).__name__}'")


def string_and(self, other): return _bitwise_base(self, other, lambda x, y: x & y, '&')
def string_or(self, other):  return _bitwise_base(self, other, lambda x, y: x | y, '|')
def string_xor(self, other): return _bitwise_base(self, other, lambda x, y: x ^ y, '^')


# --- Logical Comparison Operators & Iteration ---

def _compare_strings(self, other, op):
    if not isinstance(other, str):
        raise TypeError(f"not supported between instances of '{type(self).__name__}' and '{type(other).__name__}'")
    return op(string_len(self), string_len(other))


def string_gt(self, other): return _compare_strings(self, other, lambda x, y: x > y)
def string_lt(self, other): return _compare_strings(self, other, lambda x, y: x < y)
def string_ge(self, other): return _compare_strings(self, other, lambda x, y: x >= y)
def string_le(self, other): return _compare_strings(self, other, lambda x, y: x <= y)


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
    
    referents = gc.get_referents(str.__dict__)
    target_dict = next(obj for obj in referents if type(obj) is dict)

    methods = {
        "__add__": string_add, "__radd__": string_radd,
        "__sub__": string_sub, "__rsub__": string_rsub,
        "__mul__": string_mul, "__rmul__": string_mul,
        "__truediv__": string_truediv, "__floordiv__": string_floordiv,
        "__mod__": string_mod, "__divmod__": string_divmod, "__rdivmod__": string_rdivmod,
        "__pow__": string_pow, "__matmul__": string_matmul, "__len__": string_len,
        "__getitem__": string_getitem, "__neg__": string_neg, "__invert__": string_invert,
        "__abs__": string_abs, "__int__": string_int, "__float__": string_float,
        "__round__": string_round, "__lshift__": string_lshift, "__rshift__": string_rshift,
        "__and__": string_and, "__or__": string_or, "__xor__": string_xor,
        "__gt__": string_gt, "__lt__": string_lt, "__ge__": string_ge, "__le__": string_le,
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

    str_struct.tp_as_number = bridge_struct.tp_as_number
    str_struct.tp_as_sequence = bridge_struct.tp_as_sequence
    str_struct.tp_as_mapping = bridge_struct.tp_as_mapping
    str_struct.tp_richcompare = bridge_struct.tp_richcompare
    str_struct.tp_iter = bridge_struct.tp_iter

    all_methods = [
        "add", "radd", "sub", "rsub", "mul", "rmul", "truediv", "floordiv",
        "mod", "divmod", "rdivmod", "pow", "matmul", "len", "getitem",
        "neg", "invert", "abs", "int", "float", "round",
        "lshift", "rshift", "and", "or", "xor", "gt", "lt", "ge", "le",
        "iter", "reversed"
    ]
    for method in all_methods:
        func_name = f"string_{method}"
        if func_name in globals():
            setattr(MathChar, f"__{method}__", globals()[func_name])

    ctypes.pythonapi.PyType_Modified(ctypes.py_object(MathChar))
    ctypes.pythonapi.PyType_Modified(ctypes.py_object(str))


all_methods = [
    "add", "radd", "sub", "rsub", "mul", "rmul", "truediv", "floordiv",
    "mod", "divmod", "rdivmod", "pow", "matmul", "len", "getitem",
    "neg", "invert", "abs", "int", "float", "round",
    "lshift", "rshift", "and", "or", "xor", "gt", "lt", "ge", "le",
    "iter", "reversed"
]
for method in all_methods:
    func_name = f"string_{method}"
    if func_name in globals():
        setattr(MathChar, f"__{method}__", globals()[func_name])
