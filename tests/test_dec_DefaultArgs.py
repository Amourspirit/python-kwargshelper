import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.decorator import DefaultArgs, RequireArgs
from enum import IntEnum, auto


class Color(IntEnum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

    def __str__(self) -> str:
        return self._name_

class TestRequiredDecorators(unittest.TestCase):

    def test_default_gen(self):

        @DefaultArgs(one=1, two=2)
        @RequireArgs("one", "two", "last")
        def req_test(**kwargs) -> float:
            return (kwargs.get("one"), kwargs.get("two"), kwargs.get("last"))

        result = req_test(last="stop")
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == "stop"
        result = req_test(two="b", one="a", last="")
        assert result[0] == "a"
        assert result[1] == "b"
        assert result[2] == ""
        with self.assertRaises(ValueError):
            result = req_test(one=1)
        with self.assertRaises(ValueError):
            result = req_test(two=2)

    def test_default_enum(self):
        @DefaultArgs(one=Color.RED, two=Color.BLUE)
        @RequireArgs("one", "two", "last")
        def req_test(**kwargs) -> float:
            return (kwargs.get("one"), kwargs.get("two"), kwargs.get("last"))
        result = req_test(last="stop")
        assert result[0] == Color.RED
        assert result[1] == Color.BLUE
        assert result[2] == "stop"

    def test_default_optional(self):
        @DefaultArgs(one=1, two=2)
        @RequireArgs("one", "two", "last")
        def req_test(one, two, **kwargs) -> float:
            return (one, two, kwargs.get("last"))
        result = req_test(last="stop")
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == "stop"
        
    def test_default_args_optional(self):
        @DefaultArgs(one=1, two=2)
        @RequireArgs("one", "two", "last")
        def req_test(*args, one, two, **kwargs) -> float:
            return [*args] + [one, two, kwargs.get("last")]
        result = req_test(10, last="stop")
        assert result[0] == 10
        assert result[1] == 1
        assert result[2] == 2
        assert result[3] == "stop"
        result = req_test("a", "b","c", last="stop")
        assert result[0] == "a"
        assert result[1] == "b"
        assert result[2] == "c"
        assert result[3] == 1
        assert result[4] == 2
        assert result[5] == "stop"
        result = req_test("a", "b", "c", last="stop", two="too", one="*")
        assert result[0] == "a"
        assert result[1] == "b"
        assert result[2] == "c"
        assert result[3] == "*"
        assert result[4] == "too"
        assert result[5] == "stop"

    def test_default_with_args(self):

        @DefaultArgs(one=1, two=2)
        def req_test(first, second, **kwargs) -> float:
            return (first, second, kwargs.get("one", None), kwargs.get("two", None))

        result = req_test(first="start", second="")
        assert result[0] == "start"
        assert result[1] == ""
        assert result[2] == 1
        assert result[3] == 2

    def test_cls_default_args_optional(self):
        class Foo:
            @DefaultArgs(one=1, two=2)
            @RequireArgs("one", "two", "last")
            def req_test(self, *args, one, two, **kwargs) -> float:
                return [*args] + [one, two, kwargs.get("last")]
        f = Foo()
        result = f.req_test(10, last="stop")
        assert result[0] == 10
        assert result[1] == 1
        assert result[2] == 2
        assert result[3] == "stop"
        result = f.req_test("a", "b", "c", last="stop")
        assert result[0] == "a"
        assert result[1] == "b"
        assert result[2] == "c"
        assert result[3] == 1
        assert result[4] == 2
        assert result[5] == "stop"
        result = f.req_test("a", "b", "c", last="stop", two="too", one="*")
        assert result[0] == "a"
        assert result[1] == "b"
        assert result[2] == "c"
        assert result[3] == "*"
        assert result[4] == "too"
        assert result[5] == "stop"

    def test_cls_default_static_args_optional(self):
        class Foo:
            @staticmethod
            @DefaultArgs(one=1, two=2)
            @RequireArgs("one", "two", "last")
            def req_test(*args, one, two, **kwargs) -> float:
                return [*args] + [one, two, kwargs.get("last")]
        result = Foo.req_test(10, last="stop")
        assert result[0] == 10
        assert result[1] == 1
        assert result[2] == 2
        assert result[3] == "stop"
        result = Foo.req_test("a", "b", "c", last="stop")
        assert result[0] == "a"
        assert result[1] == "b"
        assert result[2] == "c"
        assert result[3] == 1
        assert result[4] == 2
        assert result[5] == "stop"
        result = Foo.req_test("a", "b", "c", last="stop", two="too", one="*")
        assert result[0] == "a"
        assert result[1] == "b"
        assert result[2] == "c"
        assert result[3] == "*"
        assert result[4] == "too"
        assert result[5] == "stop"

    def test_cls_default_class_args_optional(self):
        class Foo:
            @classmethod
            @DefaultArgs(one=1, two=2)
            @RequireArgs("one", "two", "last")
            def req_test(cls, *args, one, two, **kwargs) -> float:
                return [*args] + [one, two, kwargs.get("last")]
        result = Foo.req_test(10, last="stop")
        assert result[0] == 10
        assert result[1] == 1
        assert result[2] == 2
        assert result[3] == "stop"
        result = Foo.req_test("a", "b", "c", last="stop")
        assert result[0] == "a"
        assert result[1] == "b"
        assert result[2] == "c"
        assert result[3] == 1
        assert result[4] == 2
        assert result[5] == "stop"
        result = Foo.req_test("a", "b", "c", last="stop", two="too", one="*")
        assert result[0] == "a"
        assert result[1] == "b"
        assert result[2] == "c"
        assert result[3] == "*"
        assert result[4] == "too"
        assert result[5] == "stop"

if __name__ == '__main__':
    unittest.main()
