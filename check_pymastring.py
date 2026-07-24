import pymastring

# 1. Arithmetic with numbers and strings
print("1. Addition:", "abc" + 1)            # Expected: "bcd"
print("2. Right Addition:", 1 + "abc")      # Expected: "bcd"
print("3. Subtraction:", "python" - 5)       # Expected: "ktocji"

# 4. Matrix multiplication
print("4. Matrix @:", "a" @ "b")            # Expected: 9506

# 5. Length evaluation
print("5. Base len:", len("abc"))           # Expected: 3
for char in "a":
    print("6. Loop char len:", len(char))   # Expected: 97

# 7. Unary operators
print("7. Negation (reverse):", -"abc")     # Expected: "cba"
print("8. Vector norm abs():", abs("abc"))  # Expected: ~169.81

# 9. Numeric casting
print("9. Valid Int cast:", int("123"))     # Expected: 123
print("10. Valid Float cast:", float("123.45")) # Expected: 123.45

# 11. Comparisons
print("11. Rich Comparison:", "longer" > "short") # Expected: True
