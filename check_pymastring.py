import pymastring

print("=== 1. Vectorized Arithmetic & Reflected Operators ===")
print("Left Addition:", "abc" + 1)                 # "bcd"
print("Right Addition:", 1 + "abc")                # "bcd"
print("Bool Addition:", "abc" + True)              # "bcd"
print("Left Subtraction:", "python" - 5)           # "ktocji"
print("Right Subtraction:", 1000 - "a")            # chr(1000 - 97)
print("Left Division:", "xyz" / 2)                 # Uniform code scaling
print("Right Division:", 200 / "a")                # Right-hand division
print("Left Modulo:", "a" % 10)                    # chr(97 % 10)
print("Divmod:", divmod("a", 10))                  # (floordiv, modulo)

print("\n=== 2. Single-Line Vernam Stream Cipher (XOR) ===")
message = "secret_code"
key = "my_super_key_123"
encrypted = message ^ key
decrypted = encrypted ^ key
print("Encrypted:", encrypted)
print("Decrypted:", decrypted)                     # "secret_code"

print("\n=== 3. Matrix Vector Dot Product (@) ===")
print("String @ String:", "a" @ "b")               # 9506
print("String @ List:", "abc" @ [1, 2, 3])         # 590

print("\n=== 4. Cross-Type Rich Comparisons ===")
print("String > Integer:", "aaa" > 1)              # True (291 > 1)
print("Integer < String:", 100 < "aaa")            # True (100 < 291)
print("String == Weight:", "aaa" == 291)           # True
print("String > List:", "abc" > [1, 2, 3])         # True
print("String > None:", "abc" > None)              # True (294 > 0)

print("\n=== 5. Dynamic Weight Evaluation & Iteration ===")
print("Base string length:", len("abc"))           # 3
for char in "a":
    print("Loop char length:", len(char))          # 97

print("\n=== 6. Unary Operators & Vector Norm ===")
print("Negation (Reverse):", -"abc")               # "cba"
print("Vector Norm abs():", abs("abc"))            # ~169.75

print("\n=== 7. Metaclass-Enabled Transparent Casting ===")
print("Numeric Int Cast:", int("123"))             # 123
print("Non-Numeric Int Cast:", int("abc"))         # 294
print("Numeric Float Cast:", float("123.45"))      # 123.45
print("Non-Numeric Float Cast:", float("abc"))     # 294.0
print("Isinstance check:", isinstance(0, int))     # True
