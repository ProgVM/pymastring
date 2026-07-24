# pymastring

`pymastring` is a high-performance utility package that globally overrides the runtime behavior of Python's built-in primitive `str` class via deep C-level monkey-patching. It breaks standard type limitations to allow direct mathematical calculations, matrix equations, bitwise interactions, universal cross-type comparisons, and custom serialization paradigms natively on raw string literals.

---

## Technical Concept

Python's built-in `str` instances are hardcoded at the C-API level to prevent arbitrary mutation. `pymastring` bypasses this defense mechanism by temporarily modifying `PyTypeObject.tp_flags` and overwriting underlying C-slots (`tp_as_number`, `tp_as_sequence`, `tp_as_mapping`, `tp_richcompare`, `tp_iter`) via `ctypes` and garbage collector referent dictionaries.

Every mathematical operation maps characters to their respective **Unicode Code Points** (via 32-bit UCS-4 memory buffers), runs numerical adjustments, applies an auto-overflow modulo bounds-check (`% 1114112`), and decodes resulting buffers back into strings.

### Performance & Memory Acceleration
`pymastring` includes a zero-dependency C-level buffer engine utilizing Python's native `array('I')` with `utf-32-le` encoding/decoding. If `numpy` is installed in the system environment, `pymastring` automatically harnesses processor SIMD vector operations for instant array computation.

`pymastring` provides total interoperability across all native Python types: numbers (`int`, `float`, `bool`), collections (`list`, `tuple`, `set`, `dict`, `bytes`), and custom third-party objects.

---

## Installation

Install `pymastring` directly from PyPI:

```bash
pip install pymastring
```

Or install the package locally from source in editable development mode:

```bash
pip install .
```

---

## Core Features & Extended API Specification

### 1. Universal Vectorized Arithmetic Engine (`+`, `-`, `*`, `/`, `//`, `%`, `**`)
Standard string literals can be manipulated mathematically with numbers, strings, booleans, collections, and sequences across left-hand and right-hand operations.

* **Addition (`+` / `radd`):** Integer/float/bool addition shifts character unicode codes forward (`"abc" + 1` -> `"bcd"`, `"abc" + True` -> `"bcd"`). Standard string concatenation (`"a" + "b"`) is retained.
* **Subtraction (`-` / `rsub`):** Subtraction by a number reduces unicode codes (`"python" - 5`). Subtraction by another string removes target substring bytes (`"abcdef" - "bd"` -> `"acef"`). Subtraction from numbers (`1000 - "a"`) computes reverse shifts.
* **Multiplication (`*` / `rmul`):** String-by-integer multiplication performs classic repetition (`"a" * 3`). String-by-float scales codes. String-by-string evaluates element-wise Hadamard multiplication.
* **Division (`/`, `//`, `%`, `divmod`):** Performs exact truediv, floordiv, and modulo on character weights. Supports right-hand division (`200 / "a"`, `200 // "a"`) and native `divmod("abc", 2)`.
* **Exponentiation (`**` / `rpow`):** Exponentiates internal character weights (`"abc" ** 2` or `2 ** "a"`).

```python
import pymastring

print("abc" + 1)            # Outputs: "bcd"
print(1 + "abc")            # Right-hand addition -> Outputs: "bcd"
print("abc" + True)         # Bool scalar shift -> Outputs: "bcd"
print("python" - 5)         # Left-shifts unicode positions
print("abcdef" - "bd")      # Drops target slices -> Outputs: "acef"
print("abc" ** 2)           # Exponentiates character codes
print(2 ** "a")             # Right-hand exponentiation
print("xyz" / 2)            # Uniform code points scaling
print(200 / "a")            # Right-hand division
print(divmod("a", 10))      # Returns tuple of (floordiv, modulo)
```

### 2. Stream Encryption & XOR Cipher Capability (`^`)
Combining element-wise bitwise operations enables single-line Vernam / Stream encryption directly on raw strings without manual loops or `zip()` iterations.

```python
import pymastring

message = "secret_payload"
key = "super_key_12345"

# Encrypt in a single line
encrypted = message ^ key
print(encrypted)            # Outputs encrypted unicode characters

# Decrypt back
decrypted = encrypted ^ key
print(decrypted)            # Outputs: "secret_payload"
```

