# coding: utf-8
import collections

class Singleton(type):
    """Singleton abstrace class"""
    _instances = {}
    # https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class NoThing(metaclass=Singleton):
    '''Singleton Class to mimic null'''


NO_THING = NoThing()
"""
Singleton Class instance that represents null object.
"""


def is_iterable(arg: object) -> bool:
    """
    Gets if ``arg`` is iterable.

    Args:
        arg (object): object to test

    Returns:
        bool: ``True`` if ``arg`` is an iterable object; Otherwise, ``False``.

    Note:
        if ``arg`` is of type str then return result is ``False``.

    Example:
        .. code-block:: python

            # non-string iterables    
            assert is_iterable(("f", "f"))    # tuple
            assert is_iterable(["f", "f"])    # list
            assert is_iterable(iter("ff"))    # iterator
            assert is_iterable(range(44))     # generator
            assert is_iterable(b"ff")         # bytes (Python 2 calls this a string)

            # strings or non-iterables
            assert not is_iterable(u"ff")     # string
            assert not is_iterable(44)        # integer
            assert not is_iterable(is_iterable)  # function
    """
    return (
        isinstance(arg, collections.Iterable)
        and not isinstance(arg, str)
    )
