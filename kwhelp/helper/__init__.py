# coding: utf-8
from collections.abc import Iterator
from inspect import isclass
from typing import Iterable, Tuple

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


def _is_iterable_excluded(arg: object, excluded_types: Iterable) -> bool:
    try:
        isinstance(iter(excluded_types), Iterator)
    except Exception:
        return False

    if len(excluded_types) == 0:
        return False

    def _is_instance(obj: object) -> bool:
        # when obj is instance then isinstance(obj, obj) raises TypeError
        # when obj is not instance then isinstance(obj, obj) return False
        try:
            if not isinstance(obj, obj):
                return False
        except TypeError:
            pass
        return True
    ex_types = excluded_types if isinstance(excluded_types, tuple) else tuple(excluded_types)
    arg_instance = _is_instance(arg)
    if arg_instance is True:
        if isinstance(arg, ex_types):
            return True
        return False
    if isclass(arg) and issubclass(arg, ex_types):
        return True
    return arg in ex_types
 
    
def is_iterable(arg: object, excluded_types: Iterable[type]=(str,)) -> bool:
    """
    Gets if ``arg`` is iterable.

    Args:
        arg (object): object to test
        excluded_types (Iterable[type], optional): Iterable of type to exlcude.
            If ``arg`` matches any type in ``excluded_types`` then ``False`` will be returned.
            Default ``(str,)``

    Returns:
        bool: ``True`` if ``arg`` is an iterable object and not of a type in ``excluded_types``;
        Otherwise, ``False``.

    Note:
        if ``arg`` is of type str then return result is ``False``.

    Example:
        .. code-block:: python

            

            # non-string iterables    
            assert is_iterable(arg=("f", "f"))       # tuple
            assert is_iterable(arg=["f", "f"])       # list
            assert is_iterable(arg=iter("ff"))       # iterator
            assert is_iterable(arg=range(44))        # generator
            assert is_iterable(arg=b"ff")            # bytes (Python 2 calls this a string)

            # strings or non-iterables
            assert not is_iterable(arg=u"ff")        # string
            assert not is_iterable(arg=44)           # integer
            assert not is_iterable(arg=is_iterable)  # function
            
            # excluded_types, optionally exlcude types
            from enum import Enum, auto

            class Color(Enum):
                RED = auto()
                GREEN = auto()
                BLUE = auto()
            
            assert is_iterable(arg=Color)             # Enum
            assert not is_iterable(arg=Color, excluded_types=(Enum, str)) # Enum
    """
    # if isinstance(arg, str):
    #     return False
    result = False
    try:
        result = isinstance(iter(arg), Iterator)
    except Exception:
        result = False
    if result is True:
        if _is_iterable_excluded(arg, excluded_types=excluded_types):
            result = False
    return result
