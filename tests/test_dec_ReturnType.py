import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.decorator import AcceptedTypes, DecFuncEnum, ReturnType
from enum import IntEnum, auto
from tests.ex_logger import test_logger, clear_log, get_logged_errors


class Color(IntEnum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

    def __str__(self) -> str:
        return self._name_

class TestReturnTypesDecorators(unittest.TestCase):
    def test_return_gen(self):
        @ReturnType(int)
        def req_test(*arg):
            return sum(arg)

        result = req_test(2, 4)
        assert result == 6
        result = req_test(-2, -10)
        assert result == - 12
        with self.assertRaises(TypeError):
            result = req_test(2, 2.5)

    def test_return_opt_return(self):
        @ReturnType(int, opt_return=None)
        def req_test(*arg):
            return sum(arg)

        result = req_test(2, 4)
        assert result == 6
        result = req_test(-2, -10)
        assert result == - 12
        result = False
        result = req_test(2, 2.5)
        assert result == None

    def test_return_enum(self):

        @ReturnType(Color)
        def req_test(c):
            return c

        result = req_test(Color.GREEN)
        assert result == Color.GREEN
        # with self.assertRaises(TypeError):
        #     result = req_test(2, 2.5)

    def test_return_multi(self):

        @ReturnType(int, float, type_instance_check=False)
        def req_test(arg):
            return arg

        result = req_test(2)
        assert result == 2
        result = req_test(-2.5)
        assert result == -2.5
        with self.assertRaises(TypeError):
            result = req_test("Hello")
        with self.assertRaises(TypeError):
            result = req_test(self)

    
    def test_return_none(self):
        @ReturnType(type(None))
        def req_test(arg):
            return arg

        result = req_test(arg=None)
        assert result is None
        with self.assertRaises(TypeError):
            result = req_test(arg=self)

class TestReturnTypesClsDecorators(unittest.TestCase):

    def test_return_gen(self):
        class T:
            @ReturnType(int)
            def req_test(self, *arg) -> float:
                return sum(arg)
        t = T()
        
        result = t.req_test(2, 4)
        assert result == 6
        result = t.req_test(-2, -10)
        assert result == - 12
        with self.assertRaises(TypeError):
            result = t.req_test(2, 2.5)

    def test_return_opt_return(self):
        class T:
            @ReturnType(int, opt_return=None)
            def req_test(self, *arg) -> float:
                return sum(arg)
        t = T()

        result = t.req_test(2, 4)
        assert result == 6
        result = t.req_test(-2, -10)
        assert result == - 12
        result = False
        result = t.req_test(2, 2.5)
        assert result == None

    def test_return_multi(self):
        class T:
            @ReturnType(int, float)
            def req_test(self, arg) -> float:
                return arg
        t = T()
        result = t.req_test(2)
        assert result == 2
        result = t.req_test(-2.5)
        assert result == -2.5
        with self.assertRaises(TypeError):
            result = t.req_test("Hello")
        with self.assertRaises(TypeError):
            result = t.req_test(self)


    def test_return_property(self):
        class T:
            @AcceptedTypes((int, float), ftype=DecFuncEnum.METHOD)
            def __init__(self, tmp):
               self._tmp = tmp
            
            @property
            @ReturnType(int)
            def tmp(self):
                return self._tmp
    
            @tmp.setter
            @AcceptedTypes((int, float), ftype=DecFuncEnum.PROPERTY_CLASS)
            def tmp(self, value):
                self._tmp = value
        t = T(2)
        assert t.tmp == 2
        t.tmp = 5
        assert t.tmp == 5
        t.tmp = 2.5
        # t.tmp accepsts int or float when setting but only int as return
        with self.assertRaises(TypeError):
            result = t.tmp


class TestReturnTypesDecoratorsLogger(unittest.TestCase):
    def setUp(self):
        clear_log()

    def tearDown(self):
        pass

    def test_return_gen(self):
        @ReturnType(int, opt_logger=test_logger)
        def req_test(*arg):
            return sum(arg)
        with self.assertRaises(TypeError):
            result = req_test(2, 2.5)
        errors = get_logged_errors()
        assert len(errors) == 1

    def test_return_multi(self):

        @ReturnType(int, float, type_instance_check=False, opt_logger=test_logger)
        def req_test(arg):
            return arg
        with self.assertRaises(TypeError):
            req_test("Hello")
        with self.assertRaises(TypeError):
            req_test(self)
        errors = get_logged_errors()
        assert len(errors) == 2

    def test_return_none(self):
        @ReturnType(type(None), opt_logger=test_logger)
        def req_test(arg):
            return arg
        with self.assertRaises(TypeError):
            result = req_test(arg=self)
        errors = get_logged_errors()
        assert len(errors) == 1

if __name__ == '__main__':
    unittest.main()
