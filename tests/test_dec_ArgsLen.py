import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import ArgsLen, DecFuncEnum


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


if __name__ == '__main__':
    unittest.main()
