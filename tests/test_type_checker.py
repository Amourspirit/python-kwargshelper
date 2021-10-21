# coding: utf-8
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.helper import TypeChecker
from pathlib import Path
from kwhelp.decorator import TypeCheckerAny, TypeCheckerKw

class TestTypeChecker(unittest.TestCase):

    def test_main(self):
        tc = TypeChecker(types=[int, float])
        assert tc.validate(one=2, two=2.0) == True
        with self.assertRaises(TypeError):
            tc.validate(one=2, two="2")
        
        assert tc.validate(1, 3, 4.6, 5, 5.8) == True
        with self.assertRaises(TypeError):
            tc.validate(4.6, 5, 5.8, '')

    def test_path(self):
        tc = TypeChecker(types=[str, Path])
        str_path = "/home/user"
        assert tc.validate(str_path=str_path, p=Path(str_path)) == True
        tc.type_instance_check = False
        with self.assertRaises(TypeError):
            tc.validate(str_path=str_path, p=Path(str_path))
        tc.type_instance_check = True
        assert tc.validate(str_path=str_path, p=Path(str_path)) == True
        assert tc.validate(str_path, Path(str_path),str_path=str_path, p=Path(str_path)) == True
        tc.type_instance_check = False
        with self.assertRaises(TypeError):
            tc.validate(str_path, Path(str_path))


class TestTypeDecorators(unittest.TestCase):

    def test_type_checker_dec(self):

        @TypeCheckerAny(types=[float, int])
        def type_test(one, two) -> float:
            return float(one) + float(two)

        result = type_test(10, 12.3)
        assert type_test.is_types_valid == True
        assert result == 22.3
        
        with self.assertRaises(TypeError):
            result = type_test(3, "")
    
    def test_type_checker_args_dec(self):

        @TypeCheckerAny(types=[float, int])
        def type_test(*args) -> float:
            sum = 0.0
            for arg in args:
                sum += float(arg)
            return sum

        result = type_test(10, 12.3, 33, 22, 44)
        # assert type_test.is_types_valid == True
        assert result == 121.3
        
        with self.assertRaises(TypeError):
            result = type_test(3, 4, 5.5, 7, "")
    
    def test_kw_type_checker_dec(self):
        @TypeCheckerKw(arg_index={"one":0, "two": 0},types=[(int,float)])
        def type_test(one, two) -> float:
            return float(one) + float(two)
    
        result = type_test(10, 12.3)
        assert result == 22.3
        
        with self.assertRaises(TypeError):
            type_test(19, "one")
        with self.assertRaises(TypeError):
            type_test(Two=19, one="one")

    def test_kw_type_checker_dec_no_error(self):
        @TypeCheckerKw(arg_index={"one": 0, "two": 0}, types=[(int, float)], raise_error=False)
        def type_test(one, two) -> float:
            return float(one) + float(two)

        result = type_test(10, 12.3)
        assert result == 22.3
        try:
            result = type_test(19, "one")
        except ValueError:
            assert type_test.is_types_valid == False
        result = type_test(two=23.4, one=10)
        assert result == 33.4
        assert type_test.is_types_valid == True


if __name__ == '__main__':
    unittest.main()
