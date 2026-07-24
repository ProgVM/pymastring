import unittest
import json
import pymastring


class TestPyMaString(unittest.TestCase):

    def test_addition(self):
        self.assertEqual("abc" + 1, "bcd")
        self.assertEqual(1 + "abc", "bcd")
        self.assertEqual("abc" + True, "bcd")
        self.assertEqual("hello" + "world", "helloworld")

    def test_subtraction(self):
        self.assertEqual("abcdef" - "bd", "acef")
        self.assertEqual("python" - 5, "ktocji")
        self.assertEqual(1000 - "a", chr((1000 - 97) % 1114112))

    def test_multiplication(self):
        self.assertEqual("abc" * 2, "abcabc")
        self.assertEqual("a" * 2.0, chr(int(97 * 2.0)))
        self.assertEqual("a" * "b", chr((97 * 98) % 1114112))

    def test_division_and_rdivision(self):
        self.assertEqual("xyz" / 2, chr(int(ord('x') / 2)) + chr(int(ord('y') / 2)) + chr(int(ord('z') / 2)))
        self.assertEqual("xyz" // 2, chr(ord('x') // 2) + chr(ord('y') // 2) + chr(ord('z') // 2))
        self.assertEqual(200 / "a", chr(int(200 / 97)))
        self.assertEqual(200 // "a", chr(200 // 97))
        with self.assertRaises(ZeroDivisionError):
            _ = "abc" / 0

    def test_modulo_and_divmod(self):
        self.assertEqual("a" % 10, chr(97 % 10))
        self.assertEqual("hello %s", "hello %s")
        q, r = divmod("a", 10)
        self.assertEqual(q, chr(97 // 10))
        self.assertEqual(r, chr(97 % 10))

    def test_exponentiation(self):
        self.assertEqual("abc" ** 1, "abc")
        self.assertIsInstance("a" ** 2, str)
        self.assertEqual(2 ** "a", chr(int(2 ** 97) % 1114112))

    def test_matrix_multiplication(self):
        self.assertEqual("a" @ "b", 9506)
        self.assertEqual("abc" @ [1, 2, 3], 590)

    def test_custom_len_and_indexing(self):
        self.assertEqual(len("abc"), 3)
        for char in "a":
            self.assertEqual(len(char), 97)
        char_item = pymastring.MathChar("a")
        self.assertEqual(len(char_item), 97)

    def test_unaries_and_casting(self):
        self.assertEqual(-"abc", "cba")
        self.assertGreater(abs("abc"), 0)
        self.assertEqual(int("123"), 123)
        self.assertEqual(int("abc"), 294)
        self.assertEqual(float("123.45"), 123.45)
        self.assertEqual(float("abc"), 294.0)

    def test_bitwise_operators(self):
        self.assertEqual("a" << 2, chr((97 << 2) % 1114112))
        self.assertEqual("a" >> 2, chr((97 >> 2) % 1114112))
        self.assertEqual("a" & 15, chr(97 & 15))
        self.assertEqual("a" | 15, chr(97 | 15))
        self.assertEqual("a" ^ 15, chr(97 ^ 15))
        self.assertEqual(15 & "a", chr(15 & 97))

    def test_cross_type_and_nested_comparisons(self):
        self.assertTrue("aaa" > 1)
        self.assertTrue(1 < "aaa")
        self.assertTrue("aaa" == 291)
        self.assertTrue("abc" > [1, 2, 3])
        self.assertTrue([1, 2, 3] < "abc")
        self.assertTrue("abc" > None)
        self.assertTrue("longer" > "short")
        self.assertFalse("short" > "longer")

    def test_isinstance_compatibility(self):
        self.assertTrue(isinstance(0, int))
        self.assertTrue(isinstance(0.0, float))
        self.assertTrue(isinstance("abc", str))

    def test_iteration_and_reversal(self):
        items = [char for char in "a"]
        self.assertEqual(len(items[0]), 97)
        rev_items = [char for char in reversed("a")]
        self.assertEqual(len(rev_items[0]), 97)

    def test_json_encoder(self):
        data = {"key": "abc" ** 2}
        encoded = json.dumps(data, cls=pymastring.MathJSONEncoder)
        self.assertIn("key", encoded)


if __name__ == "__main__":
    unittest.main()
