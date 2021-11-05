from enum import IntEnum
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import DecFuncEnum, TypeCheck, ArgsLen


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


if __name__ == '__main__':
    unittest.main()
