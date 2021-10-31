import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import DefaultArgs, RequireArgs, calltracker, callcounter


class TestRequiredDecorators(unittest.TestCase):

    def test_default_gen(self):
        @calltracker
        @DefaultArgs(one=1, two=2)
        @RequireArgs("one", "two", "last")
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

    def test_calltracker(self):
        class Internal:
            @calltracker
            @DefaultArgs(one=1, two=2)
            @RequireArgs("one", "two", "last")
            def req_test(self, **kwargs) -> float:
                return (kwargs.get("one"), kwargs.get("two"), kwargs.get("last"))
        internal = Internal()
        assert internal.req_test.has_been_called == False
        result = internal.req_test(last="stop")
        assert internal.req_test.has_been_called == True

    def test_callcounter(self):
        class Internal:
            @callcounter
            @DefaultArgs(one=1, two=2)
            @RequireArgs("one", "two", "last")
            def req_test(self, **kwargs) -> float:
                return (kwargs.get("one"), kwargs.get("two"), kwargs.get("last"))
        internal = Internal()
        assert internal.req_test.call_count == 0
        result = internal.req_test(last="stop")
        assert internal.req_test.call_count == 1
        result = internal.req_test(last="End")
        assert internal.req_test.call_count == 2

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
