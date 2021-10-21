import functools
from typing import Dict, Iterable
from ..helper import TypeChecker


class TypeCheckerAny(object):

    def __init__(self, types: Iterable[type], **kwargs):
        self._types = types
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tc = TypeChecker(types=self._types, **self._kwargs)
            is_valid = tc.validate(*args, **kwargs)
            wrapper.is_types_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper


class KwTypeChecker(object):
    def __init__(self, arg_index: Dict[str, int], types: Iterable[Iterable[type]], **kwargs):
        self._arg_index = arg_index
        self._types = types
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def _get_types(self, key: str) -> list:
        if not key in self._arg_index:
            return []
        result = []
        try:
            index = int(self._arg_index[key])
            result = self._types[index]
        except IndexError:
            result = []
        return result

    def _get_args_dict(self, fn, args, kwargs):
        # https://stackoverflow.com/questions/218616/how-to-get-method-parameter-names
        args_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
        return {**dict(zip(args_names, args)), **kwargs}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            is_valid = True
            arg_name_values = self._get_args_dict(func, args, kwargs)
            for k, _ in arg_name_values.items():
                types = self._get_types(key=k)
                if len(types) == 0:
                    continue
                tc = TypeChecker(types=types, **self._kwargs)
                is_valid = tc.validate(**arg_name_values)
                if is_valid is False:
                    break
            wrapper.is_types_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper


def type_checker_any(types):
    def type_checker_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tc = TypeChecker(types=types)
            is_valid = tc.validate(*args, **kwargs)
            func.is_types_valid = is_valid
            return func(*args, **kwargs)
        return wrapper
    return type_checker_decorator

