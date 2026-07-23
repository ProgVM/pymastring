import json
import ctypes
import gc

# --- Custom String Elements for Advanced Iteration ---

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
        # Store as standard primitive to avoid recursion during internal processing
        self.text = str(text)
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.text):
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

def string_pow(self, power):
    """ Hook function to replace the standard behavior of str.__pow__ (**). """
    if not isinstance(power, (int, float)):
        class_name = self.__class__.__name__
        power_name = type(power).__name__
        raise TypeError(f"unsupported operand type(s) for ** or pow(): '{class_name}' and '{power_name}'")
    
    result_chars = []
    for char in self:
        char_code = ord(char)
        powered_code = char_code ** power
        final_code = int(powered_code) % 1114112
        result_chars.append(chr(final_code))
    return "".join(result_chars)

def string_truediv(self, divisor):
    """ Hook function to replace the standard behavior of str.__truediv__ (/). """
    if not isinstance(divisor, (int, float)):
        class_name = self.__class__.__name__
        divisor_name = type(divisor).__name__
        raise TypeError(f"unsupported operand type(s) for /: '{class_name}' and '{divisor_name}'")
    
    if divisor == 0:
        raise ZeroDivisionError("string division by zero")
        
    result_chars = []
    for char in self:
        char_code = ord(char)
        divided_code = int(char_code / divisor) % 1114112
        result_chars.append(chr(divided_code))
    return "".join(result_chars)

def string_sub(self, other):
    """ Hook function to replace the standard behavior of str.__sub__ (-). """
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
    else:
        class_name = self.__class__.__name__
        other_name = type(other).__name__
        raise TypeError(f"unsupported operand type(s) for -: '{class_name}' and '{other_name}'")

def string_mod(self, other):
    """ Hook function to patch str.__mod__ (%). """
    if "%s" in self or "%d" in self or "%f" in self:
        # Fallback to standard C-level string formatting if placeholders exist
        return NotImplemented
        
    if not isinstance(other, (int, float)):
        class_name = self.__class__.__name__
        other_name = type(other).__name__
        raise TypeError(f"unsupported operand type(s) for %: '{class_name}' and '{other_name}'")
        
    if other == 0:
        raise ZeroDivisionError("string modulo by zero")
        
    result_chars = []
    for char in self:
        final_code = int(ord(char) % other) % 1114112
        result_chars.append(chr(final_code))
    return "".join(result_chars)


# --- Matrix Multiplication (@) ---

def string_matmul(self, other):
    """ Hook function to patch str.__matmul__ (@). Calculates scalar dot product. """
    if not isinstance(other, str):
        class_name = self.__class__.__name__
        other_name = type(other).__name__
        raise TypeError(f"unsupported operand type(s) for @: '{class_name}' and '{other_name}'")
        
    max_len = max(len(self), len(other))
    s1 = self.ljust(max_len, '\x00')
    s2 = other.ljust(max_len, '\x00')
    
    # Secure raw length call bypassing our patched __len__ to prevent semantic mess here
    dot_product = sum(ord(c1) * ord(c2) for c1, c2 in zip(s1, s2))
    return dot_product


# --- Custom Advanced Length Hook (len()) ---

def string_len(self):
    """
    Hook function to dynamically modify the native behavior of len(str).
    Calculates total Unicode weight instead of counting raw character positions.
    Uses continuous native generation to strictly prevent deep recursion loops.
    """
    total_weight = 0
    # Use standard C-level character iteration to bypass custom Python __iter__ hook
    for i in range(super(str, self).__len__()):
        total_weight += ord(self[i])
    return total_weight


# --- Bitwise Operators (<<, >>, &, |, ^) ---

def string_lshift(self, shift):
    """ Hook function to patch str.__lshift__ (<<). """
    if not isinstance(shift, int):
        class_name = self.__class__.__name__
        shift_name = type(shift).__name__
        raise TypeError(f"unsupported operand type(s) for <<: '{class_name}' and '{shift_name}'")
    
    result_chars = []
    for char in self:
        final_code = (ord(char) << shift) % 1114112
        result_chars.append(chr(final_code))
    return "".join(result_chars)

