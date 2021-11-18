from enum import IntEnum
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import DecArgEnum, DecFuncEnum, TypeCheck, ArgsLen
from tests.ex_logger import test_logger, clear_log, get_logged_errors

class Color(IntEnum):
    RED = 1
    GREEN = 2
    BLUE = 3

    def __str__(self) -> str:
        return self._name_


class TestTypeCheck(unittest.TestCase):
    def test_type_check_gen(self):
        @TypeCheck(int, float)
        def add_numbers(*args) -> float:
            result = 0.0
            for arg in args:
                result += float(arg)
            return result

        result = add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        with self.assertRaises(TypeError):
            add_numbers(2, 1.2, "4")

    def test_type_check__opt_args_filter_kwargs(self):
        @TypeCheck(int, float, opt_args_filter=DecArgEnum.KWARGS)
        def foo(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]

        result = foo(1, 2, 3, first="start", last="!",
                     one=1, two=2.2, three=-23.4)
        assert result[0] == 1
        with self.assertRaises(TypeError):
            result = foo(1, 2, 3, first="start", last="!",
                         one=1, two=2.2, three="")

    def test_type_check__opt_args_filter_args(self):
        @TypeCheck(int, float, opt_args_filter=DecArgEnum.ARGS)
        def foo(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]

        result = foo(1, 2, 3.5, first="start", last="!",
                     one="1st", two="2nd", three="3rd")
        assert result[0] == 1
        with self.assertRaises(TypeError):
            foo(1, '2', 3.5, first="start", last="!",
                one="1st", two="2nd", three="3rd")

    def test_type_check__opt_args_filter_named_args(self):
        @TypeCheck(int, float, opt_args_filter=DecArgEnum.NAMED_ARGS)
        def foo(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]

        result = foo("a", "b", "c", first=1, last=-2.2,
                     one="1st", two="2nd", three="3rd")
        assert result[0] == "a"
        with self.assertRaises(TypeError):
            foo("a", "b", "c", first=1, last="!",
               one="1st", two="2nd", three="3rd")

    def test_type_check__opt_args_filter_no_args(self):
        @TypeCheck(int, float, opt_args_filter=DecArgEnum.NO_ARGS)
        def foo(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]

        result = foo("a", "b", "c", first=1, last=-2.2,
                     one=-12, two=22.34, three=33)
        assert result[0] == "a"
        with self.assertRaises(TypeError):
            foo("a", "b", "c", first=1, last="!",
                     one=-12, two=22.34, three=33)
        with self.assertRaises(TypeError):
            foo("a", "b", "c", first=1, last=-2.2,
                     one=-12, two="2nd", three=33)

    def test_type_check_enum(self):
        @TypeCheck(Color)
        def add_color(*args) -> float:
            result = 0.0
            for arg in args:
                result += arg.value
            return result

        result = add_color(Color.RED, Color.BLUE, Color.GREEN)
        assert result == 6
        with self.assertRaises(TypeError):
            add_color(2)

    def test_type_check_opt_return(self):
        @TypeCheck(int, float, opt_return=None)
        def add_numbers(*args) -> float:
            result = 0.0
            for arg in args:
                result += float(arg)
            return result

        result = add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        result = add_numbers(2, 1.2, "4")
        assert result == None

    def test_type_check_args_len_opt_return(self):
        # test different return for differten decorators
        @TypeCheck(int, float, opt_return=None)
        @ArgsLen(5, opt_return=False)
        def add_numbers(*args) -> float:
            result = 0.0
            for arg in args:
                result += float(arg)
            return result

        result = add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        result = add_numbers(2, 1.2, "4")
        assert result == None
        result = add_numbers(2, 1.2)
        assert result == False

    def test_type_check_raise_error(self):
        @TypeCheck(int, float, raise_error=False)
        def add_numbers(*args) -> float:
            result = 0.0
            for arg in args:
                result += float(arg)
            return result
        assert add_numbers.is_types_valid == True
        result = add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        assert add_numbers.is_types_valid == True
        result = add_numbers(2, 1.2, "4")
        assert add_numbers.is_types_valid == False

    def test_type_check_raise_error_opt_return(self):
        @TypeCheck(int, float, raise_error=False, opt_return=None)
        def add_numbers(*args) -> float:
            result = 0.0
            for arg in args:
                result += float(arg)
            return result
        assert add_numbers.is_types_valid == True
        result = add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        assert add_numbers.is_types_valid == True
        result = add_numbers(2, 1.2, "4")
        assert add_numbers.is_types_valid == False
        assert result == None

        result = add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        assert add_numbers.is_types_valid == True


