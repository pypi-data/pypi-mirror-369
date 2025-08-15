import unittest
from .test_data import stringify_test_data


class TestMojangsonStringify(unittest.TestCase):
    def test_simplify(self):
        from .. import stringify, parse
        for original, expected in stringify_test_data:
            with self.subTest(original=original):
                result = stringify(parse(original))
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
