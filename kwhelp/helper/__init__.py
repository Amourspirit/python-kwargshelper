# coding: utf-8
from typing import Iterable, Iterator, Optional, Set, Union


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

class TypeChecker:
    
    def __init__(self, types: Iterator[type], **kwargs):
        """
        [summary]

        Args:
            types (Iterator[type]): Types used for Validation purposes.

         Keyword Arguments:
            raise_error: (bool, optional): If ``True`` then an error will be raised if a :py:meth:`~.TypeChecker.validate`` fails:
                Othwewise :py:meth:`~.TypeChecker.validate`` will return a boolean value indicationg success or failure.
            type_instance_check (bool, optional): If ``True`` then :py:meth:`~.TypeChecker.validate`` args
                are tested also for isinstance if type does not match, rather then just type check if type is a match.
                If ``False`` then values willl only be tested as type.
                Default ``True``
        """
        self._types = types
        
        if self._types is None:
            self._types = []

        key = 'raise_error'
        if key in kwargs:
            self._raise_error: bool = bool(kwargs[key])
        else:
            self._raise_error: bool = True

        key = 'type_instance_check'
        if key in kwargs:
            self._type_instance_check: bool = bool(kwargs[key])
        else:
            self._type_instance_check: bool = True


    def _get_formated_types(self) -> str:
        result = ''
        for i, t in enumerate(self._types):
            if i > 0:
                result = result + ' | '
            result = f"{result}{t}"
        return result

    def _validate_type(self, value: object,  key: Union[str, None] = None):
        def _is_type_instance(_types: Iterator[type], _value):
            result = False
            for t in _types:
                if isinstance(_value, t):
                    result = True
                    break
            return result
        if len(self._types) == 0:
            return True
        result = True
        if not type(value) in self._types:
            # object such as PosixPath inherit from more than on class (Path, PurePosixPath)
            # testing if PosixPath is type of Path is False.
            # for this reason will do an instace check as well. isinstance(_posx, Path) is True
            is_valid_type = False
            if self._type_instance_check == True and _is_type_instance(self._types, value):
                is_valid_type = True

            if is_valid_type is True:
                result = True
            else:
                result = False
                if self._raise_error is True:
                    if key is None:
                        msg = f"Arg 'Value is expected to be of '{self._get_formated_types()}' but got '{type(value).__name__}'"
                    else:
                        msg = f"Arg '{key}' is expected to be of '{self._get_formated_types()}' but got '{type(value).__name__}'"
                    raise TypeError(msg)
        return result

    def validate(self, *args, **kwargs) -> bool:
        if len(self._types) == 0:
            return True
        result = True
        for arg in args:
            result = result & self._validate_type(value=arg)
            if result is False:
               break
        if result is False:
            return result
        for k, v in kwargs.items():
           result = result & self._validate_type(value=v, key=k)
           if result is False:
               break
        return result
       
    # region Properties
    @property
    def type_instance_check(self) -> bool:
        """
        Determines if instance checking is done with type checking.
        
        If ``True`` then :py:meth:`~.TypeChecker.validate`` args
        are tested also for isinstance if type does not match, rather then just type check if type is a match.
        If ``False`` then values willl only be tested as type.
        
        :getter: Gets type_instance_check value
        :setter: sets type_instance_check value
        """
        return self._type_instance_check
    
    @type_instance_check.setter
    def type_instance_check(self, value: bool) -> bool:
        self._type_instance_check = bool(value)
    # endregion Properties
