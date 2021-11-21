from typing import Optional
import unittest
from collections import namedtuple
from enum import IntEnum, auto
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import ArgsMinMax, DecFuncEnum
from tests.ex_logger import test_logger, clear_log, get_logged_errors
from tests.ex_log_adapter import LogIndentAdapter

class Color(IntEnum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

    def __str__(self) -> str:
        return self._name_


RangeTuple = namedtuple('RangeTuple', ['start', 'end'])

def gen_args(length:int) -> list:
    return [i for i in range(length)]

class TestArgsMinMax(unittest.TestCase):
    def test_gen_args(self):
        args = gen_args(3)
        assert args[0] == 0
        assert args[1] == 1
        assert args[2] == 2


    def test_gen(self):
        @ArgsMinMax(min=3, max=4)
        def foo(*args):
            return len(args)
        result = foo(*gen_args(3))
        assert result == 3
        result = foo(*gen_args(4))
        assert result == 4
        with self.assertRaises(ValueError):
            result = foo()
        with self.assertRaises(ValueError):
            foo("a", "b")
        with self.assertRaises(ValueError):
            foo("a")
        with self.assertRaises(ValueError):
            foo(*gen_args(5))

    def test_no_max(self):
        @ArgsMinMax(min=3)
        def foo(*args):
            return len(args)
        result = foo(*gen_args(3))
        assert result == 3
        result = foo(*gen_args(25))
        assert result == 25
        with self.assertRaises(ValueError):
            result = foo()
        with self.assertRaises(ValueError):
            foo("a", "b")
        with self.assertRaises(ValueError):
            foo("a")


    def test_opt_return(self):
        @ArgsMinMax(min=3, max=4, opt_return=None)
        def foo(*args):
            return len(args)
        result = foo(*gen_args(3))
        assert result == 3
        result = True
        result = foo()
        assert result == None
        result = True
        result = foo(*gen_args(2))
        assert result == None
        result = True
        result = foo(*gen_args(1))
        assert result == None
        result = True
        result = foo(*gen_args(5))
        assert result == None

    def test_enum(self):
        @ArgsMinMax(max=2)
        def foo(*args):
            return len(args)
        result = foo()
        assert result == 0
        result = foo(Color.RED, Color.BLUE)
        assert result == 2
        with self.assertRaises(ValueError):
            foo(Color.RED, Color.BLUE, Color.GREEN)

    def test_tuple(self):
        @ArgsMinMax(min=3)
        def foo(*args):
            return len(args)
        result = foo(("a", 1), ("b", 2), ("c", 3))
        assert result == 3
        with self.assertRaises(ValueError):
            result = foo()
        with self.assertRaises(ValueError):
            foo(*gen_args(2))
        with self.assertRaises(ValueError):
            foo(*gen_args(1))

    def test_name_tuple(self):
        @ArgsMinMax(min=2, max=2)
        def foo(*args):
            return len(args)
        result = foo(RangeTuple(0, 2), (2, 4))
        assert result == 2

    def test_int_range_kwargs(self):
        @ArgsMinMax(min=2, max=7)
        def foo(*args, **kwargs):
            return len(args), len(kwargs)
        result = foo("a", "b")
        assert result[0] == 2
        result = foo(*gen_args(2), a=1, b=2)
        assert result[0] == 2
        result = foo(*gen_args(5))
        assert result[0] == 5
        result = foo(*gen_args(5), a=1, b=2)
        assert result[0] == 5
        result = foo(*gen_args(6))
        assert result[0] == 6
        result = foo(*gen_args(6), a=1, b=2)
        assert result[0] == 6
        result = foo(*gen_args(7))
        assert result[0] == 7
        result = foo(*gen_args(7), a=1, b=2)
        assert result[0] == 7
        with self.assertRaises(ValueError):
            foo()
        with self.assertRaises(ValueError):
            foo(a=1, b=2)
        with self.assertRaises(ValueError):
            foo(*gen_args(1))
        with self.assertRaises(ValueError):
            foo(*gen_args(1), a=1, b=2)
        with self.assertRaises(ValueError):
            foo(*gen_args(8))
        with self.assertRaises(ValueError):
            foo(*gen_args(8), a=1, b=2)

    def test_star_args_third(self):
        @ArgsMinMax(min=2, max=4)
        def foo(arg1, arg2, *args, a, b, **kwargs):
            return len(args), len(kwargs), (a, b), (arg1, arg2)
        result = foo(*gen_args(4), a=1, b=2, opt1="one", opt2="two")
        assert result[0] == 2
        result = foo(*gen_args(6), a=1, b=2, opt1="one", opt2="two")
        assert result[0] == 4
        with self.assertRaises(ValueError):
            foo(*gen_args(7), a=1, b=2, opt1="one", opt2="two")

    def test_return_gen(self):
        @ArgsMinMax(min=2, opt_return=False)
        def foo(*args):
            return [*args]
        result = foo()
        assert result == False

    def test_return_none(self):
        @ArgsMinMax(min=3, opt_return=None)
        def foo(*args):
            return [*args]
        result = foo()
        assert result == None


class TestArgsMinMaxClass(unittest.TestCase):
    def test_gen(self):
        class Bar:
            @ArgsMinMax(min=3, max=4, ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo(*gen_args(3))
        assert result == 3
        result = b.foo(*gen_args(4))
        assert result == 4
        with self.assertRaises(ValueError):
            result = b.foo()
        with self.assertRaises(ValueError):
            b.foo("a", "b")
        with self.assertRaises(ValueError):
            b.foo("a")
        with self.assertRaises(ValueError):
            b.foo(*gen_args(5))

    def test_no_max(self):
        class Bar:
            @ArgsMinMax(min=3, ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo(*gen_args(3))
        assert result == 3
        result = b.foo(*gen_args(25))
        assert result == 25
        with self.assertRaises(ValueError):
            result = b.foo()
        with self.assertRaises(ValueError):
            b.foo("a", "b")
        with self.assertRaises(ValueError):
            b.foo("a")

    def test_opt_return(self):
        class Bar:
            @ArgsMinMax(min=3, max=4, opt_return=None, ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo(*gen_args(3))
        assert result == 3
        result = True
        result = b.foo()
        assert result == None
        result = True
        result = b.foo(*gen_args(2))
        assert result == None
        result = True
        result = b.foo(*gen_args(1))
        assert result == None
        result = True
        result = b.foo(*gen_args(5))
        assert result == None

    def test_enum(self):
        class Bar:
            @ArgsMinMax(max=2, ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo()
        assert result == 0
        result = b.foo(Color.RED, Color.BLUE)
        assert result == 2
        with self.assertRaises(ValueError):
            b.foo(Color.RED, Color.BLUE, Color.GREEN)

    def test_tuple(self):
        class Bar:
            @ArgsMinMax(min=3, ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo(("a", 1), ("b", 2), ("c", 3))
        assert result == 3
        with self.assertRaises(ValueError):
            result = b.foo()
        with self.assertRaises(ValueError):
            b.foo(*gen_args(2))
        with self.assertRaises(ValueError):
            b.foo(*gen_args(1))

    def test_name_tuple(self):
        class Bar:
            @ArgsMinMax(min=2, max=2, ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return len(args)
        b = Bar()
        result = b.foo(RangeTuple(0, 2), (2, 4))
        assert result == 2

    def test_int_range_kwargs(self):
        class Bar:
            @ArgsMinMax(min=2, max=7, ftype=DecFuncEnum.METHOD)
            def foo(self, *args, **kwargs):
                return len(args), len(kwargs)
        b = Bar()
        result = b.foo("a", "b")
        assert result[0] == 2
        result = b.foo(*gen_args(2), a=1, b=2)
        assert result[0] == 2
        result = b.foo(*gen_args(5))
        assert result[0] == 5
        result = b.foo(*gen_args(5), a=1, b=2)
        assert result[0] == 5
        result = b.foo(*gen_args(6))
        assert result[0] == 6
        result = b.foo(*gen_args(6), a=1, b=2)
        assert result[0] == 6
        result = b.foo(*gen_args(7))
        assert result[0] == 7
        result = b.foo(*gen_args(7), a=1, b=2)
        assert result[0] == 7
        with self.assertRaises(ValueError):
            b.foo()
        with self.assertRaises(ValueError):
            b.foo(a=1, b=2)
        with self.assertRaises(ValueError):
            b.foo(*gen_args(1))
        with self.assertRaises(ValueError):
            b.foo(*gen_args(1), a=1, b=2)
        with self.assertRaises(ValueError):
            b.foo(*gen_args(8))
        with self.assertRaises(ValueError):
            b.foo(*gen_args(8), a=1, b=2)

    def test_star_args_third(self):
        class Bar:
            @ArgsMinMax(min=2, max=4, ftype=DecFuncEnum.METHOD)
            def foo(self, arg1, arg2, *args, a, b, **kwargs):
                return len(args), len(kwargs), (a, b), (arg1, arg2)
        b = Bar()
        result = b.foo(*gen_args(4), a=1, b=2, opt1="one", opt2="two")
        assert result[0] == 2
        result = b.foo(*gen_args(6), a=1, b=2, opt1="one", opt2="two")
        assert result[0] == 4
        with self.assertRaises(ValueError):
            b.foo(*gen_args(7), a=1, b=2, opt1="one", opt2="two")

    def test_return_gen(self):
        class Bar:
            @ArgsMinMax(min=2, opt_return=False, ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return [*args]
        b = Bar()
        result = b.foo()
        assert result == False

    def test_return_none(self):
        class Bar:
            @ArgsMinMax(min=3, opt_return=None, ftype=DecFuncEnum.METHOD)
            def foo(self, *args):
                return [*args]
        b = Bar()
        result = b.foo()
        assert result == None


class TestArgsMinMaxLogger(unittest.TestCase):
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

    def test_no_max(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt

            @ArgsMinMax(min=3, opt_logger=log)
            def foo(*args):
                return len(args)
            with self.assertRaises(ValueError):
                foo()
            with self.assertRaises(ValueError):
                foo("a", "b")
            with self.assertRaises(ValueError):
                foo("a")
            errors = get_logged_errors()
            assert len(errors) == 3

    def test_enum(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt

            @ArgsMinMax(max=2, opt_logger=log)
            def foo(*args):
                return len(args)
            with self.assertRaises(ValueError):
                foo(Color.RED, Color.BLUE, Color.GREEN)
            errors = get_logged_errors()
            assert len(errors) == 1

    def test_tuple(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @ArgsMinMax(min=3, opt_logger=log)
            def foo(*args):
                return len(args)
            with self.assertRaises(ValueError):
                result = foo()
            with self.assertRaises(ValueError):
                foo(*gen_args(2))
            with self.assertRaises(ValueError):
                foo(*gen_args(1))
            errors = get_logged_errors()
            assert len(errors) == 3

    def test_int_range_kwargs(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @ArgsMinMax(min=2, max=7, opt_logger=log)
            def foo(*args, **kwargs):
                return len(args), len(kwargs)
            with self.assertRaises(ValueError):
                foo()
            with self.assertRaises(ValueError):
                foo(a=1, b=2)
            with self.assertRaises(ValueError):
                foo(*gen_args(1))
            with self.assertRaises(ValueError):
                foo(*gen_args(1), a=1, b=2)
            with self.assertRaises(ValueError):
                foo(*gen_args(8))
            with self.assertRaises(ValueError):
                foo(*gen_args(8), a=1, b=2)
            errors = get_logged_errors()
            assert len(errors) == 6

    def test_star_args_third(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @ArgsMinMax(min=2, max=4, opt_logger=log)
            def foo(arg1, arg2, *args, a, b, **kwargs):
                return len(args), len(kwargs), (a, b), (arg1, arg2)
            with self.assertRaises(ValueError):
                foo(*gen_args(7), a=1, b=2, opt1="one", opt2="two")
            errors = get_logged_errors()
            assert len(errors) == 1



if __name__ == '__main__':
    unittest.main()
