# pymastring

`pymastring` is a highly unorthodox utility package that globally overrides the runtime behavior of Python's built-in primitive `str` class via deep C-level monkey-patching. It breaks standard structural limitations to allow direct mathematical calculations, matrix equations, bitwise interactions, and custom serialization paradigms natively on raw string literals.

---

## Technical Concept

Python's built-in `str` instances are hardcoded at the C-API level to prevent arbitrary mutation. `pymastring` bypasses this defense mechanism by using `forbiddenfruit` to overwrite core slots within the `PyTypeObject` of the native string type.

Every mathematical operation maps the characters of the string to their respective **Unicode Code Points** (via `ord()`), runs numerical adjustments, applies an auto-overflow modulo bounds-check (`% 1114112`), and returns the resulting value shifted back into strings (via `chr()`).

---

## Installation

Install the package locally in editable development mode or via local source directory distribution:

```bash
pip install .
```

---

## Core Features & Extended API Specification

### 1. Advanced Arithmetic Operators (`**`, `/`, `-`, `%`)
Standard string literals can be manipulated mathematically with integers and floating-point elements.
* **Exponentiation (`**`):** Exponentiates the individual internal weight of every distinct character.
* **Division (`/`):** Divides character codes uniformly.
* **Subtraction (`-`):** Subtraction by an integer/float dynamically reduces unicode codes. Subtraction by another string removes all structural occurrences of those bytes.
* **Modulo (`%`):** Determines remainder against character weights. Falls back to default string formatting if `%s`, `%d`, or `%f` structural placeholders are present.

```python
import pymastring

print("abc" ** 2)      # Exponentiates character codes
print("xyz" / 2)       # Uniform code points scaling
print("python" - 5)    # Left-shifts unicode positions
print("abcdef" - "bd") # Drops exact target slices -> Outputs: "acef"
print("hello" % 3)     # Inline remainder extraction
```

### 2. Matrix Cross-Multiplication Vector Behavior (`@`)
Using the `@` operator evaluates the structural linear algebra dot product between two string arrays. It multiplies the scalar weight vectors of matching index elements and accumulates the mathematical sum. Short strings automatically pad using standard null bytes (`\x00`).

```python
# Calculates: (ord('a') * ord('b')) -> 97 * 98
result = "a" @ "b"
print(result) # Outputs integer: 9506
```

### 3. Dynamic Structural Weight Evaluation (`len()`)
The global `len()` invocation is intercepted. Instead of reporting the primitive flat character index array offset count, it computes and returns the complete integrated sum of all unicode sequence code weights.

```python
# Traditional len("abc") returns 3
# Patched version evaluates: 97 + 98 + 99
print(len("abc")) # Outputs integer: 294
```

### 4. Bitwise Vector Conversions (`<<`, `>>`, `&`, `|`, `^`)
Direct byte-level array transformations across registers using standard binary operational parameters.

```python
print("abc" << 2)      # Left shift bit positions
print("secret" ^ 42)   # XOR encryption mask mapping
print("hello" & "world") # Matrix intersection overlay
```

### 5. Total-Weight Context Comparisons (`>`, `<`, `>=`, `<=`)
Rich comparative sorting algorithms base logic on total calculated inner array vector weight sums, replacing default sequential alphabetic ASCII sorting structures.

```python
print("short" > "longer") # Strictly evaluates length/weight conditions
```

### 6. Typified Generator Array Extraction & Iteration
Loops parsing raw string sequences yield special operational wrappers (`MathChar`) inheriting full operational capabilities rather than flat string parts.

```python
for char in "xyz":
    # Loops pull fully functioning MathChar objects allowing immediate manipulation
    print(char ** 1.5)
```

### 7. Custom JSON Serialization Engine (`MathJSONEncoder`)
To prevent internal character objects from breaking standard data transfers, use our targeted serialization mapping profile.

```python
import json

data = {"payload": "abc" ** 2}
json_string = json.dumps(data, cls=pymastring.MathJSONEncoder)
```

