from types import prepare_class
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from enum import IntEnum, auto
from kwhelp.decorator import DecArgEnum, SubClass, DecFuncEnum, RequireArgs, ReturnType
from tests.ex_logger import test_logger, clear_log, get_logged_errors

def gen_args(length: int) -> list:
    return [i for i in range(length)]


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


class Color(IntEnum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

    def __str__(self) -> str:
        return self._name_


class Base:
    def __repr__(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return self.__class__.__name__


class Foo(Base):
    pass


class Bar(Foo):
    pass


class FooBar(Bar):
    pass


class Obj:
    def __repr__(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return self.__class__.__name__


class ObjFoo(Obj):
    pass


class TestSubClassDecorators(unittest.TestCase):

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

    def test_subclass_gen(self):
        @SubClass((Foo, ObjFoo), Base)
        def req_test(**kwargs):
            return (kwargs.get("one"), kwargs.get("two"))

        result = req_test(one=Foo(), two=Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        # note the order here. two comes before one but
        # first is still two and second is one because it is being
        # argsuments are being passed to **kwargs
        result = req_test(two=ObjFoo(), one=FooBar())
        assert str(result[0]) == "FooBar"
        assert str(result[1]) == "ObjFoo"
        with self.assertRaises(ValueError):
            result = req_test(one=Foo())
        with self.assertRaises(ValueError):
            result = req_test(two=Bar())
        with self.assertRaises(TypeError):
            result = req_test(one=Obj(), two=Bar())
        with self.assertRaises(ValueError):
            # too many args
            result = req_test(one=Obj(), two=Bar(), three=Bar())

    def test_subclass_opt_args_filter_kwargs(self):
        @SubClass((Foo, ObjFoo), Base, opt_args_filter=DecArgEnum.KWARGS)
        def req_test(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]

        result = req_test(1, 2, 3, first="1st", last="!", one=Foo(), two=Bar())
        assert result[0] == 1
        with self.assertRaises(TypeError):
            req_test(1, 2, 3, first="1st",
                              last="!", one='one', two=Bar())
        with self.assertRaises(ValueError):
            # too many args
            req_test(1, 2, 3, first="1st", last="!", one=Foo(), two=Bar(), three=Foo())

    def test_subclass_opt_args_filter_args(self):
        @SubClass((Foo, ObjFoo), Base, opt_args_filter=DecArgEnum.ARGS)
        def req_test(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]

        result = req_test(Foo(), Bar(), first="1st", last="!", one=1, two=2)
        assert isinstance(result[0], Foo)
        with self.assertRaises(TypeError):
            req_test(Foo(), 1, first="1st", last="!", one=1, two=2)
        with self.assertRaises(ValueError):
            # too many args
           req_test(Foo(), Bar(), Foo(), first="1st", last="!", one=1, two=2)
    
    def test_subclass_opt_args_filter_named_args(self):
        @SubClass((Foo, ObjFoo), Base, opt_args_filter=DecArgEnum.NAMED_ARGS)
        def req_test(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]

        result = req_test(1, 2, 3, first=Foo(), last=Bar(), one=1, two=2)
        assert result[0] == 1
        with self.assertRaises(TypeError):
           req_test(1, 2, 3, first=Foo(), last=1, one=1, two=2)

    def test_subclass_opt_args_filter_no_args(self):
        @SubClass((Foo, ObjFoo), Base, Foo, Base, opt_args_filter=DecArgEnum.NO_ARGS)
        def req_test(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]

        result = req_test(1, 2, 3, first=Foo(), last=Bar(), one=Foo(), two=Bar())
        assert result[0] == 1
        with self.assertRaises(TypeError):
            req_test(1, 2, 3, first=Foo(), last=Bar(), one=Foo(), two=ObjFoo())
        with self.assertRaises(TypeError):
            req_test(1, 2, 3, first=Foo(), last=ObjFoo(), one=Foo(), two=Bar())
        with self.assertRaises(ValueError):
            # too many args
           req_test(1, 2, 3, first=Foo(), last=Bar(), one=Foo(), two=Bar(), three=Bar())

    def test_subclass_named_args(self):
        @SubClass((Foo, ObjFoo), Base)
        def req_test(one, two):
            return (one, two)

        result = req_test(one=Foo(), two=Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = req_test(two=FooBar(), one=ObjFoo())
        assert str(result[0]) == "ObjFoo"
        assert str(result[1]) == "FooBar"
        with self.assertRaises(TypeError):
            result = req_test(one=Foo())
        with self.assertRaises(TypeError):
            result = req_test(two=Bar())
        with self.assertRaises(TypeError):
            result = req_test(one=Obj(), two=Bar())
        with self.assertRaises(ValueError):
            result = req_test(one=Obj(), two=Bar(), three=Bar())

    def test_subclass_opt_all_args(self):
        @SubClass((float, int), opt_all_args=True)
        def sum_num(*args):
            return sum(args)

        args = gen_int_float(20)
        result = sum_num(*args)
        assert result == 197.0
        args.append(Foo())
        with self.assertRaises(TypeError):
            sum_num(*args)
        with self.assertRaises(TypeError):
            sum_num(self)

    def test_subclass_opt_all_args_opt_return(self):
        @SubClass((float, int), opt_all_args=True, opt_return=None)
        def sum_num(*args):
            return sum(args)

        args = gen_int_float(20)
        result = sum_num(*args)
        assert result == 197.0
        args.append(Foo())
        result = False
        result = sum_num(*args)
        assert result == None
        result = False
        result = sum_num(self)
        assert result == None

    def test_subclass_opt_all_args_multi(self):
        # first arg must be float, all othe must be int
        @SubClass(float, int, opt_all_args=True)
        def sum_num(*args):
            return sum(args)

        result = sum_num(1.2, 1)
        assert result == 2.2
        int_args = gen_args(20)
        args = [12.3] + int_args
        result = sum_num(*args)
        assert result == 202.3
        args.append(12.4)
        with self.assertRaises(TypeError):
            sum_num(*args)
        args = [12, 3, 2.1] + int_args
        with self.assertRaises(TypeError):
            sum_num(*args)
        with self.assertRaises(TypeError):
            sum_num(self)

    def test_subclass_instance_only_true(self):
        @SubClass((Foo, ObjFoo), Base, instance_only=True)
        def req_test(**kwargs):
            return (kwargs.get("one"), kwargs.get("two"))

        result = req_test(one=Foo(), two=Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = req_test(two=ObjFoo(), one=FooBar())
        assert str(result[0]) == "FooBar"
        assert str(result[1]) == "ObjFoo"
        with self.assertRaises(ValueError):
            result = req_test(one=Foo())
        with self.assertRaises(ValueError):
            result = req_test(two=Bar())
        with self.assertRaises(TypeError):
            result = req_test(one=Obj(), two=Bar())

    def test_subclass_instance_only_false(self):
        @SubClass((Foo, ObjFoo), Base, opt_inst_only=False)
        def req_test(**kwargs):
            return (kwargs.get("one"), kwargs.get("two"))

        result = req_test(one=Foo(), two=Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = req_test(two=ObjFoo(), one=FooBar())
        assert str(result[0]) == "FooBar"
        assert str(result[1]) == "ObjFoo"
        result = req_test(two=ObjFoo, one=FooBar)
        self.assertIs(result[0], FooBar)
        self.assertIs(result[1], ObjFoo)
        with self.assertRaises(ValueError):
            result = req_test(one=Foo)
        with self.assertRaises(ValueError):
            result = req_test(two=Bar)
        with self.assertRaises(TypeError):
            result = req_test(one=Obj(), two=Bar())

    def test_subclass_opt_return(self):
        @SubClass((Foo, ObjFoo), Base, opt_return=False)
        def req_test(**kwargs):
            return (kwargs.get("one"), kwargs.get("two"))

        result = req_test(one=Foo(), two=Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = req_test(two=ObjFoo(), one=FooBar())
        assert str(result[0]) == "FooBar"
        assert str(result[1]) == "ObjFoo"
        result == None
        result = req_test(one=1)
        assert result == False
        result == None
        result = req_test(two=2)
        assert result == False
        result == None
        result = req_test(one=Obj(), two=Bar())
        assert result == False

    def test_subclass_opt_return_args(self):
        @SubClass((Foo, ObjFoo), Base, opt_return=False)
        def req_test(*args):
            return [*args]
        result = req_test(Foo(), Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = req_test(ObjFoo(), FooBar())
        assert str(result[0]) == "ObjFoo"
        assert str(result[1]) == "FooBar"
        result == None
        result = req_test(1)
        assert result == False
        result == None
        result = req_test(2)
        assert result == False
        result == None
        result = req_test(Obj(), Bar())
        assert result == False
        result == None
        result = req_test(Obj(), Bar(), Foo())
        assert result == False

    def test_subclass_optional_args(self):
        @SubClass(Foo, FooBar, Obj)
        def req_test(first, second=FooBar(), third=Obj()):
            return (first, second, third)

        result = req_test(Foo(), FooBar(), ObjFoo())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "ObjFoo"
        result = req_test(first=Foo())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "Obj"
        result = req_test(Foo())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "Obj"
        result = req_test(Foo(), FooBar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "Obj"
        result = req_test(first=Foo(), third=ObjFoo())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "ObjFoo"

        with self.assertRaises(TypeError):
            result = req_test(first=Obj())
        with self.assertRaises(TypeError):
            result = req_test(Obj())
        with self.assertRaises(TypeError):
            result = req_test(Foo(), FooBar(), Foo())
        with self.assertRaises(TypeError):
            result = req_test(first=Foo(), third=Foo())

    def test_subclass_args_optional_named(self):
        @SubClass(Base, Base, Base, (Bar, Obj), (FooBar, Obj), Base)
        def req_test(*args, first, second=ObjFoo(), third=Bar()):
            return [*args] + [first, second, third]
        result = req_test(Foo(), Bar(), FooBar(),
                          first=ObjFoo(), second=Obj(), third=Foo())
        assert str(result[0]) == 'Foo'
        assert str(result[1]) == 'Bar'
        assert str(result[2]) == 'FooBar'
        assert str(result[3]) == 'ObjFoo'
        assert str(result[4]) == 'Obj'
        assert str(result[5]) == 'Foo'
        result = req_test(Foo(), Bar(), FooBar(), first=ObjFoo())
        assert str(result[0]) == 'Foo'
        assert str(result[1]) == 'Bar'
        assert str(result[2]) == 'FooBar'
        assert str(result[3]) == 'ObjFoo'
        assert str(result[4]) == 'ObjFoo'
        assert str(result[5]) == 'Bar'
        result = req_test(Foo(), Bar(), FooBar(),
                          first=ObjFoo(), third=Foo())
        assert str(result[0]) == 'Foo'
        assert str(result[1]) == 'Bar'
        assert str(result[2]) == 'FooBar'
        assert str(result[3]) == 'ObjFoo'
        assert str(result[4]) == 'ObjFoo'
        assert str(result[5]) == 'Foo'
        with self.assertRaises(TypeError):
            req_test(Foo(), Bar(), FooBar(), first=Base())
        with self.assertRaises(TypeError):
            req_test(Foo(), Bar(), FooBar(), first=ObjFoo(), third=Obj())

    def test_subclass_args_and_kwargs(self):
        @SubClass(Base, Base, (Foo, ObjFoo), (Bar, Obj))
        def req_test(*args, **kwargs):
            return (*args, kwargs.get("one", None), kwargs.get("two", None))
        result = req_test(Base(), FooBar(), one=ObjFoo(), two=Bar())
        assert str(result[0]) == "Base"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "ObjFoo"
        assert str(result[3]) == "Bar"
        with self.assertRaises(TypeError):
            req_test(Base(), FooBar(), one=ObjFoo(), two=Base())
        with self.assertRaises(TypeError):
            req_test(Base(), "", one=ObjFoo(), two=Bar())
        with self.assertRaises(ValueError):
            req_test(*gen_args(5))

    def test_accept_required_with_args(self):
        @RequireArgs("one", "two")
        @SubClass(Base, Base, (Foo, ObjFoo), (Bar, Obj))
        def req_test(*args, **kwargs):
            return (*args, kwargs.get("one", None), kwargs.get("two", None))
        result = req_test(Base(), FooBar(), one=ObjFoo(), two=Bar())
        assert str(result[0]) == "Base"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "ObjFoo"
        assert str(result[3]) == "Bar"
        with self.assertRaises(TypeError):
            req_test(Base(), FooBar(), one=ObjFoo(), two=Base())
        with self.assertRaises(TypeError):
            req_test(Base(), "", one=ObjFoo(), two=Bar())

    def test_enum(self):
        @SubClass(Color, Base, Color)
        def foo(one, two, three):
            return one, two, three
        result = foo(Color.BLUE, Foo(), Color.RED)
        assert result[0] == Color.BLUE
        assert str(result[1]) == "Foo"
        assert result[2] == Color.RED
        with self.assertRaises(TypeError):
            result = foo(1, Foo(), Color.RED)

    def test_enum_base(self):
        # enum are iterable so [*Color] is list comperhension.
        # and becomes [<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]
        # for this reason when passing enum types they must be in an itterable
        # such as a list or tuple
        @SubClass([Color, Base, int])
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
        result = foo(Bar())
        assert str(result) == "Bar"

    def test_star_args_pos3_mix(self):
        # Positional argument cannot appear after keyword arguments
        # however positional arg can come after keword arguments if keyword argumnets are filled out
        # as positional args.
        # myfunc(1.33, "two", 3, Color.BLUE, 5) is allow
        # myfunc(arg1=1.33, arg2="two", 3, Color.BLUE, 5,  kwonlyarg=True) not allowed
        # result = myfunc(3, Color.BLUE, 5, arg1=1.33, arg2="two", kwonlyarg=True) not allowed

        @SubClass(Bar, Base, Obj, [Color], Foo, ObjFoo)
        def myfunc(arg1, arg2, *args, last=ObjFoo()):
            return [arg1, arg2] + [*args] + [last]
        result = myfunc(Bar(), Base(), Obj(), Color.BLUE, FooBar())
        assert str(result[0]) == "Bar"
        assert str(result[1]) == "Base"
        assert str(result[2]) == "Obj"
        assert result[3] == Color.BLUE
        assert str(result[4]) == "FooBar"
        assert str(result[5]) == "ObjFoo"
        result = myfunc(Bar(), Base(), Obj(), Color.RED,
                        FooBar(), last=ObjFoo())
        assert str(result[0]) == "Bar"
        assert str(result[1]) == "Base"
        assert str(result[2]) == "Obj"
        assert result[3] == Color.RED
        assert str(result[4]) == "FooBar"
        assert str(result[5]) == "ObjFoo"
        with self.assertRaises(TypeError):
            myfunc(Bar(), Obj(), Obj(), Color.RED, FooBar(), last=ObjFoo())
        with self.assertRaises(TypeError):
            myfunc(Bar(), Base(), Obj(), Foo(), FooBar())
        with self.assertRaises(TypeError):
            myfunc(Foo(), Base(), Obj(), Color.BLUE, FooBar())
        with self.assertRaises(TypeError):
            myfunc(Bar(), Base(), Obj(), Color.RED, FooBar(), last=Color.BLUE)


class TestSubClassDecoratorsClass(unittest.TestCase):
    def test_subclass_gen(self):
        class Runner:
            @SubClass((Foo, ObjFoo), Base, ftype=DecFuncEnum.METHOD)
            def req_test(self, **kwargs):
                return (kwargs.get("one"), kwargs.get("two"))
        r = Runner()
        result = r.req_test(one=Foo(), two=Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = r.req_test(two=ObjFoo(), one=FooBar())
        assert str(result[0]) == "FooBar"
        assert str(result[1]) == "ObjFoo"
        with self.assertRaises(ValueError):
            result = r.req_test(one=Foo())
        with self.assertRaises(ValueError):
            result = r.req_test(two=Bar())
        with self.assertRaises(TypeError):
            result = r.req_test(one=Obj(), two=Bar())

    def test_subclass_opt_all_args(self):
        class Runner:
            @SubClass((float, int), opt_all_args=True, ftype=DecFuncEnum.METHOD)
            def sum_num(self, *args):
                return sum(args)
        r = Runner()
        args = gen_int_float(20)
        result = r.sum_num(*args)
        assert result == 197.0
        args.append(Foo())
        with self.assertRaises(TypeError):
            r.sum_num(*args)
        with self.assertRaises(TypeError):
            r.sum_num(self)

    def test_subclass_opt_all_args_multi(self):
        # first arg must be float, all othe must be int
        class Runner:
            @SubClass(float, int, opt_all_args=True, ftype=DecFuncEnum.METHOD)
            def sum_num(self, *args):
                return sum(args)

        r = Runner()
        result = r.sum_num(1.2, 1)
        assert result == 2.2
        int_args = gen_args(20)
        args = [12.3] + int_args
        result = r.sum_num(*args)
        assert result == 202.3
        args.append(12.4)
        with self.assertRaises(TypeError):
            r.sum_num(*args)
        args = [12, 3, 2.1] + int_args
        with self.assertRaises(TypeError):
            r.sum_num(*args)
        with self.assertRaises(TypeError):
            r.sum_num(self)

    def test_subclass_instance_only_true(self):
        class Runner:
            @SubClass((Foo, ObjFoo), Base, instance_only=True, ftype=DecFuncEnum.METHOD)
            def req_test(self, **kwargs):
                return (kwargs.get("one"), kwargs.get("two"))
        r = Runner()
        result = r.req_test(one=Foo(), two=Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = r.req_test(two=ObjFoo(), one=FooBar())
        assert str(result[0]) == "FooBar"
        assert str(result[1]) == "ObjFoo"
        with self.assertRaises(ValueError):
            result = r.req_test(one=Foo())
        with self.assertRaises(ValueError):
            result = r.req_test(two=Bar())
        with self.assertRaises(TypeError):
            result = r.req_test(one=Obj(), two=Bar())

    def test_subclass_instance_only_false(self):
        class Runner:
            @SubClass((Foo, ObjFoo), Base, opt_inst_only=False, ftype=DecFuncEnum.METHOD)
            def req_test(self, **kwargs):
                return (kwargs.get("one"), kwargs.get("two"))
        r = Runner()
        result = r.req_test(one=Foo(), two=Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = r.req_test(two=ObjFoo(), one=FooBar())
        assert str(result[0]) == "FooBar"
        assert str(result[1]) == "ObjFoo"
        result = r.req_test(two=ObjFoo, one=FooBar)
        self.assertIs(result[0], FooBar)
        self.assertIs(result[1], ObjFoo)
        with self.assertRaises(ValueError):
            result = r.req_test(one=Foo)
        with self.assertRaises(ValueError):
            result = r.req_test(two=Bar)
        with self.assertRaises(TypeError):
            result = r.req_test(one=Obj(), two=Bar())

    def test_subclass_opt_return(self):
        class Runner:
            @SubClass((Foo, ObjFoo), Base, opt_return=False, ftype=DecFuncEnum.METHOD)
            def req_test(self, **kwargs):
                return (kwargs.get("one"), kwargs.get("two"))
        r = Runner()
        result = r.req_test(one=Foo(), two=Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = r.req_test(two=ObjFoo(), one=FooBar())
        assert str(result[0]) == "FooBar"
        assert str(result[1]) == "ObjFoo"
        result == None
        result = r.req_test(one=1)
        assert result == False
        result == None
        result = r.req_test(two=2)
        assert result == False
        result == None
        result = r.req_test(one=Obj(), two=Bar())
        assert result == False

    def test_subclass_opt_return_args(self):
        class Runner:

            @SubClass((Foo, ObjFoo), Base, opt_return=False, ftype=DecFuncEnum.METHOD)
            def req_test(self, *args):
                return [*args]
        r = Runner()
        result = r.req_test(Foo(), Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = r.req_test(ObjFoo(), FooBar())
        assert str(result[0]) == "ObjFoo"
        assert str(result[1]) == "FooBar"
        result == None
        result = r.req_test(1)
        assert result == False
        result == None
        result = r.req_test(2)
        assert result == False
        result == None
        result = r.req_test(Obj(), Bar())
        assert result == False

    def test_subclass_optional_args(self):
        class Runner:
            @SubClass(Foo, FooBar, Obj, ftype=DecFuncEnum.METHOD)
            def req_test(self, first, second=FooBar(), third=Obj()):
                return (first, second, third)
        r = Runner()
        result = r.req_test(Foo(), FooBar(), ObjFoo())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "ObjFoo"
        result = r.req_test(first=Foo())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "Obj"
        result = r.req_test(Foo())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "Obj"
        result = r.req_test(Foo(), FooBar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "Obj"
        result = r.req_test(first=Foo(), third=ObjFoo())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "ObjFoo"

        with self.assertRaises(TypeError):
            result = r.req_test(first=Obj())
        with self.assertRaises(TypeError):
            result = r.req_test(Obj())
        with self.assertRaises(TypeError):
            result = r.req_test(Foo(), FooBar(), Foo())
        with self.assertRaises(TypeError):
            result = r.req_test(first=Foo(), third=Foo())

    def test_subclass_args_optional_named(self):
        class Runner:
            @SubClass(Base, Base, Base, (Bar, Obj), (FooBar, Obj), Base, ftype=DecFuncEnum.METHOD)
            def req_test(self, *args, first, second=ObjFoo(), third=Bar()):
                return [*args] + [first, second, third]
        r = Runner()
        result = r.req_test(Foo(), Bar(), FooBar(),
                            first=ObjFoo(), second=Obj(), third=Foo())
        assert str(result[0]) == 'Foo'
        assert str(result[1]) == 'Bar'
        assert str(result[2]) == 'FooBar'
        assert str(result[3]) == 'ObjFoo'
        assert str(result[4]) == 'Obj'
        assert str(result[5]) == 'Foo'
        result = r.req_test(Foo(), Bar(), FooBar(), first=ObjFoo())
        assert str(result[0]) == 'Foo'
        assert str(result[1]) == 'Bar'
        assert str(result[2]) == 'FooBar'
        assert str(result[3]) == 'ObjFoo'
        assert str(result[4]) == 'ObjFoo'
        assert str(result[5]) == 'Bar'
        result = r.req_test(Foo(), Bar(), FooBar(),
                            first=ObjFoo(), third=Foo())
        assert str(result[0]) == 'Foo'
        assert str(result[1]) == 'Bar'
        assert str(result[2]) == 'FooBar'
        assert str(result[3]) == 'ObjFoo'
        assert str(result[4]) == 'ObjFoo'
        assert str(result[5]) == 'Foo'
        with self.assertRaises(TypeError):
            r.req_test(Foo(), Bar(), FooBar(), first=Base())
        with self.assertRaises(TypeError):
            r.req_test(Foo(), Bar(), FooBar(), first=ObjFoo(), third=Obj())

    def test_subclass_args_and_kwargs(self):
        class Runner:
            @SubClass(Base, Base, (Foo, ObjFoo), (Bar, Obj), ftype=DecFuncEnum.METHOD)
            def req_test(self, *args, **kwargs):
                return (*args, kwargs.get("one", None), kwargs.get("two", None))
        r = Runner()
        result = r.req_test(Base(), FooBar(), one=ObjFoo(), two=Bar())
        assert str(result[0]) == "Base"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "ObjFoo"
        assert str(result[3]) == "Bar"
        with self.assertRaises(TypeError):
            r.req_test(Base(), FooBar(), one=ObjFoo(), two=Base())
        with self.assertRaises(TypeError):
            r.req_test(Base(), "", one=ObjFoo(), two=Bar())

    def test_accept_required_with_args(self):
        class Runner:
            @RequireArgs("one", "two", ftype=DecFuncEnum.METHOD)
            @SubClass(Base, Base, (Foo, ObjFoo), (Bar, Obj), ftype=DecFuncEnum.METHOD)
            def req_test(self, *args, **kwargs):
                return (*args, kwargs.get("one", None), kwargs.get("two", None))
        r = Runner()
        result = r.req_test(Base(), FooBar(), one=ObjFoo(), two=Bar())
        assert str(result[0]) == "Base"
        assert str(result[1]) == "FooBar"
        assert str(result[2]) == "ObjFoo"
        assert str(result[3]) == "Bar"
        with self.assertRaises(TypeError):
            r.req_test(Base(), FooBar(), one=ObjFoo(), two=Base())
        with self.assertRaises(TypeError):
            r.req_test(Base(), "", one=ObjFoo(), two=Bar())

    def test_enum(self):
        # enum are iterable so [*Color] is list comperhension.
        # and becomes [<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]
        # for this reason when passing enum types they must be in an itterable
        # such as a list or tuple
        # SubClass will handle enum but will parse all enum values in the process
        # when enum is not passed as iterable.
        class Runner:
            @SubClass([Color], Base, [Color], ftype=DecFuncEnum.METHOD)
            def foo(self, one, two, three):
                return one, two, three
        r = Runner()
        result = r.foo(Color.BLUE, Foo(), Color.RED)
        assert result[0] == Color.BLUE
        assert str(result[1]) == "Foo"
        assert result[2] == Color.RED
        with self.assertRaises(TypeError):
            result = r.foo(1, Foo(), Color.RED)

    def test_enum_base(self):
        # enum are iterable so [*Color] is list comperhension.
        # and becomes [<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]
        # for this reason when passing enum types they must be in an itterable
        # such as a list or tuple
        class Runner:
            @SubClass([Color, Base, int], ftype=DecFuncEnum.METHOD)
            def foo(self, e):
                if isinstance(e, int):
                    result = Color(e)
                else:
                    result = e
                return result
        r = Runner()
        result = r.foo(Color.BLUE)
        assert result == Color.BLUE
        result = r.foo(e=2)
        assert result == Color.GREEN
        result = r.foo(Bar())
        assert str(result) == "Bar"

    def test_star_args_pos3_mix(self):
        # Positional argument cannot appear after keyword arguments
        # however positional arg can come after keword arguments if keyword argumnets are filled out
        # as positional args.
        # myfunc(1.33, "two", 3, Color.BLUE, 5) is allow
        # myfunc(arg1=1.33, arg2="two", 3, Color.BLUE, 5,  kwonlyarg=True) not allowed
        # result = myfunc(3, Color.BLUE, 5, arg1=1.33, arg2="two", kwonlyarg=True) not allowed
        class Runner:
            @SubClass(Bar, Base, Obj, [Color], Foo, ObjFoo, ftype=DecFuncEnum.METHOD)
            def myfunc(self, arg1, arg2, *args, last=ObjFoo()):
                return [arg1, arg2] + [*args] + [last]
        r = Runner()
        result = r.myfunc(Bar(), Base(), Obj(), Color.BLUE, FooBar())
        assert str(result[0]) == "Bar"
        assert str(result[1]) == "Base"
        assert str(result[2]) == "Obj"
        assert result[3] == Color.BLUE
        assert str(result[4]) == "FooBar"
        assert str(result[5]) == "ObjFoo"
        result = r.myfunc(Bar(), Base(), Obj(), Color.RED,
                          FooBar(), last=ObjFoo())
        assert str(result[0]) == "Bar"
        assert str(result[1]) == "Base"
        assert str(result[2]) == "Obj"
        assert result[3] == Color.RED
        assert str(result[4]) == "FooBar"
        assert str(result[5]) == "ObjFoo"
        with self.assertRaises(TypeError):
            r.myfunc(Bar(), Obj(), Obj(), Color.RED, FooBar(), last=ObjFoo())
        with self.assertRaises(TypeError):
            r.myfunc(Bar(), Base(), Obj(), Foo(), FooBar())
        with self.assertRaises(TypeError):
            r.myfunc(Foo(), Base(), Obj(), Color.BLUE, FooBar())
        with self.assertRaises(TypeError):
            r.myfunc(Bar(), Base(), Obj(), Color.RED,
                     FooBar(), last=Color.BLUE)

    def test_subclass_static(self):
        class Runner:
            @staticmethod
            @SubClass((Foo, ObjFoo), Base, ftype=DecFuncEnum.METHOD_STATIC)
            def req_test(**kwargs):
                return (kwargs.get("one"), kwargs.get("two"))
        result = Runner.req_test(one=Foo(), two=Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = Runner.req_test(two=ObjFoo(), one=FooBar())
        assert str(result[0]) == "FooBar"
        assert str(result[1]) == "ObjFoo"
        with self.assertRaises(ValueError):
            result = Runner.req_test(one=Foo())
        with self.assertRaises(ValueError):
            result = Runner.req_test(two=Bar())
        with self.assertRaises(TypeError):
            result = Runner.req_test(one=Obj(), two=Bar())

    def test_subclass_class(self):
        class Runner:
            @classmethod
            @SubClass((Foo, ObjFoo), Base, ftype=DecFuncEnum.METHOD_CLASS)
            def req_test(cls, **kwargs):
                return (kwargs.get("one"), kwargs.get("two"))
        result = Runner.req_test(one=Foo(), two=Bar())
        assert str(result[0]) == "Foo"
        assert str(result[1]) == "Bar"
        result = Runner.req_test(two=ObjFoo(), one=FooBar())
        assert str(result[0]) == "FooBar"
        assert str(result[1]) == "ObjFoo"
        with self.assertRaises(ValueError):
            result = Runner.req_test(one=Foo())
        with self.assertRaises(ValueError):
            result = Runner.req_test(two=Bar())
        with self.assertRaises(TypeError):
            result = Runner.req_test(one=Obj(), two=Bar())

    def test_subclass_property(self):
        class Runner:
            @SubClass(str, ftype=DecFuncEnum.METHOD_CLASS)
            def __init__(self, test_value):
                self._test = test_value

            @property
            def test(self):
                return self._test

            @test.setter
            @SubClass(str, ftype=DecFuncEnum.PROPERTY_CLASS)
            def test(self, value):
                self._test = value
        r = Runner("hello")
        assert r.test == "hello"
        r.test = "world"
        assert r.test == "world"
        with self.assertRaises(TypeError):
            r.test = 1


class TestSubClassDecoratorsLogger(unittest.TestCase):
    def setUp(self):
        clear_log()

    def tearDown(self):
        pass
    
    def test_subclass_gen(self):
        @SubClass((Foo, ObjFoo), Base, opt_logger=test_logger)
        def req_test(**kwargs):
            pass
        with self.assertRaises(ValueError):
            req_test(one=Foo())
        with self.assertRaises(ValueError):
            req_test(two=Bar())
        with self.assertRaises(TypeError):
            req_test(one=Obj(), two=Bar())
        with self.assertRaises(ValueError):
            # too many args
            req_test(one=Obj(), two=Bar(), three=Bar())
        errors = get_logged_errors()
        assert len(errors) == 4

    def test_subclass_opt_args_filter_kwargs(self):
        @SubClass((Foo, ObjFoo), Base, opt_args_filter=DecArgEnum.KWARGS, opt_logger=test_logger)
        def req_test(*args, first, last, **kwargs):
            pass
        with self.assertRaises(TypeError):
            req_test(1, 2, 3, first="1st",
                     last="!", one='one', two=Bar())
        with self.assertRaises(ValueError):
            # too many args
            req_test(1, 2, 3, first="1st", last="!",
                     one=Foo(), two=Bar(), three=Foo())
        errors = get_logged_errors()
        assert len(errors) == 2

    def test_subclass_opt_args_filter_args(self):
        @SubClass((Foo, ObjFoo), Base, opt_args_filter=DecArgEnum.ARGS, opt_logger=test_logger)
        def req_test(*args, first, last, **kwargs):
            pass
        with self.assertRaises(TypeError):
            req_test(Foo(), 1, first="1st", last="!", one=1, two=2)
        with self.assertRaises(ValueError):
            # too many args
           req_test(Foo(), Bar(), Foo(), first="1st", last="!", one=1, two=2)
        errors = get_logged_errors()
        assert len(errors) == 2

    def test_subclass_opt_args_filter_named_args(self):
        @SubClass((Foo, ObjFoo), Base, opt_args_filter=DecArgEnum.NAMED_ARGS, opt_logger=test_logger)
        def req_test(*args, first, last, **kwargs):
            pass
        with self.assertRaises(TypeError):
           req_test(1, 2, 3, first=Foo(), last=1, one=1, two=2)
        errors = get_logged_errors()
        assert len(errors) == 1

    def test_subclass_opt_args_filter_no_args(self):
        @SubClass((Foo, ObjFoo), Base, Foo, Base, opt_args_filter=DecArgEnum.NO_ARGS, opt_logger=test_logger)
        def req_test(*args, first, last, **kwargs):
            pass
        with self.assertRaises(TypeError):
            req_test(1, 2, 3, first=Foo(), last=Bar(), one=Foo(), two=ObjFoo())
        with self.assertRaises(TypeError):
            req_test(1, 2, 3, first=Foo(), last=ObjFoo(), one=Foo(), two=Bar())
        with self.assertRaises(ValueError):
            # too many args
           req_test(1, 2, 3, first=Foo(), last=Bar(),
                    one=Foo(), two=Bar(), three=Bar())
        errors = get_logged_errors()
        assert len(errors) == 3

    def test_subclass_named_args(self):
        @SubClass((Foo, ObjFoo), Base, opt_logger=test_logger)
        def req_test(one, two):
            pass
        with self.assertRaises(TypeError):
            req_test(one=Obj(), two=Bar())
        with self.assertRaises(ValueError):
            req_test(one=Obj(), two=Bar(), three=Bar())
        errors = get_logged_errors()
        assert len(errors) == 2

    def test_subclass_instance_only_true(self):
        @SubClass((Foo, ObjFoo), Base, instance_only=True, opt_logger=test_logger)
        def req_test(**kwargs):
            pass
        with self.assertRaises(ValueError):
            req_test(one=Foo())
        with self.assertRaises(ValueError):
            req_test(two=Bar())
        with self.assertRaises(TypeError):
            req_test(one=Obj(), two=Bar())
        errors = get_logged_errors()
        assert len(errors) == 3

    def test_subclass_instance_only_false(self):
        @SubClass((Foo, ObjFoo), Base, opt_inst_only=False, opt_logger=test_logger)
        def req_test(**kwargs):
            pass
        with self.assertRaises(ValueError):
            req_test(one=Foo)
        with self.assertRaises(ValueError):
            req_test(two=Bar)
        with self.assertRaises(TypeError):
            req_test(one=Obj(), two=Bar())
        errors = get_logged_errors()
        assert len(errors) == 3

    def test_subclass_optional_args(self):
        @SubClass(Foo, FooBar, Obj, opt_logger=test_logger)
        def req_test(first, second=FooBar(), third=Obj()):
            pass
        with self.assertRaises(TypeError):
            req_test(first=Obj())
        with self.assertRaises(TypeError):
            req_test(Obj())
        with self.assertRaises(TypeError):
            req_test(Foo(), FooBar(), Foo())
        with self.assertRaises(TypeError):
            req_test(first=Foo(), third=Foo())
        errors = get_logged_errors()
        assert len(errors) == 4

    def test_subclass_args_optional_named(self):
        @SubClass(Base, Base, Base, (Bar, Obj), (FooBar, Obj), Base, opt_logger=test_logger)
        def req_test(*args, first, second=ObjFoo(), third=Bar()):
            pass
        with self.assertRaises(TypeError):
            req_test(Foo(), Bar(), FooBar(), first=Base())
        with self.assertRaises(TypeError):
            req_test(Foo(), Bar(), FooBar(), first=ObjFoo(), third=Obj())
        errors = get_logged_errors()
        assert len(errors) == 2

    def test_subclass_args_and_kwargs(self):
        @SubClass(Base, Base, (Foo, ObjFoo), (Bar, Obj), opt_logger=test_logger)
        def req_test(*args, **kwargs):
            pass
        with self.assertRaises(TypeError):
            req_test(Base(), FooBar(), one=ObjFoo(), two=Base())
        with self.assertRaises(TypeError):
            req_test(Base(), "", one=ObjFoo(), two=Bar())
        with self.assertRaises(ValueError):
            req_test(*gen_args(5))
        errors = get_logged_errors()
        assert len(errors) == 3

    def test_accept_required_with_args(self):
        @RequireArgs("one", "two")
        @SubClass(Base, Base, (Foo, ObjFoo), (Bar, Obj), opt_logger=test_logger)
        def req_test(*args, **kwargs):
            pass
        with self.assertRaises(TypeError):
            req_test(Base(), FooBar(), one=ObjFoo(), two=Base())
        with self.assertRaises(TypeError):
            req_test(Base(), "", one=ObjFoo(), two=Bar())
        errors = get_logged_errors()
        assert len(errors) == 2

    def test_star_args_pos3_mix(self):
        # Positional argument cannot appear after keyword arguments
        # however positional arg can come after keword arguments if keyword argumnets are filled out
        # as positional args.
        # myfunc(1.33, "two", 3, Color.BLUE, 5) is allow
        # myfunc(arg1=1.33, arg2="two", 3, Color.BLUE, 5,  kwonlyarg=True) not allowed
        # result = myfunc(3, Color.BLUE, 5, arg1=1.33, arg2="two", kwonlyarg=True) not allowed

        @SubClass(Bar, Base, Obj, [Color], Foo, ObjFoo, opt_logger=test_logger)
        def myfunc(arg1, arg2, *args, last=ObjFoo()):
            pass
        with self.assertRaises(TypeError):
            myfunc(Bar(), Obj(), Obj(), Color.RED, FooBar(), last=ObjFoo())
        with self.assertRaises(TypeError):
            myfunc(Bar(), Base(), Obj(), Foo(), FooBar())
        with self.assertRaises(TypeError):
            myfunc(Foo(), Base(), Obj(), Color.BLUE, FooBar())
        with self.assertRaises(TypeError):
            myfunc(Bar(), Base(), Obj(), Color.RED, FooBar(), last=Color.BLUE)
        errors = get_logged_errors()
        assert len(errors) == 4


if __name__ == '__main__':
    unittest.main()
