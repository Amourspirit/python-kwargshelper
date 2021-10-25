# coding: utf-8
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.checks import TypeChecker
from pathlib import Path
from kwhelp.decorator import TypeCheckerAny, TypeCheckerKw

class TestTypeChecker(unittest.TestCase):

    def test_main(self):
        tc = TypeChecker(types=[int, float])
        assert len(tc.types) == 2
        assert tc.validate(one=2, two=2.0) == True
        with self.assertRaises(TypeError):
            tc.validate(one=2, two="2")
        
        assert tc.validate(1, 3, 4.6, 5, 5.8) == True
        with self.assertRaises(TypeError):
            tc.validate(4.6, 5, 5.8, '')
            
    def test_types_none(self):
        tc = TypeChecker(types=None)
        # no checking takes place with types is None
        assert tc.validate(one=2, two=2.0) == True
        assert tc.validate(1, 3, 4.6, 5, 5.8) == True
        assert tc.validate(1, "a", int, self) == True

    def test_types_err(self):
        with self.assertRaises(TypeError):
            tc = TypeChecker(types=str)

    def test_no_err(self):
        tc = TypeChecker(types=[int, float], raise_error=False)
        assert tc.validate(one=2, two=2.0) == True
        assert tc.validate(one=2, two="2") == False
        assert tc.validate(4.6, 5, 5.8, '') == False
        tc.raise_error = True
        assert tc.raise_error == True
        with self.assertRaises(TypeError):
           tc.validate(4.6, 5, 5.8, '')

    def test_path(self):
        tc = TypeChecker(types=[str, Path], type_instance_check=True)
        assert tc.type_instance_check == True
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
        assert result == 22.3
        
        with self.assertRaises(TypeError):
            result = type_test(3, "")

    def test_type_checker_dec_type_err(self):
        with self.assertRaises(TypeError):
            @TypeCheckerAny(types=int)
            def type_test(one) -> float:
                return one


    def test_type_checker_args_dec(self):

        @TypeCheckerAny(types=[float, int], raise_error=True)
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
    
    def test_type_checker_args_dec_no_err(self):

        @TypeCheckerAny(types=[float, int], raise_error=False)
        def type_test(*args) -> float:
            sum = 0.0
            for arg in args:
                sum += float(arg)
            return sum

        result = type_test(10, 12.3, 33, 22, 44)
        # assert type_test.is_types_valid == True
        assert result == 121.3
        assert type_test.is_types_valid == True
        with self.assertRaises(ValueError):
            result = type_test(3, 4, 5.5, 7, "")
        assert type_test.is_types_valid == False
    
    def test_kw_type_checker_dec(self):
        @TypeCheckerKw(arg_info={"one":0, "two": 0},types=[(int,float)])
        def type_test(one, two) -> float:
            return float(one) + float(two)
    
        result = type_test(10, 12.3)
        assert result == 22.3
        
        with self.assertRaises(TypeError):
            type_test(19, "one")
        with self.assertRaises(TypeError):
            type_test(two=19, one="one")
    
    def test_kw_type_checker_dec_types_type(self):
        @TypeCheckerKw(arg_info={"one":0, "two": 1},types=[int, float])
        def type_test(one, two) -> float:
            return float(one) + float(two)
    
        result = type_test(10, 12.3)
        assert result == 22.3
        
        with self.assertRaises(TypeError):
            type_test(19, 10)
        with self.assertRaises(TypeError):
            type_test(two=19.2, one=1.2)
    
    def test_kw_type_checker_dec_no_type(self):
        @TypeCheckerKw(arg_info={"one":int, "two": [float]})
        def type_test(one, two) -> float:
            return float(one) + float(two)
    
        result = type_test(10, 12.3)
        assert result == 22.3
        
        with self.assertRaises(TypeError):
            type_test(19, 10)
        with self.assertRaises(TypeError):
            type_test(two=19.2, one=1.2)
    
    
    def test_kw_type_checker_dec_arg_index_three_list(self):
        @TypeCheckerKw(arg_info={"one":0, "two": 0, "three": [int]},types=[(int,float)])
        def type_test(one, two, three) -> float:
            return float(one) + float(two) + float(three)
    
        result = type_test(10, 12.3, 1)
        assert result == 23.3
        
        with self.assertRaises(TypeError):
            type_test(19, 1, 3.4)
        with self.assertRaises(TypeError):
            type_test(two=19, one=2.2, three="2")
    
    def test_kw_type_checker_dec_arg_index_type(self):
        @TypeCheckerKw(arg_info={"one": 0, "two": 0, "three": int}, types=[(int, float)])
        def type_test(one, two, three) -> float:
            return float(one) + float(two) + float(three)

        result = type_test(10, 12.3, 1)
        assert result == 23.3

        with self.assertRaises(TypeError):
            type_test(19, 1, 3.4)
        with self.assertRaises(TypeError):
            type_test(two=19, one=2.2, three="2")


    def test_kw_type_checker_dec_no_error(self):
        @TypeCheckerKw(arg_info={"one": 0, "two": 0}, types=[(int, float)], raise_error=False)
        def type_test(one, two) -> float:
            return float(one) + float(two)

        result = type_test(10, 12.3)
        assert result == 22.3
        try:
            result = type_test(19, "one")
        except ValueError:
            assert type_test.is_types_kw_valid == False
        result = type_test(two=23.4, one=10)
        assert result == 33.4
        assert type_test.is_types_kw_valid == True

    def test_kw_type_checker_dec_empty_type(self):
        @TypeCheckerKw(arg_info={"one": 0}, types=[[]])
        def type_test(one, two) -> float:
            return float(one) + float(two)

        result = type_test(10, 12.3)
        assert result == 22.3

    def test_speed_msg(self):

        @TypeCheckerKw(arg_info={"speed": 0, "limit": 0, "hours": 0, "name": 1},
                    types=[(int, float), str])
        def speed_msg(speed, limit, **kwargs) -> str:
            name = kwargs.get('name', 'You')
            if limit > speed:
                msg = f"Current speed is '{speed}'. {name} may go faster as the limit is '{limit}'."
            elif speed == limit:
                msg = f"Current speed is '{speed}'. {name} are at the limit."
            else:
                msg = f"Please slow down limit is '{limit}' and current speed is '{speed}'."
            if 'hours' in kwargs:
                msg = msg + f" Current driving hours is '{kwargs['hours']}'."
            return msg
    
        result = speed_msg(speed=45, limit=60)
        assert result == "Current speed is '45'. You may go faster as the limit is '60'."
        result = speed_msg(speed=45, limit=60, name="John")
        assert result == "Current speed is '45'. John may go faster as the limit is '60'."
        with self.assertRaises(TypeError):
            result = speed_msg(speed=-2, limit=60, name=17, hours=5)

if __name__ == '__main__':
    unittest.main()
