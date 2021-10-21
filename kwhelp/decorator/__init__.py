import functools
import inspect
import itertools
from typing import Dict, Iterable

from inspect import signature
from ..helper import TypeChecker, RuleChecker
from ..rules import IRule

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

class TypeCheckerKw(object):
    def __init__(self, arg_index: Dict[str, int], types: Iterable[Iterable[type]], **kwargs):
        self._arg_index = arg_index
        self._types = types
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def _get_types(self, key: str) -> Iterable:
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
        # args_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
        sig = signature(fn)
        args_names = sig.parameters.keys()
        return {**dict(zip(args_names, args)), **kwargs}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            is_valid = True
            arg_name_values = self._get_args_dict(func, args, kwargs)
            for k, v in arg_name_values.items():
                types = self._get_types(key=k)
                if len(types) == 0:
                    continue
                tc = TypeChecker(types=types, **self._kwargs)
                # is_valid = tc.validate(**arg_name_values)
                is_valid = tc.validate(**{k:v})
                if is_valid is False:
                    break
            wrapper.is_types_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper


class RuleCheckAny(object):
    def __init__(self, rules: Iterable[IRule], **kwargs):
        self._rules = rules
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            rc = RuleChecker(rules_any=self._rules, **self._kwargs)
            is_valid = rc.validate_any(*args, **kwargs)
            wrapper.is_rules_any_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper


class RuleCheckAll(object):
    def __init__(self, rules: Iterable[IRule], **kwargs):
        self._rules = rules
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            rc = RuleChecker(rules_all=self._rules, **self._kwargs)
            is_valid = rc.validate_all(*args, **kwargs)
            wrapper.is_rules_all_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper


class RuleCheckAllKw(object):
    def __init__(self, arg_index: Dict[str, int], rules: Iterable[Iterable[IRule]], **kwargs):
        self._arg_index = arg_index
        self._rules = rules
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def _get_rules(self, key: str) -> Iterable:
        if not key in self._arg_index:
            return []
        result = []
        try:
            index = int(self._arg_index[key])
            result = self._rules[index]
        except IndexError:
            result = []
        return result

    def _get_args_dict(self, fn, args, kwargs):
        # https://stackoverflow.com/questions/218616/how-to-get-method-parameter-names
        # args_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
        sig = signature(fn)
        args_names = sig.parameters.keys()
        return {**dict(zip(args_names, args)), **kwargs}

    def __call__(self, func):
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            is_valid = True
            arg_name_values = self._get_args_dict(func, args, kwargs)
            arg_keys = arg_name_values.keys()
                       
            for key in self._arg_index.keys():
                if key in arg_keys:
                    rules = self._get_rules(key=key)
                    if len(rules) == 0:
                        continue
                    value = arg_name_values[key]
                    rc = RuleChecker(rules_all=rules, **self._kwargs)
                    is_valid = rc.validate_all(**{key: value})
                    if is_valid is False:
                        break
            wrapper.is_rules_all_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper


class RuleCheckAnyKw(RuleCheckAllKw):
 
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            is_valid = True
            arg_name_values = self._get_args_dict(func, args, kwargs)
            arg_keys = arg_name_values.keys()
            for key in self._arg_index.keys():
                if key in arg_keys:
                    rules = self._get_rules(key=key)
                    if len(rules) == 0:
                        continue
                    value = arg_name_values[key]
                    rc = RuleChecker(rules_any=rules, **self._kwargs)
                    is_valid = rc.validate_any(**{key: value})
                    if is_valid is False:
                        break
            wrapper.is_rules_any_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper
