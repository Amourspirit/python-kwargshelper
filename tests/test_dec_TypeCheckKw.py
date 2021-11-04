from enum import IntEnum
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import DecFuncEnum, TypeCheckKw, TypeCheck, ReturnType


class Color(IntEnum):
    RED = 1
    GREEN = 2
    BLUE = 3

    def __str__(self) -> str:
        return self._name_


class TestTypeCheckKw(unittest.TestCase):
    def test_type_checkkw_gen(self):
        @TypeCheckKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": 1},
                   types=[(int, float), str])
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        result = foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        with self.assertRaises(TypeError):
            foo(first="First", last=100, hours=12.5, name="test")
        with self.assertRaises(TypeError):
            foo(first=1, last="100", hours=12.5, name="test")
        with self.assertRaises(TypeError):
            foo(first=1, last=100, hours="2", name="test")
        with self.assertRaises(TypeError):
            foo(first=1, last=100, hours=12.5, name=7)

    def test_type_checkkw_opt_return(self):
        @TypeCheckKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": 1},
                     types=[(int, float), str], opt_return=None)
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        result = foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        result = False
        result = foo(first="First", last=100, hours=12.5, name="test")
        assert result == None
        result = False
        result = foo(first=1, last="100", hours=12.5, name="test")
        assert result == None
        result = False
        result = foo(first=1, last=100, hours="2", name="test")
        assert result == None
        result = False
        result = foo(first=1, last=100, hours=12.5, name=7)
        assert result == None

    def test_type_checkkw_mix(self):
        @TypeCheckKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": str},
                     types=[(int, float)])
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        result = foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        with self.assertRaises(TypeError):
            foo(first="First", last=100, hours=12.5, name="test")
        with self.assertRaises(TypeError):
            foo(first=1, last="100", hours=12.5, name="test")
        with self.assertRaises(TypeError):
            foo(first=1, last=100, hours="2", name="test")
        with self.assertRaises(TypeError):
            foo(first=1, last=100, hours=12.5, name=7)

    def test_type_checkkw_arg_info(self):
        @TypeCheckKw(arg_info={"first": int, "last": int, "hours": float, "name": str})
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        result = foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        with self.assertRaises(TypeError):
            foo(first="First", last=100, hours=12.5, name="test")
        with self.assertRaises(TypeError):
            foo(first=1, last="100", hours=12.5, name="test")
        with self.assertRaises(TypeError):
            foo(first=1, last=100, hours="2", name="test")
        with self.assertRaises(TypeError):
            foo(first=1, last=100, hours=12.5, name=7)

    def test_type_checkkw_raise_error_opt_return(self):
        @TypeCheckKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": 1},
                     types=[(int, float), str], raise_error=False, opt_return=None)
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        assert foo.is_types_kw_valid == True
        result = foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        assert foo.is_types_kw_valid == True
        result = False
        result = foo(first="First", last=100, hours=12.5, name="test")
        assert result == None
        assert foo.is_types_kw_valid == False
        result = False
        result = foo(first=1, last="100", hours=12.5, name="test")
        assert result == None
        assert foo.is_types_kw_valid == False
        result = False
        result = foo(first=1, last=100, hours="2", name="test")
        assert result == None
        assert foo.is_types_kw_valid == False
        result = False
        result = foo(first=1, last=100, hours=12.5, name=7)
        assert result == None

class TestTypeCheckKwClass(unittest.TestCase):
    def test_type_checkkw_gen(self):
        class Bar:
            def __init__(self):
                self._test = 0

            @TypeCheckKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": 1},
                        types=[(int, float), str], ftype=DecFuncEnum.METHOD)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d
            @property
            @ReturnType(int, ftype=DecFuncEnum.PROPERTY_CLASS)
            def test(self):
                return self._test

            @test.setter
            @TypeCheck(int, ftype=DecFuncEnum.PROPERTY_CLASS)
            def test(self, value):
                self._test = value
        b = Bar()
        result = b.foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        assert b.test == 0
        b.test = 22
        assert b.test == 22
        with self.assertRaises(TypeError):
            b.foo(first="First", last=100, hours=12.5, name="test")
        with self.assertRaises(TypeError):
            b.foo(first=1, last="100", hours=12.5, name="test")
        with self.assertRaises(TypeError):
            b.foo(first=1, last=100, hours="2", name="test")
        with self.assertRaises(TypeError):
            b.foo(first=1, last=100, hours=12.5, name=7)
        with self.assertRaises(TypeError):
            b.test = 22.4
        with self.assertRaises(TypeError):
            b._test = 44.6
            result = b.test

    def test_type_checkkw_opt_return(self):
        class Bar:
            def __init__(self):
                self._test = 0

            @TypeCheckKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": 1},
                         types=[(int, float), str], ftype=DecFuncEnum.METHOD,
                         opt_return=None)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d

            @property
            @ReturnType(int, ftype=DecFuncEnum.PROPERTY_CLASS, opt_return=None)
            def test(self):
                return self._test

            @test.setter
            @TypeCheck(int, ftype=DecFuncEnum.PROPERTY_CLASS)
            def test(self, value):
                self._test = value
        b = Bar()
        result = b.foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        result = False
        result = b.foo(first="First", last=100, hours=12.5, name="test")
        assert result == None
        result = False
        result = b.foo(first=1, last="100", hours=12.5, name="test")
        assert result == None
        result = False
        result = b.foo(first=1, last=100, hours="2", name="test")
        assert result == None
        result = False
        result = b.foo(first=1, last=100, hours=12.5, name=7)
        assert result == None
        result = False
        b._test = 22.4
        result = b.test
        assert result == None

    def test_type_checkkw_mix(self):
        class Bar:
            @TypeCheckKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": str},
                         types=[(int, float)], ftype=DecFuncEnum.METHOD)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d
        b = Bar()
        result = b.foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        with self.assertRaises(TypeError):
            b.foo(first="First", last=100, hours=12.5, name="test")
        with self.assertRaises(TypeError):
            b.foo(first=1, last="100", hours=12.5, name="test")
        with self.assertRaises(TypeError):
            b.foo(first=1, last=100, hours="2", name="test")
        with self.assertRaises(TypeError):
            b.foo(first=1, last=100, hours=12.5, name=7)

    def test_type_checkkw_arg_info(self):
        class Bar:
            @TypeCheckKw(arg_info={"first": int, "last": int, "hours": float, "name": str},
                        ftype=DecFuncEnum.METHOD)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d
        b = Bar()
        result = b.foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        with self.assertRaises(TypeError):
            b.foo(first="First", last=100, hours=12.5, name="test")
        with self.assertRaises(TypeError):
            b.foo(first=1, last="100", hours=12.5, name="test")
        with self.assertRaises(TypeError):
            b.foo(first=1, last=100, hours="2", name="test")
        with self.assertRaises(TypeError):
            b.foo(first=1, last=100, hours=12.5, name=7)

if __name__ == '__main__':
    unittest.main()
