import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import AutoFill
from enum import IntEnum, auto

class Color(IntEnum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

    def __str__(self) -> str:
        return self._name_
class TestGeneral(unittest.TestCase):

    def test_gen(self):
        @AutoFill('a', 'b', c=3)
        class Foo: pass

        f = Foo(1, 2)
        assert f.a == 1
        assert f.b == 2
        assert f.c == 3
 
    def test_enum(self):
        @AutoFill('a', 'b', c=Color.GREEN)
        class Foo:
            pass

        f = Foo(1, 2)
        assert f.a == 1
        assert f.b == 2
        assert f.c == Color.GREEN

    def test_obj(self):
        @AutoFill('a', 'b', c=3)
        class Foo: pass

        f = Foo(1, 2, self)
        assert f.a == 1
        assert f.b == 2
        assert f.c is self


if __name__ == '__main__':
    unittest.main()