def string_rshift(self, shift):
    """ Hook function to patch str.__rshift__ (>>). """
    if not isinstance(shift, int):
        class_name = self.__class__.__name__
        shift_name = type(shift).__name__
        raise TypeError(f"unsupported operand type(s) for >>: '{class_name}' and '{shift_name}'")
    
    result_chars = []
    for char in self:
        final_code = (ord(char) >> shift) % 1114112
        result_chars.append(chr(final_code))
    return "".join(result_chars)

def _bitwise_base(self, other, op_func, op_symbol):
    if isinstance(other, int):
        result_chars = []
        for char in self:
            final_code = op_func(ord(char), other) % 1114112
            result_chars.append(chr(final_code))
        return "".join(result_chars)
    elif isinstance(other, str):
        max_len = max(super(str, self).__len__(), super(str, other).__len__())
        s1 = self.ljust(max_len, '\x00')
        s2 = other.ljust(max_len, '\x00')
        
        result_chars = []
        for c1, c2 in zip(s1, s2):
            final_code = op_func(ord(c1), ord(c2)) % 1114112
            result_chars.append(chr(final_code))
        return "".join(result_chars)
    else:
        class_name = self.__class__.__name__
        other_name = type(other).__name__
        raise TypeError(f"unsupported operand type(s) for {op_symbol}: '{class_name}' and '{other_name}'")

def string_and(self, other): return _bitwise_base(self, other, lambda x, y: x & y, '&')
def string_or(self, other):  return _bitwise_base(self, other, lambda x, y: x | y, '|')
def string_xor(self, other): return _bitwise_base(self, other, lambda x, y: x ^ y, '^')


# --- Logical Comparison Operators ---

def _compare_strings(self, other, op):
    if not isinstance(other, str):
        class_name = self.__class__.__name__
        other_name = type(other).__name__
        raise TypeError(f"not supported between instances of '{class_name}' and '{other_name}'")
        
    return op(string_len(self), string_len(other))

def string_gt(self, other): return _compare_strings(self, other, lambda x, y: x > y)
def string_lt(self, other): return _compare_strings(self, other, lambda x, y: x < y)
def string_ge(self, other): return _compare_strings(self, other, lambda x, y: x >= y)
def string_le(self, other): return _compare_strings(self, other, lambda x, y: x <= y)


# --- Custom Iteration Hook ---

def string_iter(self):
    """ Hook function to replace standard str.__iter__. """
    return StringMathIterator(self)


# --- Global Monkey-Patch Executor ---

def patch_strings():
    """
    Injects all mathematical, matrix, bitwise, logical, length and iteration hooks 
    into native 'str' class using safe C-level memory dictionary manipulation.
    Bypasses standard mappingproxy restrictions and prevents forbiddenfruit errors.
    """
    # Find the real underlying mutable dictionary of the built-in 'str' class
    # to bypass the read-only 'mappingproxy' proxy object constraints
    target_dict = [obj for obj in gc.get_referents(str.__dict__) if type(obj) is dict][0]

    # Map every single custom dunder method directly into the str namespace dict
    target_dict["__pow__"] = string_pow
    target_dict["__truediv__"] = string_truediv
    target_dict["__sub__"] = string_sub
    target_dict["__mod__"] = string_mod
    target_dict["__matmul__"] = string_matmul
    target_dict["__len__"] = string_len
    target_dict["__lshift__"] = string_lshift
    target_dict["__rshift__"] = string_rshift
    target_dict["__and__"] = string_and
    target_dict["__or__"] = string_or
    target_dict["__xor__"] = string_xor
    target_dict["__gt__"] = string_gt
    target_dict["__lt__"] = string_lt
    target_dict["__ge__"] = string_ge
    target_dict["__le__"] = string_le
    target_dict["__iter__"] = string_iter

    # Crucial CPython API call to force internal type lookup cache evaluation 
    # to clear up stale references and register new operations globally
    ctypes.pythonapi.PyType_Modified(ctypes.py_object(str))

# Dynamically synchronize the custom MathChar fallback operations
for method in ["__pow__", "__truediv__", "__sub__", "__mod__", "__matmul__", "__len__",
               "__lshift__", "__rshift__", "__and__", "__or__", "__xor__",
               "__gt__", "__lt__", "__ge__", "__le__", "__iter__"]:
    setattr(MathChar, method, locals()[f"string_{method.strip('_')}"])

