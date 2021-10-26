import functools
from typing import Dict, Iterable, Optional, Union
from inspect import signature, isclass, ismethod, getargspec, isfunction
from ..checks import TypeChecker, RuleChecker
from ..rules import IRule
from ..helper import is_iterable
from abc import ABC
class DecBase(ABC):
    def _args_without_self(self, method):
        # https://stackoverflow.com/questions/27777939/list-arguments-of-function-method-and-skip-self-in-python-3
        args, varargs, varkw, defaults = getargspec(method)
        if ismethod(method):
            args = args[1:]    # Skip 'self'
        return args


def _args_without_self(method, args):
    sig = signature(method)
    args_names = [k for k in sig.parameters.keys()]
    if isfunction(method) and '.' in method.__qualname__ and args_names[0] == 'self':
        return args[1:], args_names[1:]    # Skip 'self'
    return args, args_names


def _get_args_dict(method, args, kwargs):
        # https://stackoverflow.com/questions/218616/how-to-get-method-parameter-names
        # args_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
    _args, _names = _args_without_self(method, args)
    return {**dict(zip(_names, _args)), **kwargs}

class TypeCheck(object):
    """
    Decorator that decorates methods that require args to match a type specificed in a list

    See Also:
        :doc:`../../usage/Decorator/TypeCheck`
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor

        Other Parameters:
            args (type): One or more types for wrapped function args to match.

        Keyword Arguments:
            raise_error: (bool, optional): If ``True`` then a ``TypeError`` will be raised if a
                validation fails. If ``False`` then an attribute will be set on decorated function
                named ``is_types_valid`` indicating if validation status.
                Default ``True``.
            type_instance_check (bool, optional): If ``True`` then args are tested also for ``isinstance()``
                if type does not match, rather then just type check. If ``False`` then values willl only be
                tested as type. Default ``True``

        Raises:
            TypeError: If ``types`` arg is not a iterable object such as a list or tuple.
            TypeError: If any arg is not of a type listed in ``types``.
        """
        self._types = [arg for arg in args]
        if kwargs:
            # keyword args are passed to TypeChecker
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tc = TypeChecker(*self._types, **self._kwargs)
            is_valid = tc.validate(*args, **kwargs)
            if tc.raise_error is False:
                wrapper.is_types_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper
class TypeCheckKw(object):
    """
    Decorator that decorates methods that require key, value args to match a type specificed in a list

    See Also:
        :doc:`../../usage/Decorator/TypeCheckKw`
    """

    def __init__(self, arg_info: Dict[str, Union[int, type, Iterable[type]]], types: Optional[Iterable[Union[type, Iterable[type]]]] = None, **kwargs):
        """
        Constructor

        Args:
            arg_info (Dict[str, Union[int, type, Iterable[type]]]): Dictionary of Key and int, type, or Iterable[type].
                Each Key represents that name of an arg to match one or more types(s).
                If value is int then value is an index that corresponds to an item in ``types``.
            types (Iterable[Union[type, Iterable[type]]], optional): List of types for arg_info entries to match.
                Default ``None``

        Keyword Arguments:
            raise_error: (bool, optional): If ``True`` then a ``TypeError`` will be raised if a
                validation fails. If ``False`` then an attribute will be set on decorated function
                named ``is_types_kw_valid`` indicating if validation status.
                Default ``True``.
            type_instance_check (bool, optional): If ``True`` then args are tested also for ``isinstance()``
                if type does not match, rather then just type check. If ``False`` then values willl only be
                tested as type. Default ``True``
        """
        self._arg_index = arg_info
        if types is None:
            self._types = []
        else:
            self._types = types
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def _get_types(self, key: str) -> Iterable:
        value = self._arg_index[key]
        if isinstance(value, int):
            t = self._types[value]
            if isinstance(t, Iterable):
                return t
            return [t]
        if is_iterable(value):
            return value
        else:
            # make iterable
            return (value,)


    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            is_valid = True
            arg_name_values = _get_args_dict(func, args, kwargs)
            arg_keys = arg_name_values.keys()
            tc = False
            for key in self._arg_index.keys():
                if key in arg_keys:
                    types = self._get_types(key=key)
                    if len(types) == 0:
                        continue
                    value = arg_name_values[key]
                    tc = TypeChecker(*types, **self._kwargs)
                    is_valid = tc.validate(**{key: value})
                    if is_valid is False:
                        break
            if tc and tc.raise_error is False:
                wrapper.is_types_kw_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper


class RuleCheckAny(DecBase):
    """
    Decorator that decorates methods that require args to match a rule specificed in ``rules`` list.
    
    If a function arg does not match at least one rule in ``rules`` list then validation will fail.

    See Also:
        :doc:`../../usage/Decorator/RuleCheckAny`
    """
    def __init__(self, *args: IRule, **kwargs):
        """
        Constructor

        Other Parameters:
            args (IRule): One or more rules to use for validation

        Keyword Arguments:
            raise_error (bool, optional): If ``True`` then an Exception will be raised if a
                validation fails. The kind of exception raised depends on the rule that is
                invalid. Typically a ``TypeError`` or a ``ValueError`` is raised.
                
                If ``False`` then an attribute will be set on decorated function
                named ``is_rules_any_valid`` indicating if validation status.
                Default ``True``.
        """
        self._rules = [arg for arg in args]
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            rc = RuleChecker(rules_any=self._rules, **self._kwargs)
            _args = _args_without_self(func, args)[0]
            is_valid = rc.validate_any(*_args, **kwargs)
            if rc.raise_error is False:
                wrapper.is_rules_any_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper

