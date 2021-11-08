# coding: utf-8
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.helper import is_iterable
from enum import Enum, auto


class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

class TestIsIterable(unittest.TestCase):
    def test_is_iterable(self):
        assert is_iterable(arg=("f", "f"))    # tuple
        assert is_iterable(arg=["f", "f"])    # list
        assert is_iterable(arg=iter("ff"))    # iterator
        assert is_iterable(arg=range(44))     # generator
        # bytes (Python 2 calls this a string)
        assert is_iterable(arg=b"ff")

        # strings or non-iterables
        assert not is_iterable(arg=u"ff")     # string
        assert not is_iterable(arg=44)        # integer
        assert not is_iterable(arg=is_iterable)  # function
        assert is_iterable(arg=Color)             # Enum
        assert not is_iterable(arg=Color, excluded_types=(Enum, str))    # Enum
        assert is_iterable(arg=Color, excluded_types=())
        assert is_iterable(arg=Color, excluded_types=2)
if __name__ == '__main__':
    unittest.main()
