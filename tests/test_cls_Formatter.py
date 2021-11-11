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

    def test_get_formated_types(self):
        types = [str, float, type(self)]
        result = Formatter.get_formated_types(types=[str, float, type(self)])
        assert isinstance(result, str)
        for t in types:
            t_name = f"'{t.__name__}'"
            assert result.index(t_name) >= 0
        assert result.index('and') > 0
        result = Formatter.get_formated_types(types=[str, float, type(self)], conj='or', wrapper="")
        assert isinstance(result, str)
        for t in types:
            t_name = f"{t.__name__}"
            assert result.index(t_name) >= 0
        assert result.index('or') > 0

    def test_get_missing_args_error_msg(self):
        names_lst = ['first', 'second', 'third']
        name = 'myfunc()'
        result = Formatter.get_missing_args_error_msg(missing_names=names_lst, name=name)
        assert isinstance(result, str)
        assert result.startswith(name)
        for n in names_lst:
            assert result.index(n) > 0
        names_lst = ['first']
        result = Formatter.get_missing_args_error_msg(
            missing_names=names_lst)
        assert isinstance(result, str)
        assert result.startswith("missing")
        for n in names_lst:
            assert result.index(n) > 0
        

if __name__ == '__main__':
    unittest.main()
