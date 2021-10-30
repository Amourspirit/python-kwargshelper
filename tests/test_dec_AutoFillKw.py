import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import AutoFillKw


class TestGeneral(unittest.TestCase):

    def test_gen(self):
        @AutoFillKw
        class Foo:
            pass

        f = Foo(a=1, b=2, end="!")
        assert f.a == 1
        assert f.b == 2
        assert f.end == "!"

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
