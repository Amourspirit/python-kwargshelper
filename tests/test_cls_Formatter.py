import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.helper import Formatter


class TestFormatter(unittest.TestCase):
    def test_ordianl(self):
        result = Formatter.get_ordinal(1)
        self.assertEqual(result, "1st")
        result = Formatter.get_ordinal(2)
        self.assertEqual(result, "2nd")
        result = Formatter.get_ordinal(4)
        self.assertEqual(result, "4th")
        result = Formatter.get_ordinal(10)
        self.assertEqual(result, "10th")
        result = Formatter.get_ordinal(11)
        self.assertEqual(result, "11th")
        result = Formatter.get_ordinal(22)
        self.assertEqual(result, "22nd")
        result = Formatter.get_ordinal(33)
        self.assertEqual(result, "33rd")

    def test_get_formated_names(self):
        result = Formatter.get_formated_names(names=['first'])
        assert result == "'first'"
        result = Formatter.get_formated_names(names=['first', 'second'])
        assert result == "'first' and 'second'"
        result = Formatter.get_formated_names(
            names=['first', 'second', 'third'])
        assert result == "'first', 'second', and 'third'"

if __name__ == '__main__':
    unittest.main()
