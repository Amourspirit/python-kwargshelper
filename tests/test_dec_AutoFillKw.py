import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import AutoFillKw
from enum import IntEnum, auto


class Color(IntEnum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

    def __str__(self) -> str:
        return self._name_

class TestGeneral(unittest.TestCase):

    def test_gen(self):
        @AutoFillKw
        class Foo:
            pass

        f = Foo(a=1, b=2, end="!")
        assert f.a == 1
        assert f.b == 2
        assert f.end == "!"
    
    def test_enum(self):
        @AutoFillKw
        class Foo:
            pass

        f = Foo(a=1, b=2, color=Color.BLUE)
        assert f.a == 1
        assert f.b == 2
        assert f.color == Color.BLUE

    def test_obj(self):
        @AutoFillKw
        class Foo:
            pass

        f = Foo(a=1, b=2, c=self)
        assert f.a == 1
        assert f.b == 2
        assert f.c is self


if __name__ == '__main__':
    unittest.main()