class TestTypeCheckClass(unittest.TestCase):
    def test_type_check_gen(self):
        class Foo:
            @TypeCheck(int, float, ftype=DecFuncEnum.METHOD)
            def add_numbers(self, *args) -> float:
                result = 0.0
                for arg in args:
                    result += float(arg)
                return result
        f = Foo()
        result = f.add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        with self.assertRaises(TypeError):
            f.add_numbers(2, 1.2, "4")

    def test_type_check_enum(self):
        class Foo:
            @TypeCheck(Color, ftype=DecFuncEnum.METHOD)
            def add_color(self, *args) -> float:
                result = 0.0
                for arg in args:
                    result += arg.value
                return result
        f = Foo()
        result = f.add_color(Color.RED, Color.BLUE, Color.GREEN)
        assert result == 6
        with self.assertRaises(TypeError):
            f.add_color(2)

    def test_type_check_opt_return(self):
        class Foo:
            @TypeCheck(int, float, opt_return=None, ftype=DecFuncEnum.METHOD)
            def add_numbers(self, *args) -> float:
                result = 0.0
                for arg in args:
                    result += float(arg)
                return result
        f = Foo()
        result = f.add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        result = f.add_numbers(2, 1.2, "4")
        assert result == None

    def test_type_check_args_len_opt_return(self):
        # test different return for differten decorators
        class Foo:
            @TypeCheck(int, float, opt_return=None, ftype=DecFuncEnum.METHOD)
            @ArgsLen(5, opt_return=False, ftype=DecFuncEnum.METHOD)
            def add_numbers(self, *args) -> float:
                result = 0.0
                for arg in args:
                    result += float(arg)
                return result
        f = Foo()
        result = f.add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        result = f.add_numbers(2, 1.2, "4")
        assert result == None
        result = f.add_numbers(2, 1.2)
        assert result == False

    def test_type_check_raise_error(self):
        class Foo:
            @TypeCheck(int, float, raise_error=False, ftype=DecFuncEnum.METHOD)
            def add_numbers(self, *args) -> float:
                result = 0.0
                for arg in args:
                    result += float(arg)
                return result
        f = Foo()
        assert f.add_numbers.is_types_valid == True
        result = f.add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        assert f.add_numbers.is_types_valid == True
        result = f.add_numbers(2, 1.2, "4")
        assert f.add_numbers.is_types_valid == False

    def test_type_check_raise_error_opt_return(self):
        class Foo:
            @TypeCheck(int, float, raise_error=False, opt_return=None, ftype=DecFuncEnum.METHOD)
            def add_numbers(self, *args) -> float:
                result = 0.0
                for arg in args:
                    result += float(arg)
                return result
        f = Foo()
        assert f.add_numbers.is_types_valid == True
        result = f.add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        assert f.add_numbers.is_types_valid == True
        result = f.add_numbers(2, 1.2, "4")
        assert f.add_numbers.is_types_valid == False
        assert result == None

        result = f.add_numbers(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        assert f.add_numbers.is_types_valid == True


class TestTypeCheckLogger(unittest.TestCase):
    def setUp(self):
        clear_log()

    def tearDown(self):
        pass

    def test_type_check_gen(self):
        @TypeCheck(int, float, opt_logger=test_logger)
        def add_numbers(*args) -> float:
            result = 0.0
            for arg in args:
                result += float(arg)
            return result
        with self.assertRaises(TypeError):
            add_numbers(2, 1.2, "4")
        with self.assertRaises(TypeError):
            add_numbers(2, 1.2, 4, self)
        errors = get_logged_errors()
        assert len(errors) == 2

    def test_type_check__opt_args_filter_args(self):
        @TypeCheck(int, float, opt_args_filter=DecArgEnum.ARGS, opt_logger=test_logger)
        def foo(*args, first, last, **kwargs):
            pass

        with self.assertRaises(TypeError):
            foo(1, '2', 3.5, first="start", last="!",
                one="1st", two="2nd", three="3rd")
        errors = get_logged_errors()
        assert len(errors) == 1

    def test_type_check__opt_args_filter_named_args(self):
        @TypeCheck(int, float, opt_args_filter=DecArgEnum.NAMED_ARGS, opt_logger=test_logger)
        def foo(*args, first, last, **kwargs):
            pass

        with self.assertRaises(TypeError):
            foo("a", "b", "c", first=1, last="!",
                one="1st", two="2nd", three="3rd")
        errors = get_logged_errors()
        assert len(errors) == 1

if __name__ == '__main__':
    unittest.main()
