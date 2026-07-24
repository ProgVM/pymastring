# pymastring

`pymastring` is an unorthodox utility package that globally overrides the runtime behavior of Python's built-in primitive `str` class via deep C-level monkey-patching. It breaks standard structural limitations to allow direct mathematical calculations, matrix equations, bitwise interactions, and custom serialization paradigms natively on raw string literals.

---

## Technical Concept

Python's built-in `str` instances are hardcoded at the C-API level to prevent arbitrary mutation. `pymastring` bypasses this defense mechanism by temporarily modifying `PyTypeObject.tp_flags` and overwriting underlying C-slots (`tp_as_number`, `tp_as_sequence`, `tp_as_mapping`, `tp_iter`) via `ctypes` and garbage collector referent dictionaries.

Every mathematical operation maps the characters of the string to their respective **Unicode Code Points** (via `ord()`), runs numerical adjustments, applies an auto-overflow modulo bounds-check (`% 1114112`), and returns the resulting value shifted back into strings (via `chr()`).

---

## Installation

Install the package locally in editable development mode or via local source directory distribution:

```bash
pip install .
```

---

## Core Features & Extended API Specification

### 1. Complete Arithmetic Suite (`+`, `-`, `*`, `/`, `//`, `%`, `**`)
Standard string literals can be manipulated mathematically with integers, floating-point elements, and other strings.

* **Addition (`+` / `radd`):** Integer/float addition shifts character unicode codes forward (`"abc" + 1` -> `"bcd"`). Standard string concatenation (`"a" + "b"`) is retained.
* **Subtraction (`-` / `rsub`):** Subtraction by an integer/float reduces unicode codes (`"python" - 5`). Subtraction by another string removes target substring bytes (`"abcdef" - "bd"` -> `"acef"`).
* **Multiplication (`*` / `rmul`):** String-by-integer multiplication performs classic repetition (`"a" * 3`). String-by-float scales codes. String-by-string evaluates element-wise Hadamard multiplication.
* **Division (`/`, `//`, `%`, `divmod`):** Performs exact truediv, floordiv, and modulo on character weights. Supports native `divmod("abc", 2)`. Falls back to default string formatting if `%s`, `%d`, or `%f` placeholders are present.
* **Exponentiation (`**`):** Exponentiates internal character weights (`"abc" ** 2`).

```python
import pymastring

print("abc" + 1)       # Outputs: "bcd"
print(1 + "abc")       # Right-hand addition -> Outputs: "bcd"
print("python" - 5)    # Left-shifts unicode positions
print("abcdef" - "bd") # Drops exact target slices -> Outputs: "acef"
print("abc" ** 2)      # Exponentiates character codes
print("xyz" / 2)       # Uniform code points scaling
print("xyz" // 2)      # Integer character division
print(divmod("a", 10)) # Returns tuple of (floordiv, modulo)
```

### 2. Matrix Cross-Multiplication Vector Behavior (`@`)
Using the `@` operator evaluates the structural linear algebra dot product between two string arrays. It multiplies the scalar weight vectors of matching index elements and accumulates the mathematical sum. Short strings automatically pad using standard null bytes (`\x00`).

```python
# Calculates: (ord('a') * ord('b')) -> 97 * 98
result = "a" @ "b"
print(result) # Outputs integer: 9506
```

### 3. Dynamic Structural Weight Evaluation & Element Extraction (`len()`, `str[i]`)

The global `len()` invocation evaluates context dynamically to guarantee maximum environment stability and prevent side-effect exceptions in external packages. Standard raw string literals retain traditional array element counts. However, iterated elements, indexed characters (`"a"[0]`), or `MathChar` objects compute and report the integrated unicode code point weight (`ord()`).

```python
import pymastring

# A primitive baseline string keeps its classic character length
print(len("abc"))     # Outputs integer: 3

# Single character indexing yields MathChar wrapper reporting true inner weight
char = "a"[0]
print(len(char))      # Outputs Unicode weight: 97

# Intercept loops pull typified MathChar wrappers
for char in "a":
    print(len(char))  # Outputs Unicode weight: 97
```

### 4. Unary Operators & Mathematical Casting (`-str`, `~str`, `abs()`, `int()`, `float()`, `round()`)

* **Unary Negation (`-`):** Reverses the string (`-"abc"` -> `"cba"`).
* **Bitwise NOT (`~`):** Inverts character bit positions (`~"abc"`).
* **Vector Norm (`abs()`):** Calculates Euclidean vector magnitude ($\sqrt{\sum \text{ord}(c)^2}$).
* **Numerical Casting (`int()`, `float()`, `round()`):** Fallbacks to total unicode character weight sum when parsing non-numeric strings.

```python
print(-"abc")         # Reverses string -> Outputs: "cba"
print(abs("abc"))     # Calculates Euclidean vector length
print(int("abc"))     # Returns sum of weights -> 97 + 98 + 99 = 294
print(float("abc"))   # Outputs: 294.0
print(round("abc"))   # Outputs: 294
```

### 5. Bitwise Vector Conversions (`<<`, `>>`, `&`, `|`, `^`)
Direct byte-level array transformations across registers using standard binary operational parameters.

```python
print("abc" << 2)        # Left shift bit positions
print("secret" ^ 42)     # XOR encryption mask mapping
print("hello" & "world")  # Matrix intersection overlay
```

### 6. Total-Weight Context Comparisons (`>`, `<`, `>=`, `<=`)
Rich comparative sorting algorithms base logic on total calculated inner array vector weight sums, replacing default sequential alphabetic ASCII sorting structures.

```python
print("short" > "longer") # Evaluates length/weight conditions
```

### 7. Typified Generator Array Extraction & Reversal
Loops and reversed iterators parsing raw string sequences yield operational wrappers (`MathChar`) inheriting full operational capabilities.

```python
for char in reversed("xyz"):
    print(char ** 1.5)
```

### 8. Custom JSON Serialization Engine (`MathJSONEncoder`)
To prevent internal character objects from breaking standard data transfers, use our targeted serialization mapping profile.

```python
import json

data = {"payload": "abc" ** 2}
json_string = json.dumps(data, cls=pymastring.MathJSONEncoder)
```

---

## License

MIT License - Copyright (c) 2026 ProgVM
