import unittest

from .test_data import (
    parse_test_1_text,
    parse_test_1_json,
    parse_test_2_text,
    parse_test_2_json
)


class TestMojangsonParse(unittest.TestCase):
    def test_parse(self):
        from .. import parse
        for original, expected in [
            (parse_test_1_text, parse_test_1_json),
            (parse_test_2_text, parse_test_2_json)
        ]:
            with self.subTest(original=original):
                result = parse(original)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