### 3. Matrix Cross-Multiplication Vector Behavior (`@`)
Using the `@` operator evaluates the structural linear algebra dot product between two string arrays or between strings and numeric vectors (`list`, `tuple`).

```python
import pymastring

# String-by-string dot product: (ord('a') * ord('b')) -> 97 * 98
print("a" @ "b")            # Outputs integer: 9506

# String-by-vector dot product: (97*1 + 98*2 + 99*3)
print("abc" @ [1, 2, 3])    # Outputs integer: 590
```

### 4. Cross-Type Rich Comparisons (`>`, `<`, `>=`, `<=`, `==`, `!=`)
Rich comparison algorithms evaluate recursive integrated inner array vector weight sums (`_get_weight`), allowing seamless comparisons between strings, numbers, nested lists, dicts, and custom objects.

```python
import pymastring

print("aaa" > 1)            # Compares 291 > 1 -> Outputs: True
print(100 < "aaa")          # Compares 100 < 291 -> Outputs: True
print("aaa" == 291)         # Weight equality -> Outputs: True
print("abc" > [1, 2, 3])    # Compares string weight vs list weight -> Outputs: True
print("abc" > None)         # Compares string weight vs None weight -> Outputs: True
```

### 5. Dynamic Structural Weight Evaluation & Element Extraction (`len()`, `str[i]`)

The global `len()` invocation evaluates context dynamically. Standard raw string literals retain traditional element counts. However, iterated elements, indexed characters (`pymastring.MathChar("a")`), or `MathChar` objects compute and report the integrated unicode code point weight (`ord()`).

```python
import pymastring

# A primitive baseline string keeps its classic character length
print(len("abc"))           # Outputs integer: 3

# MathChar objects report true inner weight sum
char = pymastring.MathChar("a")
print(len(char))            # Outputs Unicode weight: 97

# Intercept loops pull typified MathChar wrappers
for char in "a":
    print(len(char))        # Outputs Unicode weight: 97
```

### 6. Unary Operators & Transparent Casting (`-str`, `~str`, `abs()`, `int()`, `float()`, `round()`)

* **Unary Negation (`-`):** Reverses the string (`-"abc"` -> `"cba"`).
* **Bitwise NOT (`~`):** Inverts character bit positions (`~"abc"`).
* **Vector Norm (`abs()`):** Calculates Euclidean vector magnitude ($\sqrt{\sum \text{ord}(c)^2}$).
* **Transparent Casting (`int()`, `float()`, `round()`):** Safely parses valid numeric text or falls back to total character weight sums for non-numeric strings via metaclass-enabled numeric types.

```python
import pymastring

print(-"abc")               # Reverses string -> Outputs: "cba"
print(abs("abc"))           # Calculates Euclidean vector length -> ~169.75
print(int("123"))           # Parses valid integer -> 123
print(int("abc"))           # Fallback sum of weights -> 97 + 98 + 99 = 294
print(float("123.45"))      # Parses float -> 123.45
print(float("abc"))         # Fallback sum of weights -> 294.0
```

### 7. Bitwise Vector Conversions (`<<`, `>>`, `&`, `|`, `^`)
Direct byte-level array transformations across registers supporting left-hand and right-hand operations.

```python
import pymastring

print("abc" << 2)           # Left shift bit positions
print("secret" ^ 42)        # XOR encryption mask mapping
print("hello" & "world")     # Matrix intersection overlay
print(15 & "a")             # Right-hand bitwise AND
```

### 8. Typified Generator Array Extraction & Reversal
Loops and reversed iterators parsing raw string sequences yield operational wrappers (`MathChar`) inheriting full mathematical capabilities.

```python
import pymastring

for char in reversed("xyz"):
    print(char ** 1.5)
```

### 9. Custom JSON Serialization Engine (`MathJSONEncoder`)
To prevent internal character objects from breaking standard data transfers, use our targeted serialization mapping profile.

```python
import json
import pymastring

data = {"payload": "abc" ** 2}
json_string = json.dumps(data, cls=pymastring.MathJSONEncoder)
```

---

## License

MIT License - Copyright (c) 2026 ProgVM
