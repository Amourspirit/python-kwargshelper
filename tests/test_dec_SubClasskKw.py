from enum import IntEnum
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import DecFuncEnum, SubClasskKw, TypeCheck, ReturnType
from tests.ex_logger import test_logger, clear_log, get_logged_errors
from tests.ex_log_adapter import LogIndentAdapter

class Color(IntEnum):
    RED = 1
    GREEN = 2
    BLUE = 3

    def __str__(self) -> str:
        return self._name_


class TestSubClasskKw(unittest.TestCase):
    def test_type_checkkw_gen(self):
        @SubClasskKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": 1},
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
        @SubClasskKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": 1},
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
        @SubClasskKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": str},
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
        @SubClasskKw(arg_info={"first": int, "last": int, "hours": float, "name": str})
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

    def test_kw_type_checker_dec_arg_index_three_list(self):

        @SubClasskKw(arg_info={"one": 0, "two": 0, "three": [int]}, types=[(int, float)])
        def type_test(one, two, three) -> float:
            return float(one) + float(two) + float(three)

        result = type_test(10, 12.3, 1)
        assert result == 23.3

        with self.assertRaises(TypeError):
            type_test(19, 1, 3.4)
        with self.assertRaises(TypeError):
            type_test(two=19, one=2.2, three="2")

    def test_kw_type_checker_dec_empty_type(self):
        @SubClasskKw(arg_info={"one": 0}, types=[[]])
        def type_test(one, two) -> float:
            return float(one) + float(two)

        result = type_test(10, 12.3)
        assert result == 22.3


class TestSubClasskKwClass(unittest.TestCase):
    def test_type_checkkw_gen(self):
        class Bar:
            def __init__(self):
                self._test = 0

            @SubClasskKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": 1},
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

            @SubClasskKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": 1},
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
            @SubClasskKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": str},
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
            @SubClasskKw(arg_info={"first": int, "last": int, "hours": float, "name": str},
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


class TestSubClasskKwLogger(unittest.TestCase):
    # region setup/teardown
    @classmethod
    def setUpClass(cls):
        cls.log_adapt = LogIndentAdapter(test_logger, {})
        cls.logger = test_logger

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass
    # endregion setup/teardown

    def test_type_checkkw_gen(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @SubClasskKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": 1},
                        types=[(int, float), str], opt_logger=log)
            def foo(first, last, **kwargs):
                pass
            with self.assertRaises(TypeError):
                foo(first="First", last=100, hours=12.5, name="test")
            with self.assertRaises(TypeError):
                foo(first=1, last="100", hours=12.5, name="test")
            with self.assertRaises(TypeError):
                foo(first=1, last=100, hours="2", name="test")
            with self.assertRaises(TypeError):
                foo(first=1, last=100, hours=12.5, name=7)
            errors = get_logged_errors()
            assert len(errors) == 4

    def test_type_checkkw_mix(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @SubClasskKw(arg_info={"first": 0, "last": 0, "hours": 0, "name": str},
                        types=[(int, float)], opt_logger=log)
            def foo(first, last, **kwargs):
                pass
            with self.assertRaises(TypeError):
                foo(first="First", last=100, hours=12.5, name="test")
            with self.assertRaises(TypeError):
                foo(first=1, last="100", hours=12.5, name="test")
            with self.assertRaises(TypeError):
                foo(first=1, last=100, hours="2", name="test")
            with self.assertRaises(TypeError):
                foo(first=1, last=100, hours=12.5, name=7)
            errors = get_logged_errors()
            assert len(errors) == 4

    def test_type_checkkw_arg_info(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @SubClasskKw(arg_info={"first": int, "last": int, "hours": float, "name": str}, opt_logger=log)
            def foo(first, last, **kwargs):
                pass
            with self.assertRaises(TypeError):
                foo(first="First", last=100, hours=12.5, name="test")
            with self.assertRaises(TypeError):
                foo(first=1, last="100", hours=12.5, name="test")
            with self.assertRaises(TypeError):
                foo(first=1, last=100, hours="2", name="test")
            with self.assertRaises(TypeError):
                foo(first=1, last=100, hours=12.5, name=7)
            errors = get_logged_errors()
            assert len(errors) == 4

    def test_kw_type_checker_dec_arg_index_three_list(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @SubClasskKw(arg_info={"one": 0, "two": 0, "three": [int]}, types=[(int, float)], opt_logger=log)
            def type_test(one, two, three) -> float:
                pass
            with self.assertRaises(TypeError):
                type_test(19, 1, 3.4)
            with self.assertRaises(TypeError):
                type_test(two=19, one=2.2, three="2")
            errors = get_logged_errors()
            assert len(errors) == 2


if __name__ == '__main__':
    unittest.main()
