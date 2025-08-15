import unittest
from .test_data import simplify_test_data


class TestMojangsonSimplify(unittest.TestCase):
    def test_simplify(self):
        from .. import simplify, parse
        for original, expected in simplify_test_data:
            with self.subTest(original=original):
                result = simplify(parse(original))
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()