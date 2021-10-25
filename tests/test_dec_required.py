import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.decorator import RequiredCheck

class TestRequiredDecorators(unittest.TestCase):
    def test_required_gen(self):

        @RequiredCheck("one", "two")
        def req_test(**kwargs) -> float:
            return (kwargs.get("one", None), kwargs.get("two", None))
        
        result = req_test(one=1, two=2)
        assert result[0] == 1
        assert result[1] == 2
        result = req_test(two="b", one="a")
        assert result[0] == "a"
        assert result[1] == "b"
        with self.assertRaises(ValueError):
            result = req_test(one=1)
        with self.assertRaises(ValueError):
            result = req_test(two=2)

    def test_required_with_args(self):

        @RequiredCheck("one", "two")
        def req_test(first, second, **kwargs) -> float:
            return (first, second, kwargs.get("one", None), kwargs.get("two", None))

        result = req_test(first="start", second="", one=1, two=2)
        assert result[0] == "start"
        assert result[1] == ""
        assert result[2] == 1
        assert result[3] == 2

        with self.assertRaises(ValueError):
            result = req_test(first="start", second="", one=1)
        with self.assertRaises(ValueError):
            result = req_test(first="start", second="", two=2)

if __name__ == '__main__':
    unittest.main()
