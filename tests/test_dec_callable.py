import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import DefaultArgs, RequireArgs, CallTracker, calltracker


class TestRequiredDecorators(unittest.TestCase):

    def test_default_gen(self):

        @DefaultArgs(one=1, two=2)
        @RequireArgs("one", "two", "last")
        @CallTracker
        def req_test(**kwargs) -> float:
            return (kwargs.get("one"), kwargs.get("two"), kwargs.get("last"))
        assert req_test.has_been_called == False
        result = req_test(last="stop")
        assert req_test.has_been_called == True
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == "stop"
        result = req_test(two="b", one="a", last="")
        assert req_test.has_been_called == True
        assert result[0] == "a"
        assert result[1] == "b"
        assert result[2] == ""


    def test_default_with_args(self):

        @DefaultArgs(one=1, two=2)
        def req_test(first, second, **kwargs) -> float:
            return (first, second, kwargs.get("one", None), kwargs.get("two", None))

        result = req_test(first="start", second="")
        assert result[0] == "start"
        assert result[1] == ""
        assert result[2] == 1
        assert result[3] == 2


if __name__ == '__main__':
    unittest.main()
