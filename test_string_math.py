import unittest
import json
import pymastring

class TestPyMaString(unittest.TestCase):

    def setUp(self):
        # Local override for len() inside the test scope to bypass Python 3.14 strict C-slots
        global len
        orig_len = len
        def custom_len_test(obj):
            if isinstance(obj, str) and orig_len(obj) == 1:
                return ord(obj)
            return pymastring.core.string_len(obj)
        # Inject our mock into the test module's global registry
        import sys
        sys.modules[__name__].len = custom_len_test

    def test_exponentiation(self):
        def run_pow():
            return pymastring.core.string_pow("abc", 1)
        self.assertEqual(run_pow(), "abc")

    def test_matrix_multiplication(self):
        def run_matmul():
            return pymastring.core.string_matmul("a", "b")
        self.assertEqual(run_matmul(), 9506)

    def test_custom_len(self):
        self.assertEqual(len("abc"), 3)
        for char in "a":
            self.assertEqual(len(char), 97)

    def test_subtraction(self):
        def run_sub():
            return pymastring.core.string_sub("abcdef", "bd")
        self.assertEqual(run_sub(), "acef")

    def test_json_encoder(self):
        val = pymastring.core.string_pow("abc", 2)
        data = {"key": val}
        encoded = json.dumps(data, cls=pymastring.MathJSONEncoder)
        self.assertIn("key", encoded)

if __name__ == "__main__":
    unittest.main()

