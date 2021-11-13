# coding: utf-8
from inspect import isclass
import re
from typing import Iterable, List, Optional, Iterator

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

class Formatter:
    """String Fromat Methods"""
    _rx_star = re.compile("^\*(\d*)$")

    @staticmethod
    def is_star_num(name: str) -> bool:
        """
        Gets if arg name is a match to foramt ``'*#'``, eg: ``'*0'``, ``'*1'``, ``'*2'``.

        Args:
            name (str): Name to match

        Raises:
            TypeError: if name is not a ``str`` value.

        Returns:
            bool: ``True`` if ``arg_name`` is a match; Otherwise, ``False``
        """
        if not isinstance(name, str):
            raise TypeError("'is_star_num()' error, arg 'name` must be of type `str`")
        m = Formatter._rx_star.match(name)
        if m:
            return True
        return False
    
    @staticmethod
    def get_star_num(num: int) -> str:
        """
        Gets a str in format of ``'*#'``, eg: ``'*0'``, ``'*1'``, ``'*2'``.

        Args:
            num (int): int to convert

        Returns:
            str: [str in format of ``'*#'``
        """
        return "*" + str(num)

    @staticmethod
    def get_missing_args_error_msg(missing_names: List[str], name: Optional[str] = ""):
        """
        Get an error message for a list of names.

        Args:
            missing_names (List[str]): List of names that generated the error.
                Such as a list of missing arguments of a function.
            name (Optional[str], optional): Function, class, method name. Defaults to "".

        Returns:
            [type]: Formated string for ``missing_names`` has elements; Otherwise, empty string is returned.
        """
        missing_names_len = len(missing_names)
        if missing_names_len == 0:
            return ""
        msg = f"{name} missing {missing_names_len} required positional".lstrip()
        if missing_names_len == 1:
            msg = msg + " argument: "
        else:
            msg = msg + " arguments: "
        msg = msg + Formatter.get_formated_names(names=missing_names)
        return msg

    @staticmethod
    def get_formated_names(names: List[str], **kwargs) -> str:
        """
        Gets a formated string of a list of names

        Args:
            names (List[str]): List of names

        Keyword Args:
            conj (str, optional): Conjunction used to join list. Default ``and``.
            wrapper (str, optional): String to prepend and append to each value. Default ``'``.

        Returns:
            str: formated such as ``'final' and 'end'`` or ``'one', 'final', and 'end'``
        """
        conj = kwargs.get("conj", "and")
        wrapper = kwargs.get("wrapper", "'")
        s = ""
        names_len = len(names)
        last_index = names_len - 1
        for i, name in enumerate(names):
            if i > 0:
                if names_len > 2:
                    s = s + ', '
                else:
                    s = s + ' '
                if names_len > 1 and i == last_index:
                    s = s + conj + ' '

            s = s + "{0}{1}{0}".format(wrapper, name)
        return s
    
    @staticmethod
    def get_formated_types(types: Iterator[type], **kwargs) -> str:
        """
        Gets a formated string from a list of types.

        Args:
            types (Iterator[type]): Types to create fromated string.

        Keyword Args:
            conj (str, optional): Conjunction used to join list. Default ``and``.
            wrapper (str, optional): String to prepend and append to each value. Default ``'``.

        Returns:
            str: Formated String
        """
        t_names = [t.__name__ for t in types]
        result = Formatter.get_formated_names(names=t_names, **kwargs)
        return result

    @staticmethod
    def get_ordinal(num: int) -> str:
        """
        Returns the ordinal number of a given integer, as a string.

        Args:
            num (int): integer to get ordinal value of.

        Returns:
            str: num as ordinal str. eg. 1 -> 1st, 2 -> 2nd, 3 -> 3rd, etc.
        """
        if 10 <= num % 100 < 20:
            return '{0}th'.format(num)
        else:
            ord = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
            return '{0}{1}'.format(num, ord)

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
