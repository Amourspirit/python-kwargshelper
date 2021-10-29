import functools
from typing import Dict, Iterable, Optional, Union
from inspect import signature, isclass, Parameter, Signature
from ..checks import TypeChecker, RuleChecker
from ..rules import IRule
from ..helper import is_iterable
from enum import IntEnum
# import wrapt


class DecFuncEnum(IntEnum):
    """Represents options for type of Function or Method"""
    FUNCTION = 1
    """Normal Unbound function"""
    METHOD_STATIC = 2
    """Class Static Method (@staticmethod)"""
    METHOD = 3
    """Class Method"""
    METHOD_CLASS = 4
    """Class Method (@classmethod)"""

    def __str__(self):
        return self._name_

class _DecBase:
    def __init__(self, **kwargs):
        self._ftype: DecFuncEnum = kwargs.get("ftype", None)
        if self._ftype is not None:
            if not isinstance(self._ftype, DecFuncEnum):
                try:
                    self._ftype = DecFuncEnum(self._ftype)
                except:
                    raise TypeError(
                        f"{self.__class__.__name__} requires arg 'ftype' to be a 'DecFuncType")
        else:
            self._ftype = DecFuncEnum.FUNCTION

    def _drop_arg_first(self) -> bool:
        return self._ftype.value > DecFuncEnum.METHOD_STATIC.value

    def _get_args(self, args):
        if self._drop_arg_first():
            return args[1:]
        return args

    def _get_args_dict(self, method, args, kwargs):
        sig = signature(method)
        _names = [k for k in sig.parameters.keys()]
        if self._drop_arg_first():
            _names = _names[1:]
            _args = args[1:]
        else:
            _args = args
        return {**dict(zip(_names, _args)), **kwargs}


