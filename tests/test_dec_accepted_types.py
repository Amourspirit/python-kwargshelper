import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.decorator import AcceptedTypes, DecFuncEnum, RequireArgs, ReturnType


class TestAcceptedTypesDecorators(unittest.TestCase):
    def test_accepted_gen(self):

        @AcceptedTypes((int, str), (int, str))
        def req_test(**kwargs) -> float:
            return (kwargs.get("one"), kwargs.get("two"))

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
        with self.assertRaises(TypeError):
            result = req_test(one=4.5, two=2)

    def test_accept_required_with_args(self):

        @RequireArgs("one", "two")
        @AcceptedTypes(str, str, (int, str), (int, str))
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
        with self.assertRaises(TypeError):
            result = req_test(first="start", second="", one=1, two=2.5)


    def test_accept_class(self):
        class Foo:
            @AcceptedTypes((int, float), (int, float), ftype=DecFuncEnum.METHOD)
            def __init__(self, start, stop):
                self.start = start
                self.stop = stop
        f = Foo(1, 99.9)
        assert f.start == 1
        assert f.stop == 99.9
        with self.assertRaises(TypeError):
            f = Foo("yes", 99.9)

    def test_accept_class_static(self):
        class Foo:
            @AcceptedTypes((int, float), (int, float), ftype=DecFuncEnum.METHOD)
            def __init__(self, start, stop):
                self.start = start
                self.stop = stop
            
            @staticmethod
            @AcceptedTypes(int, int, ftype=DecFuncEnum.METHOD_STATIC)
            @ReturnType(int)
            def add(first, last):
                return first + last
        f = Foo(1, 99.9)
        assert f.start == 1
        assert f.stop == 99.9
        result = Foo.add(3, 2)
        assert result == 5
        with self.assertRaises(TypeError):
            result = Foo.add(1, 99.9)


    def test_accept_class_cls(self):
        class Foo:
            @AcceptedTypes((int, float), (int, float), ftype=DecFuncEnum.METHOD)
            def __init__(self, start, stop):
                self.start = start
                self.stop = stop

            @classmethod
            @AcceptedTypes(int, int, ftype=DecFuncEnum.METHOD_CLASS)
            @ReturnType(int)
            def add(cls, first, last):
                return first + last
        f = Foo(1, 99.9)
        assert f.start == 1
        assert f.stop == 99.9
        result = Foo.add(3, 2)
        assert result == 5
        with self.assertRaises(TypeError):
            result = Foo.add(1, 99.9)

if __name__ == '__main__':
    unittest.main()
