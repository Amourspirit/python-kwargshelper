import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from enum import IntEnum, auto
from kwhelp.decorator import AcceptedTypes, DecFuncEnum, DecArgEnum, RequireArgs, ReturnType
from tests.ex_logger import test_logger, clear_log, get_logged_errors
from tests.ex_log_adapter import LogIndentAdapter

def gen_int_float(length: int) -> list:
    r = []
    for i in range(length):
        if (i % 3) == 0:
            r.append(i + 0.3)
            continue
        if (i % 2) == 0:  # even
            r.append(i)
            continue
        r.append(i + 0.7)
    return r


def gen_args(length: int) -> list:
    return [i for i in range(length)]

class Color(IntEnum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

    def __str__(self) -> str:
        return self._name_


class TestAcceptedTypesDecorators(unittest.TestCase):
    def test_gen_args(self):
        args = gen_args(3)
        assert args[0] == 0
        assert args[1] == 1
        assert args[2] == 2

    def test_gen_int_float(self):
        ex = [0.3, 1.7, 2, 3.3, 4, 5.7, 6.3, 7.7, 8, 9.3, 10,
              11.7, 12.3, 13.7, 14, 15.3, 16, 17.7, 18.3, 19.7]
        result = gen_int_float(20)
        for i, num in enumerate(ex):
            assert result[i] == num

    def test_accepted_gen(self):
        @AcceptedTypes((int, str), (int, str))
        def req_test(**kwargs):
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

    def test_accepted_all_args(self):
        @AcceptedTypes((float, int), opt_all_args=True)
        def sum_num(*args):
            return sum(args)

        args = gen_int_float(20)
        result = sum_num(*args)
        assert result == 197.0
        args.append("33")
        with self.assertRaises(TypeError):
            sum_num(*args)
        with self.assertRaises(TypeError):
            sum_num(self)

    def test_accepted_all_args_opt_return(self):
        @AcceptedTypes((float, int), opt_all_args=True, opt_return=False)
        def sum_num(*args):
            return sum(args)

        args = gen_int_float(20)
        result = sum_num(*args)
        assert result == 197.0
        args.append("33")
        result = None
        result = sum_num(*args)
        assert result == False
        result = None
        result = sum_num(self)
        assert result == False

    def test_accepted_opt_return(self):
        @AcceptedTypes((int, str), (int, str), opt_return=False)
        def req_test(**kwargs):
            return (kwargs.get("one"), kwargs.get("two"))

        result = req_test(one=1, two=2)
        assert result[0] == 1
        assert result[1] == 2
        result = req_test(two="b", one="a")
        assert result[0] == "a"
        assert result[1] == "b"
        result = req_test(one=1)
        assert result == False
        result = True
        result = req_test(two=2)
        assert result == False
        result = True
        result = req_test(one=4.5, two=2)
        assert result == False

    def test_accepted_opt_return_args(self):
        @AcceptedTypes((int, str), (int, str), opt_return=False)
        def req_test(*args):
            return [*args]
        result = req_test(1, 2)
        assert result[0] == 1
        assert result[1] == 2
        result = req_test("a", "b")
        assert result[0] == "a"
        assert result[1] == "b"
        result = req_test(1)
        assert result == False
        result = True
        result = req_test(4.5, 2)
        assert result == False

    def test_accepted_optional_args(self):

        @AcceptedTypes((int, str), (int, str), int)
        def req_test(first, second=2, third=3):
            return (first, second, third)

        result = req_test(4, 5, 6)
        assert result[0] == 4
        assert result[1] == 5
        assert result[2] == 6
        result = req_test(first="one")
        assert result[0] == "one"
        assert result[1] == 2
        assert result[2] == 3
        result = req_test("one")
        assert result[0] == "one"
        assert result[1] == 2
        assert result[2] == 3
        result = req_test(11, 12)
        assert result[0] == 11
        assert result[1] == 12
        assert result[2] == 3
        result = req_test(first=1, third=33)
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == 33
        with self.assertRaises(TypeError):
            result = req_test(first=33.44)
        with self.assertRaises(TypeError):
            result = req_test(33.44)
        with self.assertRaises(TypeError):
            result = req_test(5, 6, "7")
        with self.assertRaises(TypeError):
            result = req_test(first=5, third="7")

    def test_accepted_args_optional_named(self):
        @AcceptedTypes(int, int, int, (int, str), (int, str), int)
        def req_test(*args, first, second=2, third=3):
            return [*args] + [first, second, third]
        result = req_test(1, 2, 3, first=4, second=5, third=6)
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == 3
        assert result[3] == 4
        assert result[4] == 5
        assert result[5] == 6
        result = req_test(1, 2, 3, first=77)
        assert result[3] == 77
        assert result[4] == 2
        assert result[5] == 3
        result = req_test(1, 2, 3, first="one", third=55)
        assert result[3] == "one"
        assert result[4] == 2
        assert result[5] == 55
        with self.assertRaises(TypeError):
            req_test(1, 2.2, 3, first=77)
        with self.assertRaises(TypeError):
            req_test(1, 2, 3, first=77, third="yes")

    def test_accept_args_and_kwargs(self):
        @AcceptedTypes(str, str, (int, str), (int, str))
        def req_test(*args, **kwargs):
            return (*args, kwargs.get("one", None), kwargs.get("two", None))
        result = req_test("start", "", one=1, two=2)
        assert result[0] == "start"
        assert result[1] == ""
        assert result[2] == 1
        assert result[3] == 2
        with self.assertRaises(TypeError):
            req_test("start", "", one=1, two=2.5)
        with self.assertRaises(TypeError):
            req_test("start", 3, one=1, two=2)

    def test_accept_required_with_args(self):

        @RequireArgs("one", "two")
        @AcceptedTypes(str, str, (int, str), (int, str))
        def req_test(first, second, **kwargs):
            return (first, second, kwargs.get("one", None), kwargs.get("two", None))

        result = req_test(first="start", second="", one=1, two=2)
        assert result[0] == "start"
        assert result[1] == ""
        assert result[2] == 1
        assert result[3] == 2

        with self.assertRaises(ValueError):
            req_test(first="start", second="", one=1)
        with self.assertRaises(ValueError):
            req_test(first="start", second="", two=2)
        with self.assertRaises(TypeError):
            req_test(first="start", second="", one=1, two=2.5)

    def test_enum(self):
        # enum are iterable so [*Color] is list comperhension.
        # and becomes [<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]
        # for this reason when passing enum types they must be in an itterable
        # such as a list or tuple
        @AcceptedTypes(Color, int, Color)
        def foo(e, length, oth):
            return e, length, oth
        result = foo(Color.BLUE, 2, Color.RED)
        assert result[0] == Color.BLUE
        assert result[1] == 2
        assert result[2] == Color.RED
        with self.assertRaises(TypeError):
            result = foo(1, 2, Color.RED)

    def test_enum_int(self):
        # enum are iterable so [*Color] is list comperhension.
        # and becomes [<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]
        # for this reason when passing enum types they must be in an itterable
        # such as a list or tuple
        @AcceptedTypes([Color, int])
        def foo(e):
            if isinstance(e, int):
                result = Color(e)
            else:
                result = e
            return result
        result = foo(Color.BLUE)
        assert result == Color.BLUE
        result = foo(e=2)
        assert result == Color.GREEN

    def test_star_args_pos3_mix(self):
        # Positional argument cannot appear after keyword arguments
        # however positional arg can come after keword arguments if keyword argumnets are filled out
        # as positional args.
        # myfunc(1.33, "two", 3, Color.BLUE, 5) is allow
        # myfunc(arg1=1.33, arg2="two", 3, Color.BLUE, 5,  kwonlyarg=True) not allowed
        # result = myfunc(3, Color.BLUE, 5, arg1=1.33, arg2="two", kwonlyarg=True) not allowed

        @AcceptedTypes(float, str, int, [Color], int, bool)
        def myfunc(arg1, arg2, *args, kwonlyarg=True):
            return [arg1, arg2] + [*args] + [kwonlyarg]
        result = myfunc(1.33, "two", 3, Color.BLUE, 5)
        assert result[0] == 1.33
        assert result[1] == "two"
        assert result[2] == 3
        assert result[3] == Color.BLUE
        assert result[4] == 5
        assert result[5] == True
        result = myfunc(1.33, "two", 3, Color.RED, 5, kwonlyarg=False)
        assert result[0] == 1.33
        assert result[1] == "two"
        assert result[2] == 3
        assert result[3] == Color.RED
        assert result[4] == 5
        assert result[5] == False
        with self.assertRaises(TypeError):
            myfunc(1.33, "two", 3, Color.BLUE, 5, kwonlyarg=22)
        with self.assertRaises(TypeError):
            myfunc(1, "two", 3, Color.BLUE, 5)
        with self.assertRaises(TypeError):
            myfunc(1.33, 2, 3, Color.BLUE, 5)
        with self.assertRaises(TypeError):
            myfunc(1.33, "two", "three", Color.BLUE, 5)
        with self.assertRaises(TypeError):
            myfunc(1.33, "two", 3, 22, 5)
        with self.assertRaises(TypeError):
            myfunc(1.33, "two", 3, Color.BLUE, 5.5)


class TestAcceptedTypesClassDecorators(unittest.TestCase):

    def test_accept_class(self):
        class Foo:
            @AcceptedTypes((int, float), (int, float), ftype=DecFuncEnum.METHOD)
            def __init__(self, start, stop):
                self.start = start
                self.stop = stop
        f = Foo(1, 99.9)
        assert f.start == 1
        assert f.stop == 99.9
        f = Foo(start=1, stop=99.9)
        assert f.start == 1
        assert f.stop == 99.9
        with self.assertRaises(TypeError):
            f = Foo("yes", 99.9)

    def test_accept_class_args(self):
        class Foo:
            @AcceptedTypes((int, float), (int, float), ftype=DecFuncEnum.METHOD)
            def __init__(self, *args):
                self.start = args[0]
                self.stop = args[1]
        f = Foo(1, 99.9)
        assert f.start == 1
        assert f.stop == 99.9
        with self.assertRaises(TypeError):
            f = Foo("yes", 99.9)

    def test_accepted_all_args(self):
        class Runner:
            @AcceptedTypes((float, int), opt_all_args=True, ftype=DecFuncEnum.METHOD)
            def sum_num(self, *args):
                return sum(args)
        r = Runner()
        args = gen_int_float(20)
        result = r.sum_num(*args)
        assert result == 197.0
        args.append("33")
        with self.assertRaises(TypeError):
            r.sum_num(*args)
        with self.assertRaises(TypeError):
            r.sum_num(self)

    def test_accepted_all_args_opt_return(self):
        class Runner:
            @AcceptedTypes((float, int), opt_all_args=True,
                           opt_return=False,
                           ftype=DecFuncEnum.METHOD)
            def sum_num(self, *args):
                return sum(args)
        r = Runner()
        args = gen_int_float(20)
        result = r.sum_num(*args)
        assert result == 197.0
        args.append("33")
        result = None
        result = r.sum_num(*args)
        assert result == False
        result = None
        result = r.sum_num(self)
        assert result == False

    def test_accept_class_args_optional(self):
        class Foo:
            @AcceptedTypes((int, float), (int, float), int, int, ftype=DecFuncEnum.METHOD)
            def __init__(self, *args, third, fourth=4):
                self.start = args[0]
                self.stop = args[1]
                self.third = third
                self.fourth = fourth
        f = Foo(1, 99.9, third=3, fourth=44)
        assert f.start == 1
        assert f.stop == 99.9
        assert f.third == 3
        assert f.fourth == 44
        f = Foo(1, 99.9, third=3)
        assert f.start == 1
        assert f.stop == 99.9
        assert f.third == 3
        assert f.fourth == 4
        with self.assertRaises(TypeError):
            f = Foo("yes", 99.9, third=3, fourth=44)
        with self.assertRaises(TypeError):
            f = Foo(1, 99.9, third=3.5)

    def test_accept_class_args_optional_kwargs(self):
        class Foo:
            @AcceptedTypes((int, float), (int, float), int, int, int, int, ftype=DecFuncEnum.METHOD)
            def __init__(self, *args, third, fourth=4, **kwargs):
                self.start = args[0]
                self.stop = args[1]
                self.third = third
                self.fourth = fourth
                self.fifth = kwargs.get("fifth", None)
                self.sixth = kwargs.get("sixth", None)
        f = Foo(1, 99.9, third=3, fourth=44, fifth=5, sixth=6)
        assert f.start == 1
        assert f.stop == 99.9
        assert f.third == 3
        assert f.fourth == 44
        assert f.fifth == 5
        assert f.sixth == 6
        f = Foo(1, 99.9, third=3, fifth=5, sixth=6)
        assert f.start == 1
        assert f.stop == 99.9
        assert f.third == 3
        assert f.fourth == 4
        assert f.fifth == 5
        assert f.sixth == 6
        with self.assertRaises(TypeError):
            f = Foo(1, 99.9, third=3, fourth=44, fifth=5, sixth=55.77)

    def test_accept_class_args_kwargs_opt_all(self):
        class Foo:
            @AcceptedTypes((int, float), (int, float), int, ftype=DecFuncEnum.METHOD, opt_all_args=True)
            def __init__(self, *args, **kwargs):
                self.start = args[0]
                self.stop = args[1]
                self.third = kwargs.get("third", None)
                self.fourth = kwargs.get("fourth", None)
                self.fifth = kwargs.get("fifth", None)
                self.sixth = kwargs.get("sixth", None)
        f = Foo(1, 99.9, third=3, fourth=44, fifth=5, sixth=6)
        assert f.start == 1
        assert f.stop == 99.9
        assert f.third == 3
        assert f.fourth == 44
        assert f.fifth == 5
        assert f.sixth == 6
        with self.assertRaises(TypeError):
            f = Foo(1, 99.9, third=3, fourth=44, fifth=5, sixth=6.76)
        with self.assertRaises(TypeError):
            f = Foo("", 99.9, third=3, fourth=44, fifth=5, sixth=6)

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

    def test_accept_class_property(self):
        class Foo:
            @AcceptedTypes((int, float), (int, float), ftype=DecFuncEnum.METHOD)
            def __init__(self, start, stop):
                self._start = start
                self._stop = stop

            @property
            def start(self):
                return self._start

            @start.setter
            @AcceptedTypes((int, float), ftype=DecFuncEnum.PROPERTY_CLASS)
            def start(self, value):
                self._start = value

            @property
            def stop(self):
                return self._stop

            @stop.setter
            @AcceptedTypes((int, float), ftype=DecFuncEnum.PROPERTY_CLASS)
            def stop(self, value):
                self._stop = value

        f = Foo(1, 99.9)
        assert f.start == 1
        assert f.stop == 99.9
        f.start = 101.22
        assert f.start == 101.22
        with self.assertRaises(TypeError):
            f.stop = "False"
        with self.assertRaises(TypeError):
            f.start = self

    def test_enum(self):
        # enum are iterable so [*Color] is list comperhension.
        # and becomes [<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]
        # for this reason when passing enum types they must be in an itterable
        # such as a list or tuple
        class Bar:
            @AcceptedTypes([Color], int, [Color], ftype=DecFuncEnum.PROPERTY_CLASS)
            def foo(self, e, length, oth):
                return e, length, oth
        b = Bar()
        result = b.foo(Color.BLUE, 2, Color.RED)
        assert result[0] == Color.BLUE
        assert result[1] == 2
        assert result[2] == Color.RED
        with self.assertRaises(TypeError):
            result = b.foo(1, 2, Color.RED)

    def test_star_args_pos3_mix(self):
        # Positional argument cannot appear after keyword arguments
        # however positional arg can come after keword arguments if keyword argumnets are filled out
        # as positional args.
        # myfunc(1.33, "two", 3, Color.BLUE, 5) is allow
        # myfunc(arg1=1.33, arg2="two", 3, Color.BLUE, 5,  kwonlyarg=True) not allowed
        # result = myfunc(3, Color.BLUE, 5, arg1=1.33, arg2="two", kwonlyarg=True) not allowed
        class Bar:
            @AcceptedTypes(float, str, int, [Color], int, bool, ftype=DecFuncEnum.METHOD)
            def myfunc(self, arg1, arg2, *args, kwonlyarg=True):
                return [arg1, arg2] + [*args] + [kwonlyarg]
        b = Bar()
        result = b.myfunc(1.33, "two", 3, Color.BLUE, 5)
        assert result[0] == 1.33
        assert result[1] == "two"
        assert result[2] == 3
        assert result[3] == Color.BLUE
        assert result[4] == 5
        assert result[5] == True
        result = b.myfunc(1.33, "two", 3, Color.RED, 5, kwonlyarg=False)
        assert result[0] == 1.33
        assert result[1] == "two"
        assert result[2] == 3
        assert result[3] == Color.RED
        assert result[4] == 5
        assert result[5] == False
        with self.assertRaises(TypeError):
            b.myfunc(1.33, "two", 3, Color.BLUE, 5, kwonlyarg=3)
        with self.assertRaises(TypeError):
            b.myfunc(1, "two", 3, Color.BLUE, 5)
        with self.assertRaises(TypeError):
            b.myfunc(1.33, 2, 3, Color.BLUE, 5)
        with self.assertRaises(TypeError):
            b.myfunc(1.33, "two", "three", Color.BLUE, 5)
        with self.assertRaises(TypeError):
            b.myfunc(1.33, "two", 3, 22, 5)
        with self.assertRaises(TypeError):
            b.myfunc(1.33, "two", 3, Color.BLUE, 5.5)

    def test_accepted_opt_return(self):
        class Bar:
            @AcceptedTypes((int, str), (int, str), opt_return=False, ftype=DecFuncEnum.METHOD)
            def req_test(self, **kwargs):
                return (kwargs.get("one"), kwargs.get("two"))
        b = Bar()
        result = b.req_test(one=1, two=2)
        assert result[0] == 1
        assert result[1] == 2
        result = b.req_test(two="b", one="a")
        assert result[0] == "a"
        assert result[1] == "b"
        result = b.req_test(one=1)
        assert result == False
        result = b.req_test(two=2)
        assert result == False
        result = b.req_test(one=4.5, two=2)
        assert result == False

class TestAcceptedTypesClassFilter(unittest.TestCase):
   
    def test_opt_args_only(self):
        # opt_args_only: only test *args
        @AcceptedTypes(int, int, int, opt_args_filter=DecArgEnum.ARGS)
        def foo(*args, first, second, **kwargs):
            result = [*args]
            result = result + [first, second]
            result = result + [v for _, v in kwargs.items()]
            return result
        args_len = 3
        args_lst = [*gen_args(args_len)]
        result = foo(*args_lst, first='1st', second='2nd', one='1', two='2')
        assert result[0] == 0
        args_len = 4
        args_lst = [*gen_args(args_len)]
        with self.assertRaises(ValueError):
            foo(*args_lst, first='1st', second='2nd', one='1', two='2')

    def test_opt_all_args_opt_args_only(self):
        # opt_all_args then the last subclass type passed into constructor will validate all others
        # opt_args_only: only *args are validated
        @AcceptedTypes(int, opt_args_filter=DecArgEnum.ARGS, opt_all_args=True)
        def foo(*args, first, second, **kwargs):
            result = [*args]
            result = result + [first, second]
            result = result + [v for _, v in kwargs.items()]
            return result
        args_len = 22
        args_lst = [*gen_args(args_len)]
        result = foo(*args_lst, first='1st', second='2nd', one='1', two='2')
        assert result[0] == 0
        assert len(result) == 26
        
    def test_opt_kwarg_only(self):
        # opt_kwarg_only: only **kwargs are validated
        @AcceptedTypes(str, str, opt_args_filter=DecArgEnum.KWARGS)
        def foo(*args, first, second, **kwargs):
            result = [*args]
            result = result + [first, second]
            result = result + [v for _, v in kwargs.items()]
            return result
        args_len = 3
        args_lst = [*gen_args(args_len)]
        result = foo(*args_lst, first='1st', second='2nd', one='1', two='2')
        assert result[0] == 0
        with self.assertRaises(TypeError):
            foo(*args_lst, first='1st', second='2nd', one=1, two='2')


class TestAcceptedTypesDecoratorsLog(unittest.TestCase):
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

    def test_accepted_gen(self):
    
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @AcceptedTypes((int, str), (int, str), opt_logger=log)
            def req_test(**kwargs):
                pass

            with self.assertRaises(ValueError):
                req_test(one=1)
            with self.assertRaises(ValueError):
                req_test(two=2)
            with self.assertRaises(TypeError):
                req_test(one=4.5, two=2)
            errors = get_logged_errors()
            assert len(errors) == 3

    def test_accepted_all_args(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @AcceptedTypes((float, int), opt_all_args=True, opt_logger=log)
            def sum_num(*args):
                return sum(args)

            args = gen_int_float(20)
            result = sum_num(*args)
            assert result == 197.0
            args.append("33")
            with self.assertRaises(TypeError):
                sum_num(*args)
            with self.assertRaises(TypeError):
                sum_num(self)
            errors = get_logged_errors()
            assert len(errors) == 2

    def test_accepted_optional_args(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @AcceptedTypes((int, str), (int, str), int, opt_logger=log)
            def req_test(first, second=2, third=3):
                return (first, second, third)

            with self.assertRaises(TypeError):
                req_test(first=33.44)
            with self.assertRaises(TypeError):
                req_test(33.44)
            with self.assertRaises(TypeError):
                req_test(5, 6, "7")
            with self.assertRaises(TypeError):
                req_test(first=5, third="7")
            errors = get_logged_errors()
            assert len(errors) == 4

    def test_accepted_args_optional_named(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @AcceptedTypes(int, int, int, (int, str), (int, str), int, opt_logger=log)
            def req_test(*args, first, second=2, third=3):
                pass
            with self.assertRaises(TypeError):
                req_test(1, 2.2, 3, first=77)
            with self.assertRaises(TypeError):
                req_test(1, 2, 3, first=77, third="yes")
            errors = get_logged_errors()
            assert len(errors) == 2

    def test_accept_args_and_kwargs(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @AcceptedTypes(str, str, (int, str), (int, str), opt_logger=log)
            def req_test(*args, **kwargs):
                return (*args, kwargs.get("one", None), kwargs.get("two", None))
            with self.assertRaises(TypeError):
                req_test("start", "", one=1, two=2.5)
            with self.assertRaises(TypeError):
                req_test("start", 3, one=1, two=2)
            errors = get_logged_errors()
            assert len(errors) == 2

    def test_accept_required_with_args(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @RequireArgs("one", "two", opt_logger=log)
            @AcceptedTypes(str, str, (int, str), (int, str), opt_logger=log)
            def req_test(first, second, **kwargs):
                pass

            with self.assertRaises(ValueError):
                req_test(first="start", second="", one=1)
            with self.assertRaises(ValueError):
                req_test(first="start", second="", two=2)
            with self.assertRaises(TypeError):
                req_test(first="start", second="", one=1, two=2.5)
            errors = get_logged_errors()
            assert len(errors) == 3

    def test_star_args_pos3_mix(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @AcceptedTypes(float, str, int, [Color], int, bool, opt_logger=log)
            def myfunc(arg1, arg2, *args, kwonlyarg=True):
                pass
            with self.assertRaises(TypeError):
                myfunc(1.33, "two", 3, Color.BLUE, 5, kwonlyarg=22)
            with self.assertRaises(TypeError):
                myfunc(1, "two", 3, Color.BLUE, 5)
            with self.assertRaises(TypeError):
                myfunc(1.33, 2, 3, Color.BLUE, 5)
            with self.assertRaises(TypeError):
                myfunc(1.33, "two", "three", Color.BLUE, 5)
            with self.assertRaises(TypeError):
                myfunc(1.33, "two", 3, 22, 5)
            with self.assertRaises(TypeError):
                myfunc(1.33, "two", 3, Color.BLUE, 5.5)
            errors = get_logged_errors()
            assert len(errors) == 6

if __name__ == '__main__':
    unittest.main()