class RuleCheckAll(object):
    """
    Decorator that decorates methods that require args to match all rules specificed in ``rules`` list.
    
    If a function arg does not match all rules in ``rules`` list then validation will fail.
    
    See Also:
        :doc:`../../usage/Decorator/RuleCheckAll`
    """
    def __init__(self, *args: IRule, **kwargs):
        """
        Constructor

        Other Parameters:
            args (IRule): One or more rules to use for validation

        Keyword Arguments:
            raise_error (bool, optional): If ``True`` then an Exception will be raised if a
                validation fails. The kind of exception raised depends on the rule that is
                invalid. Typically a ``TypeError`` or a ``ValueError`` is raised.

                If ``False`` then an attribute will be set on decorated function
                named ``is_rules_all_valid`` indicating if validation status.
                Default ``True``.
        """
        self._rules = [arg for arg in args]
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            rc = RuleChecker(rules_all=self._rules, **self._kwargs)
            _args = _args_without_self(func, args)[0]
            is_valid = rc.validate_all(*_args, **kwargs)
            if rc.raise_error is False:
                wrapper.is_rules_all_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper

class RuleCheckAllKw(object):
    """
    Decorator that decorates methods that require specific args to match rules specificed in ``rules`` list.
    
    If a function specific args do not match all matching rules in ``rules`` list then validation will fail.
    
    See Also:
        :doc:`../../usage/Decorator/RuleCheckAllKw`
    """
    def __init__(self, arg_info: Dict[str, Union[int, IRule, Iterable[IRule]]], rules: Optional[Iterable[Union[IRule, Iterable[IRule]]]] = None, **kwargs):
        """
        Constructor

        Args:
            arg_info (Dict[str, Union[int, IRule, Iterable[IRule]]]): Dictionary of Key and int, IRule, or Iterable[IRule].
                Each Key represents that name of an arg to check with one or more rules.
                If value is int then value is an index that corresponds to an item in ``rules``.
            rules (Iterable[Union[IRule, Iterable[IRule]]], optional): List of rules for arg_info entries to match.
                Default ``None``

         Keyword Arguments:
            raise_error: (bool, optional): If ``True`` then an Exception will be raised if a
                validation fails. The kind of exception raised depends on the rule that is
                invalid. Typically a ``TypeError`` or a ``ValueError`` is raised.

                If ``False`` then an attribute will be set on decorated function
                named ``is_rules_kw_all_valid`` indicating if validation status.
                Default ``True``.
        """
        self._arg_index = arg_info
        if rules is None:
            self._rules = []
        else:
            self._rules = rules
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def _get_rules(self, key: str) -> Iterable:
        value = self._arg_index[key]
        if isinstance(value, int):
            r = self._rules[value]
            if isinstance(r, Iterable):
                return r
            return [r]
        if isclass(value) and issubclass(value, IRule):
            return (value,)
        return value

    def __call__(self, func):
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            is_valid = True
            arg_name_values = _get_args_dict(func, args, kwargs)
            arg_keys = arg_name_values.keys()
            add_attrib = None
            for key in self._arg_index.keys():
                if key in arg_keys:
                    rules = self._get_rules(key=key)
                    if len(rules) == 0:
                        continue
                    value = arg_name_values[key]
                    rc = RuleChecker(rules_all=rules, **self._kwargs)
                    if add_attrib is None:
                        add_attrib = not rc.raise_error
                    is_valid = rc.validate_all(**{key: value})
                    if is_valid is False:
                        break
            if add_attrib:
                wrapper.is_rules_kw_all_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper

class RuleCheckAnyKw(RuleCheckAllKw):
    """
    Decorator that decorates methods that require specific args to match rules specificed in ``rules`` list.

    If a function specific args do not match at least one matching rule in ``rules`` list then validation will fail.

    See Also:
        :doc:`../../usage/Decorator/RuleCheckAnyKw`
    """
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            is_valid = True
            arg_name_values = _get_args_dict(func, args, kwargs)
            arg_keys = arg_name_values.keys()
            add_attrib = None
            for key in self._arg_index.keys():
                if key in arg_keys:
                    rules = self._get_rules(key=key)
                    if len(rules) == 0:
                        continue
                    value = arg_name_values[key]
                    rc = RuleChecker(rules_any=rules, **self._kwargs)
                    if add_attrib is None:
                        add_attrib = not rc.raise_error
                    is_valid = rc.validate_any(**{key: value})
                    if is_valid is False:
                        break
            if add_attrib:
                wrapper.is_rules_any_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper

class RequireArgs(object):
    """
    Decorator that defines required args for ``**kwargs`` of a function.

    See Also:
        :doc:`../../usage/Decorator/RequireArgs`
    """
    def __init__(self, *args: str):
        """
        Constructor

        Other Parameters:
            args (type): One or more names of wrapped function args to require.
        """
        self._args = []
        for arg in args:
            if isinstance(arg, str):
                self._args.append(arg)
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            arg_name_values = _get_args_dict(func, args, kwargs)
            arg_keys = arg_name_values.keys()
            for key in self._args:
                if not key in arg_keys:
                    raise ValueError(f"'{key}' is a required arg.")
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper

class DefaultArgs(object):
    """
    Decorator that defines default values for ``**kwargs`` of a function.

    See Also:
        :doc:`../../usage/Decorator/DefaultArgs`
    """
    def __init__(self, **kwargs: Dict[str, object]):
        """
        Constructor

        Keyword Arguments:
            kwargs (Dict[str, object]): One or more Key, Value pairs to assign to wrapped function args as defaults.
        """
        self._kwargs = kwargs

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for key, value in self._kwargs.items():
                if not key in kwargs:
                    kwargs[key] = value
            return func(*args, **kwargs)
        return wrapper

