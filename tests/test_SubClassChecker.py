# coding: utf-8
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.checks import SubClassChecker
from enum import IntEnum, auto


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

class TestSubClassChecker(unittest.TestCase):

    def test_main(self):
        tc = SubClassChecker(Obj, Base)
        assert len(tc.types) == 2
        assert tc.validate(one=ObjFoo(), two=Base()) == True
        with self.assertRaises(TypeError):
            tc.validate(one=ObjFoo, two=Color.BLUE)

        assert tc.validate(Base(), Foo(), Bar()) == True
        # with self.assertRaises(TypeError):
        #     tc.validate(4.6, 5, 5.8, '')

    def test_types_none(self):
        sc = SubClassChecker()
        # no checking takes place with types is None
        assert sc.validate(one=ObjFoo(), two=Base) == True
        assert sc.validate(Base(), Foo(), Bar(), FooBar(), Obj(), ObjFoo()) == True
        assert sc.validate(Base(), "a", int, self) == True

    def test_no_err(self):
        sc = SubClassChecker(Base, ObjFoo, raise_error=False)
        assert sc.validate(one=Foo(), two=ObjFoo()) == True
        assert sc.validate(one=Bar(), two=Obj()) == False
        assert sc.validate(Foo(), ObjFoo(), '') == False
        sc.raise_error = True
        assert sc.raise_error == True
        with self.assertRaises(TypeError):
            sc.validate(Foo(), ObjFoo(), '')

    def test_instance_only(self):
        sc = SubClassChecker(Color, int, Base, opt_inst_only=False)
        sc.raise_error = False
        assert sc.raise_error == False
        assert sc.instance_only == False
        assert sc.validate(first=1, second=Color.BLUE, third=Foo) == True
        sc.instance_only = False
        assert sc.validate(first="", second=Color.BLUE, third=Foo) == False

    def test_typecheck(self):
        sc = SubClassChecker()
        assert sc._is_instance(Foo) == False
        assert sc._is_instance(int) == False
        assert sc._is_instance(float) == False
        assert sc._is_instance(str) == False
        assert sc._is_instance(Foo()) == True
        assert sc._is_instance(1) == True
        assert sc._is_instance(-22.33) == True
        assert sc._is_instance("") == True
        assert sc._is_instance(Color) == False
        assert sc._is_instance(Color.BLUE) == True
        assert sc._is_instance(Color.RED) == True
        assert sc._is_instance(Color.GREEN) == True
        assert sc._is_instance(self) == True



if __name__ == '__main__':
    unittest.main()
