import unittest
from collections import namedtuple
from enum import IntEnum, auto
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import ArgsLen, DecFuncEnum

class Color(IntEnum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

    def __str__(self) -> str:
        return self._name_

RangeTuple = namedtuple('RangeTuple', ['start', 'end'])

class TestArgsLen(unittest.TestCase):

    def test_gen(self):
        @ArgsLen(3)
        def foo(*args):
            return len(args)
        result = foo("a", "b", "c")
        assert result == 3
        with self.assertRaises(ValueError):
            result = foo()
        with self.assertRaises(ValueError):
            foo("a", "b")
        with self.assertRaises(ValueError):
            foo("a")

    def test_incorrect_args(self):
        with self.assertRaises(ValueError):
            @ArgsLen()
            def foo(*args): pass

    def test_enum(self):
        @ArgsLen(0, 2)
        def foo(*args):
            return len(args)
        result = foo()
        assert result == 0
        result = foo(Color.RED, Color.BLUE)
        assert result == 2
        with self.assertRaises(ValueError):
            foo(Color.RED, Color.BLUE, Color.GREEN)
        with self.assertRaises(ValueError):
            foo(Color.RED)

    def test_tuple(self):
        @ArgsLen(3)
        def foo(*args):
            return len(args)
        result = foo(("a",1), ("b", 2), ("c", 3))
        assert result == 3
        with self.assertRaises(ValueError):
            result = foo()
        with self.assertRaises(ValueError):
            foo("a", "b")
        with self.assertRaises(ValueError):
            foo("a")

    def test_repeat_lens(self):
        @ArgsLen(3, 3, 3, 3, 3)
        def foo(*args):
            return len(args)
        result = foo("a", "b", "c")
        assert result == 3
        with self.assertRaises(ValueError):
            result = foo()
        with self.assertRaises(ValueError):
            foo("a", "b")
        with self.assertRaises(ValueError):
            foo("a")


    def test_name_tuple(self):
        @ArgsLen(2)
        def foo(*args):
            return len(args)
        result = foo(RangeTuple(0, 2), (2, 4))
        assert result == 2

    def test_two_lens(self):
        @ArgsLen(3, 5)
        def foo(*args):
            return len(args)
        result = foo("a", "b", "c")
        assert result == 3
        result = foo("a", "b", "c", "d", "e")
        assert result == 5
        with self.assertRaises(ValueError):
            result = foo()
        with self.assertRaises(ValueError):
            foo("a", "b")
        with self.assertRaises(ValueError):
            foo("a")
        with self.assertRaises(ValueError):
            foo("a", "b", "c", "d")
    
    def test_three_lens(self):
        @ArgsLen(3, 5 , 7)
        def foo(*args):
            return len(args)
        result = foo("a", "b", "c")
        assert result == 3
        result = foo("a", "b", "c", "d", "e")
        assert result == 5
        result = foo("a", "b", "c", "d", "e","f", "g")
        assert result == 7
        with self.assertRaises(ValueError):
            result = foo()
        with self.assertRaises(ValueError):
            foo("a", "b")
        with self.assertRaises(ValueError):
            foo("a")
        with self.assertRaises(ValueError):
            foo("a", "b", "c", "d")
        with self.assertRaises(ValueError):
            foo("a", "b", "c", "d", "e", "f")

    def test_range(self):
        @ArgsLen((3,5))
        def foo(*args):
            return len(args)
        result = foo("a", "b", "c")
        assert result == 3
        result = foo("a", "b", "c", "d")
        assert result == 4
        result = foo("a", "b", "c", "d", "e")
        assert result == 5

    def test_range_repeat(self):
        @ArgsLen((3, 5), (3, 5), (3, 5), (3, 5))
        def foo(*args):
            return len(args)
        result = foo("a", "b", "c")
        assert result == 3
        result = foo("a", "b", "c", "d")
        assert result == 4
        result = foo("a", "b", "c", "d", "e")
        assert result == 5

    def test_ranges(self):
        @ArgsLen((3, 5), (7, 9))
        def foo(*args):
            return len(args)
        result = foo("a", "b", "c")
        assert result == 3
        result = foo("a", "b", "c", "d")
        assert result == 4
        result = foo("a", "b", "c", "d", "e")
        assert result == 5
        result = foo("a", "b", "c", "d", "e", "f", "g")
        assert result == 7
        result = foo("a", "b", "c", "d", "e", "f", "g", "h")
        assert result == 8
        result = foo("a", "b", "c", "d", "e", "f", "g", "h", "i")
        assert result == 9
        with self.assertRaises(ValueError):
            foo()
        with self.assertRaises(ValueError):
            foo("a", "b")
        with self.assertRaises(ValueError):
            foo("a", "b", "c", "d", "e", "f")

    def test_int_range(self):
        @ArgsLen(2, (5, 7))
        def foo(*args):
            return len(args)
        result = foo("a", "b")
        assert result == 2
        result = foo("a", "b", "c", "d", "e")
        assert result == 5
        result = foo("a", "b", "c", "d", "e", "f")
        assert result == 6
        result = foo("a", "b", "c", "d", "e", "f", "g")
        assert result == 7
        with self.assertRaises(ValueError):
            foo()
        with self.assertRaises(ValueError):
            foo("a")
        with self.assertRaises(ValueError):
            foo("a", "b", "c")
    
    def test_int_range_kwargs(self):
        @ArgsLen(2, (5, 7))
        def foo(*args, **kwargs):
            return len(args), len(kwargs)
        result = foo("a", "b")
        assert result[0] == 2
        result = foo("a", "b", a=1, b=2)
        assert result[0] == 2
        result = foo("a", "b", "c", "d", "e")
        assert result[0] == 5
        result = foo("a", "b", "c", "d", "e", a=1, b=2)
        assert result[0] == 5
        result = foo("a", "b", "c", "d", "e", "f")
        assert result[0] == 6
        result = foo("a", "b", "c", "d", "e", "f", a=1, b=2)
        assert result[0] == 6
        result = foo("a", "b", "c", "d", "e", "f", "g")
        assert result[0] == 7
        result = foo("a", "b", "c", "d", "e", "f", "g", a=1, b=2)
        assert result[0] == 7
        with self.assertRaises(ValueError):
            foo()
        with self.assertRaises(ValueError):
            foo(a=1,b=2)
        with self.assertRaises(ValueError):
            foo("a")
        with self.assertRaises(ValueError):
            foo("a", a=1, b=2)
        with self.assertRaises(ValueError):
            foo("a", "b", "c")
        with self.assertRaises(ValueError):
            foo("a", "b", "c", a=1, b=2)

    def test_int_range_names_kwargs(self):
        @ArgsLen(2, (5, 7))
        def foo(*args, a, b, **kwargs):
            return len(args), len(kwargs), a, b
        result = foo("a", "b", a=1, b=2)
        assert result[0] == 2
        result = foo("a", "b", a=1, b=2, one="one", two="two")
        assert result[0] == 2
        result = foo("a", "b", "c", "d", "e", a=1, b=2)
        assert result[0] == 5
        result = foo("a", "b", "c", "d", "e", a=1, b=2, one="one", two="two")
        assert result[0] == 5
        result = foo("a", "b", "c", "d", "e", "f", a=1, b=2)
        assert result[0] == 6
        result = foo("a", "b", "c", "d", "e", "f",
                     a=1, b=2, one="one", two="two")
        assert result[0] == 6
        result = foo("a", "b", "c", "d", "e", "f", "g",
                     a=1, b=2, one="one", two="two")
        assert result[0] == 7
        result = foo("a", "b", "c", "d", "e", "f", "g", a=1, b=2)
        assert result[0] == 7
        with self.assertRaises(ValueError):
            foo(a=1, b=2)
        with self.assertRaises(ValueError):
            foo(a=1, b=2, one="one", two="two")
        with self.assertRaises(ValueError):
            foo("a", a=1, b=2)
        with self.assertRaises(ValueError):
            foo("a", a=1, b=2, one="one", two="two")
        with self.assertRaises(ValueError):
            foo("a", "b", "c", a=1, b=2)
        with self.assertRaises(ValueError):
            foo("a", "b", "c", a=1, b=2, one="one", two="two")

    def test_star_args_third(self):
        @ArgsLen(2, 4)
        def foo(arg1, arg2, *args, a, b, **kwargs):
            return len(args), len(kwargs), (a, b), (arg1, arg2)
        result = foo("a1", "b2", 1, 2, a=1, b=2, opt1="one", opt2="two")
        assert result[0] == 2
        result = foo("a1", "b2", 1, 2,3 , 4, a=1, b=2, opt1="one", opt2="two")
        assert result[0] == 4

class TestArgsLenClass(unittest.TestCase):

    def test_gen(self):
        class Bar:
            @ArgsLen(3, ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo("a", "b", "c")
        assert result == 3
        with self.assertRaises(ValueError):
            result = b.foo()
        with self.assertRaises(ValueError):
            b.foo("a", "b")
        with self.assertRaises(ValueError):
            b.foo("a")

    def test_two_lens(self):
        class Bar:
            @ArgsLen(3, 5, ftype = DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo("a", "b", "c")
        assert result == 3
        result = b.foo("a", "b", "c", "d", "e")
        assert result == 5
        with self.assertRaises(ValueError):
            result = b.foo()
        with self.assertRaises(ValueError):
            b.foo("a", "b")
        with self.assertRaises(ValueError):
            b.foo("a")
        with self.assertRaises(ValueError):
            b.foo("a", "b", "c", "d")

    def test_three_lens(self):
        class Bar:
            @ArgsLen(3, 5, 7, ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo("a", "b", "c")
        assert result == 3
        result = b.foo("a", "b", "c", "d", "e")
        assert result == 5
        result = b.foo("a", "b", "c", "d", "e", "f", "g")
        assert result == 7
        with self.assertRaises(ValueError):
            result = b.foo()
        with self.assertRaises(ValueError):
            b.foo("a", "b")
        with self.assertRaises(ValueError):
            b.foo("a")
        with self.assertRaises(ValueError):
            b.foo("a", "b", "c", "d")
        with self.assertRaises(ValueError):
            b.foo("a", "b", "c", "d", "e", "f")

    def test_range(self):
        class Bar:
            @ArgsLen((3, 5), ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo("a", "b", "c")
        assert result == 3
        result = b.foo("a", "b", "c", "d")
        assert result == 4
        result = b.foo("a", "b", "c", "d", "e")
        assert result == 5

    def test_ranges(self):
        class Bar:
            @ArgsLen((3, 5), (7, 9), ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo("a", "b", "c")
        assert result == 3
        result = b.foo("a", "b", "c", "d")
        assert result == 4
        result = b.foo("a", "b", "c", "d", "e")
        assert result == 5
        result = b.foo("a", "b", "c", "d", "e", "f", "g")
        assert result == 7
        result = b.foo("a", "b", "c", "d", "e", "f", "g", "h")
        assert result == 8
        result = b.foo("a", "b", "c", "d", "e", "f", "g", "h", "i")
        assert result == 9
        with self.assertRaises(ValueError):
            b.foo()
        with self.assertRaises(ValueError):
            b.foo("a", "b")
        with self.assertRaises(ValueError):
            b.foo("a", "b", "c", "d", "e", "f")

    def test_int_range(self):
        class Bar:
            @ArgsLen(2, (5, 7), ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo("a", "b")
        assert result == 2
        result = b.foo("a", "b", "c", "d", "e")
        assert result == 5
        result = b.foo("a", "b", "c", "d", "e", "f")
        assert result == 6
        result = b.foo("a", "b", "c", "d", "e", "f", "g")
        assert result == 7
        with self.assertRaises(ValueError):
            b.foo()
        with self.assertRaises(ValueError):
            b.foo("a")
        with self.assertRaises(ValueError):
            b.foo("a", "b", "c")

    def test_int_range_kwargs(self):
        class Bar:
            @ArgsLen(2, (5, 7), ftype=DecFuncEnum.METHOD)
            def foo(self, *args, **kwargs):
                return len(args), len(kwargs)
        b = Bar()
        result = b.foo("a", "b")
        assert result[0] == 2
        result = b.foo("a", "b", a=1, b=2)
        assert result[0] == 2
        result = b.foo("a", "b", "c", "d", "e")
        assert result[0] == 5
        result = b.foo("a", "b", "c", "d", "e", a=1, b=2)
        assert result[0] == 5
        result = b.foo("a", "b", "c", "d", "e", "f")
        assert result[0] == 6
        result = b.foo("a", "b", "c", "d", "e", "f", a=1, b=2)
        assert result[0] == 6
        result = b.foo("a", "b", "c", "d", "e", "f", "g")
        assert result[0] == 7
        result = b.foo("a", "b", "c", "d", "e", "f", "g", a=1, b=2)
        assert result[0] == 7
        with self.assertRaises(ValueError):
            b.foo()
        with self.assertRaises(ValueError):
            b.foo(a=1, b=2)
        with self.assertRaises(ValueError):
            b.foo("a")
        with self.assertRaises(ValueError):
            b.foo("a", a=1, b=2)
        with self.assertRaises(ValueError):
            b.foo("a", "b", "c")
        with self.assertRaises(ValueError):
            b.foo("a", "b", "c", a=1, b=2)

    def test_int_range_names_kwargs(self):
        class Bar:
            @ArgsLen(2, (5, 7), ftype=DecFuncEnum.METHOD)
            def foo(self, *args, a, b, **kwargs):
                return len(args), len(kwargs), a, b
        b = Bar()
        result = b.foo("a", "b", a=1, b=2)
        assert result[0] == 2
        result = b.foo("a", "b", a=1, b=2, one="one", two="two")
        assert result[0] == 2
        result = b.foo("a", "b", "c", "d", "e", a=1, b=2)
        assert result[0] == 5
        result = b.foo("a", "b", "c", "d", "e", a=1, b=2, one="one", two="two")
        assert result[0] == 5
        result = b.foo("a", "b", "c", "d", "e", "f", a=1, b=2)
        assert result[0] == 6
        result = b.foo("a", "b", "c", "d", "e", "f",
                     a=1, b=2, one="one", two="two")
        assert result[0] == 6
        result = b.foo("a", "b", "c", "d", "e", "f", "g",
                     a=1, b=2, one="one", two="two")
        assert result[0] == 7
        result = b.foo("a", "b", "c", "d", "e", "f", "g", a=1, b=2)
        assert result[0] == 7
        with self.assertRaises(ValueError):
            b.foo(a=1, b=2)
        with self.assertRaises(ValueError):
            b.foo(a=1, b=2, one="one", two="two")
        with self.assertRaises(ValueError):
            b.foo("a", a=1, b=2)
        with self.assertRaises(ValueError):
            b.foo("a", a=1, b=2, one="one", two="two")
        with self.assertRaises(ValueError):
            b.foo("a", "b", "c", a=1, b=2)
        with self.assertRaises(ValueError):
            b.foo("a", "b", "c", a=1, b=2, one="one", two="two")

    def test_int_range_names_kwargs_static(self):
        class Bar:
            @staticmethod
            @ArgsLen(2, (5, 7), ftype=DecFuncEnum.METHOD_STATIC)
            def foo(*args, a, b, **kwargs):
                return len(args), len(kwargs), a, b
        result = Bar.foo("a", "b", a=1, b=2)
        assert result[0] == 2
        result = Bar.foo("a", "b", a=1, b=2, one="one", two="two")
        assert result[0] == 2

    def test_int_range_names_kwargs_class(self):
        class Bar:
            @classmethod
            @ArgsLen(2, (5, 7), ftype=DecFuncEnum.METHOD_CLASS)
            def foo(cls, *args, a, b, **kwargs):
                return len(args), len(kwargs), a, b
        result = Bar.foo("a", "b", a=1, b=2)
        assert result[0] == 2
        result = Bar.foo("a", "b", a=1, b=2, one="one", two="two")
        assert result[0] == 2

    def test_star_args_third(self):
        class Bar:
            @ArgsLen(2, 4, ftype=DecFuncEnum.METHOD)
            def foo(self, arg1, arg2, *args, a, b, **kwargs):
                return len(args), len(kwargs), (a, b), (arg1, arg2)
        b = Bar()
        result = b.foo("a1", "b2", 1, 2, a=1, b=2, opt1="one", opt2="two")
        assert result[0] == 2
        result = b.foo("a1", "b2", 1, 2, 3, 4, a=1, b=2, opt1="one", opt2="two")
        assert result[0] == 4

    def test_enum(self):
        class Bar:
            @ArgsLen(0, 2, ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo()
        assert result == 0
        result = b.foo(Color.RED, Color.BLUE)
        assert result == 2
        with self.assertRaises(ValueError):
            b.foo(Color.RED, Color.BLUE, Color.GREEN)
        with self.assertRaises(ValueError):
            b.foo(Color.RED)

    def test_tuple(self):
        @ArgsLen(3)
        def foo(*args):
            return len(args)
        result = foo(("a", 1), ("b", 2), ("c", 3))
        assert result == 3
        with self.assertRaises(ValueError):
            result = foo()
        with self.assertRaises(ValueError):
            foo("a", "b")
        with self.assertRaises(ValueError):
            foo("a")

    def test_name_tuple(self):
        class Words:
            @ArgsLen(0, 2, 4, ftype=DecFuncEnum.METHOD)
            def __init__(self, *args):
                self._ranges  = []
                self._end = 0
                self._value = 0
                self.append(*args)

            @ArgsLen(0, 1, 2, 4, ftype=DecFuncEnum.METHOD)
            def append(self, *args):
                return [*args]
        t = Words()
        result = t.append(RangeTuple(0, 2))
        assert len(result) == 1
        result = t.append(RangeTuple(0, 2), (2, 4))
        assert len(result) == 2
        result = t.append(RangeTuple(0, 2), (2, 4), (6, 8, 10), 2)
        assert len(result) == 4
        with self.assertRaises(ValueError):
            result = t.append(RangeTuple(0, 2), (2, 4), (6, 8, 10))
        with self.assertRaises(ValueError):
            Words(1)
        with self.assertRaises(ValueError):
            Words(1, 1, 1)
        with self.assertRaises(ValueError):
            Words(1, 1, 1, 1, 1)

if __name__ == '__main__':
    unittest.main()