class TypeCheck(_DecBase):
    """
    Decorator that decorates methods that requires args to match a type specificed in a list

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
                tested as type.
                Default ``True``
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``

        Raises:
            TypeError: If ``types`` arg is not a iterable object such as a list or tuple.
            TypeError: If any arg is not of a type listed in ``types``.
        """
        super().__init__(**kwargs)
        self._tc = None
        self._types = [arg for arg in args]
        if kwargs:
            # keyword args are passed to TypeChecker
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}
        

    def __call__(self, func: callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _args = self._get_args(args)
            is_valid = self._typechecker.validate(*_args, **kwargs)
            if self._typechecker.raise_error is False:
                wrapper.is_types_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper

    @property
    def _typechecker(self) -> TypeChecker:
        if self._tc is None:
            self._tc = TypeChecker(*self._types, **self._kwargs)
        return self._tc


class ReturnTypeCheck(_DecBase):
    """
    Decorator that decorates methods that require return value to match a type specificed.

    See Also:
        :doc:`../../usage/Decorator/ReturnTypeCheck`
    """
    def __init__(self, return_type: type, **kwargs):
        """
        Constructor

        Args:
            return_type (type): Type that is used to validate return type.
        Keyword Arguments:
            type_instance_check (bool, optional): If ``True`` then args are tested also for ``isinstance()``
                if type does not match, rather then just type check. If ``False`` then values willl only be
                tested as type.
                Default ``True``
        """
        super().__init__(**kwargs)
        self._tc = None
        self._type = return_type
        if kwargs:
            # keyword args are passed to TypeChecker
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func: callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return_value = func(*args, **kwargs)
            is_valid = False
            try:
                is_valid = self._typechecker.validate(return_value)
            except TypeError:
                # catch type error and raise a new one so a more fitting message is raised.
                raise TypeError(self._get_err_msg(return_value))
            # validate will raise Typeerror if raise_error is True,
            # otherwise will rasise error here
            if is_valid is False:
                raise TypeError(self._get_err_msg(return_value))
            return return_value
        return wrapper

    def _get_err_msg(self, value: object):
        msg = f"Return Value is expected to be of '{self._type.__name__}' but got '{type(value).__name__}'"
        return msg

    @property
    def _typechecker(self) -> TypeChecker:
        if self._tc is None:
            self._tc = TypeChecker(self._type, **self._kwargs)
        return self._tc

class TypeCheckKw(_DecBase):
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
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
        """
        super().__init__(**kwargs)
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
            arg_name_values = self._get_args_dict(func, args, kwargs)
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


class RuleCheckAny(_DecBase):
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
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
        """
        super().__init__(**kwargs)
        self._rc = None
        self._rules = [arg for arg in args]
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _args = self._get_args(args)
            is_valid = self._rulechecker.validate_any(*_args, **kwargs)
            if self._rulechecker.raise_error is False:
                wrapper.is_rules_any_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper

    @property
    def _rulechecker(self) -> RuleChecker:
        if self._rc is None:
            self._rc = RuleChecker(rules_any=self._rules, **self._kwargs)
        return self._rc


class RuleCheckAll(_DecBase):
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
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
        """
        super().__init__(**kwargs)
        self._rc = None
        self._rules = [arg for arg in args]
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _args = self._get_args(args)
            is_valid = self._rulechecker.validate_all(*_args, **kwargs)
            if self._rulechecker.raise_error is False:
                wrapper.is_rules_all_valid = is_valid
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper

    @property
    def _rulechecker(self) -> RuleChecker:
        if self._rc is None:
            self._rc = RuleChecker(rules_all=self._rules, **self._kwargs)
        return self._rc


class RuleCheckAllKw(_DecBase):
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
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
        """
        super().__init__(**kwargs)
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
            arg_name_values = self._get_args_dict(func, args, kwargs)
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
            arg_name_values = self._get_args_dict(func, args, kwargs)
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


class RequireArgs(_DecBase):
    """
    Decorator that defines required args for ``**kwargs`` of a function.

    See Also:
        :doc:`../../usage/Decorator/RequireArgs`
    """

    def __init__(self, *args: str, **kwargs):
        """
        Constructor

        Other Parameters:
            args (type): One or more names of wrapped function args to require.

        Keyword Arguments:
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
        """
        super().__init__(**kwargs)
        self._args = []
        for arg in args:
            if isinstance(arg, str):
                self._args.append(arg)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            arg_name_values = self._get_args_dict(func, args, kwargs)
            arg_keys = arg_name_values.keys()
            for key in self._args:
                if not key in arg_keys:
                    raise ValueError(f"'{key}' is a required arg.")
            return func(*args, **kwargs)
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


def calltracker(func):
    """
    Decorator method that adds ``has_been_called`` attribute to decorated method.
    ``has_been_called`` is ``False`` if method has not been called.
    ``has_been_called`` is ``True`` if method has been called.

    Note:
        This decorator needs to be the topmost decorator applied to a method

    Example:
        .. code-block:: python

            >>> @calltracker
            >>> def foo(msg):
            >>>     print(msg)

            >>> print(foo.has_been_called)
            False
            >>> foo("Hello World")
            Hello World
            >>> print(foo.has_been_called)
            True
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.has_been_called = True
        return func(*args, **kwargs)
    wrapper.has_been_called = False
    return wrapper


def callcounter(func):
    """
    Decorator method that adds ``call_count`` attribute to decorated method.
    ``call_count`` is ``0`` if method has not been called.
    ``call_count`` increases by 1 each time method is been called.

    Note:
        This decorator needs to be the topmost decorator applied to a method

    Example:
        .. code-block:: python

            >>> @callcounter
            >>> def foo(msg):
            >>>     print(msg)

            >>> print("Call Count:", foo.call_count)
            0
            >>> foo("Hello")
            Hello
            >>> print("Call Count:", foo.call_count)
            1
            >>> foo("World")
            World
            >>> print("Call Count:", foo.call_count)
            2
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.call_count += 1
        return func(*args, **kwargs)
    wrapper.call_count = 0
    return wrapper


def singleton(orig_cls):
    """
    Makes a class a singleton class

    Example:
        .. code-block:: python

            @singleton
            class Logger:
                def log(self, msg):
                    print(msg)

            logger1 = Logger()
            logger2 = Logger()
            assert logger1 is logger2
    """
    orig_new = orig_cls.__new__
    instance = None

    @functools.wraps(orig_cls.__new__)
    def __new__(cls, *args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = orig_new(cls, *args, **kwargs)
        return instance
    orig_cls.__new__ = __new__
    return orig_cls


class AutoFill:
    """
    Class decorator that replaces the ``__init__`` function with one that
    sets instance attributes with the specified argument names and
    default values. The original ``__init__`` is called with no arguments
    after the instance attributes have been assigned.

    Example:
        .. code-block:: python

            >>> @AutoFill('a', 'b', c=3)
            ... class Foo: pass
            >>> sorted(Foo(1, 2).__dict__.items())
            [('a', 1), ('b', 2), ('c', 3)]
    """
    # https://codereview.stackexchange.com/questions/142073/class-decorator-in-python-to-set-variables-for-the-constructor

    def __init__(self,  *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def __call__(self, cls):
        class Wrapped(cls):
            """Wrapped Class"""
        self._init(Wrapped)
        return Wrapped

    def _init(self, cls):
        argnames = self._args
        defaults = self._kwargs
        kind = Parameter.POSITIONAL_OR_KEYWORD
        signature = Signature(
            [Parameter(a, kind) for a in argnames]
            + [Parameter(k, kind, default=v) for k, v in defaults.items()])
        original_init = cls.__init__

        def init(self, *args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            for k, v in bound.arguments.items():
                setattr(self, k, v)
            original_init(self)

        cls.__init__ = init

class AutoFillKw:
    """
    Class decorator that replaces the ``__init__`` function with one that
    sets instance attributes with the specified key, value of ``kwargs``.
    The original ``__init__`` is called with any ``*args``
    after the instance attributes have been assigned.

    Example:
        .. code-block:: python

            >>> @AutoFillKw
            ... class Foo: pass
            >>> sorted(Foo(a=1, b=2, End="!").__dict__.items())
            [('End', '!'), ('a', 1), ('b', 2)]
    """
    def __init__(self, cls):
        self._cls = cls

    def __call__(self, *args, **kwargs):
        kind = Parameter.KEYWORD_ONLY
        signature = Signature(
            [Parameter(k, kind, default=v) for k, v in kwargs.items()])
        original_init = self._cls.__init__

        def init(self, *arguments, **kw):
            bound = signature.bind(**kw)
            bound.apply_defaults()
            for k, v in bound.arguments.items():
                setattr(self, k, v)
            original_init(self, *arguments)

        self._cls.__init__ = init
        return self._cls(*args, **kwargs)
