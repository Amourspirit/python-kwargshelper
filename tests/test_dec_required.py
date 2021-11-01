import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.decorator import DecFuncEnum, RequireArgs

class TestRequiredDecorators(unittest.TestCase):
    def test_required_gen(self):

        @RequireArgs("one", "two")
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

        @RequireArgs("one", "two")
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

    def test_required_opt_args(self):

        @RequireArgs("one", "two")
        def req_test(first, second="two", **kwargs) -> float:
            return (first, second, kwargs.get("one", None), kwargs.get("two", None))

        result = req_test(first="start", one=1, two=2)
        assert result[0] == "start"
        assert result[1] == "two"
        assert result[2] == 1
        assert result[3] == 2
        with self.assertRaises(ValueError):
            result = req_test(first="start", one=1)

    def test_required_args_kwargs(self):
        @RequireArgs("one", "two")
        def req_test(*args, **kwargs) -> float:
            return [*args] + [kwargs.get("one", None), kwargs.get("two", None)]

        result = req_test("start", "two", one=1, two=2)
        assert result[0] == "start"
        assert result[1] == "two"
        assert result[2] == 1
        assert result[3] == 2
        with self.assertRaises(ValueError):
            result = req_test("start", "two", two=2)


class TestClsRequiredDecorators(unittest.TestCase):
    def test_required_gen(self):
        class Foo:
            @RequireArgs("one", "two", ftype=DecFuncEnum.METHOD)
            def req_test(self, **kwargs) -> float:
                return (kwargs.get("one", None), kwargs.get("two", None))
        f = Foo()
        result = f.req_test(one=1, two=2)
        assert result[0] == 1
        assert result[1] == 2
        result = f.req_test(two="b", one="a")
        assert result[0] == "a"
        assert result[1] == "b"
        with self.assertRaises(ValueError):
            result = f.req_test(one=1)
        with self.assertRaises(ValueError):
            result = f.req_test(two=2)

    def test_required_with_args(self):
        class Foo:
            @RequireArgs("one", "two", ftype=DecFuncEnum.METHOD)
            def req_test(self, first, second, **kwargs) -> float:
                return (first, second, kwargs.get("one", None), kwargs.get("two", None))
        f = Foo()
        result = f.req_test(first="start", second="", one=1, two=2)
        assert result[0] == "start"
        assert result[1] == ""
        assert result[2] == 1
        assert result[3] == 2

        with self.assertRaises(ValueError):
            result = f.req_test(first="start", second="", one=1)
        with self.assertRaises(ValueError):
            result = f.req_test(first="start", second="", two=2)

    def test_required_opt_args(self):
        class Foo:
            @RequireArgs("one", "two", ftype=DecFuncEnum.METHOD)
            def req_test(self, first, second="two", **kwargs) -> float:
                return (first, second, kwargs.get("one", None), kwargs.get("two", None))
        f = Foo()
        result = f.req_test(first="start", one=1, two=2)
        assert result[0] == "start"
        assert result[1] == "two"
        assert result[2] == 1
        assert result[3] == 2
        with self.assertRaises(ValueError):
            result = f.req_test(first="start", one=1)

    def test_required_args_kwargs(self):
        class Foo:
            @RequireArgs("one", "two", ftype=DecFuncEnum.METHOD)
            def req_test(self, *args, **kwargs) -> float:
                return [*args] + [kwargs.get("one", None), kwargs.get("two", None)]

        f = Foo()
        result = f.req_test("start", "two", one=1, two=2)
        assert result[0] == "start"
        assert result[1] == "two"
        assert result[2] == 1
        assert result[3] == 2
        with self.assertRaises(ValueError):
            result = f.req_test("start", "two", two=2)

    def test_static_required_args_kwargs(self):
        class Foo:
            @staticmethod
            @RequireArgs("one", "two", ftype=DecFuncEnum.METHOD_STATIC)
            def req_test(*args, **kwargs) -> float:
                return [*args] + [kwargs.get("one", None), kwargs.get("two", None)]

        result = Foo.req_test("start", "two", one=1, two=2)
        assert result[0] == "start"
        assert result[1] == "two"
        assert result[2] == 1
        assert result[3] == 2
        with self.assertRaises(ValueError):
            result = Foo.req_test("start", "two", two=2)


    def test_class_required_args_kwargs(self):
        class Foo:
            @classmethod
            @RequireArgs("one", "two", ftype=DecFuncEnum.METHOD_STATIC)
            def req_test(cls, *args, **kwargs) -> float:
                return [*args] + [kwargs.get("one", None), kwargs.get("two", None)]

        result = Foo.req_test("start", "two", one=1, two=2)
        assert result[0] == "start"
        assert result[1] == "two"
        assert result[2] == 1
        assert result[3] == 2
        with self.assertRaises(ValueError):
            result = Foo.req_test("start", "two", two=2)

if __name__ == '__main__':
    unittest.main()
