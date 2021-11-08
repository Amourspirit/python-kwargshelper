import enum
import functools
import inspect
import re
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union
from inspect import _ParameterKind, signature, isclass, Parameter, Signature
from ..checks import TypeChecker, RuleChecker, SubClassChecker
from ..rules import IRule
from ..helper import is_iterable
from ..exceptions import RuleError
from ..helper import NO_THING
from enum import Enum, IntEnum
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
    PROPERTY_CLASS = 5
    """Class Property (@property)"""

    def __str__(self):
        return self._name_


class _CommonBase(object):
    def __init__(self, **kwargs):
        """
        Constructor

        Keyword Arguments:
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
        """
        self._opt_return = kwargs.get("opt_return", NO_THING)

    def _is_opt_return(self) -> bool:
        """
        Gets if opt_return value has been set in constructor

        Returns:
            bool: True if opt_return value is set; Otherwise, False
        """
        return not self._opt_return is NO_THING


class _DecBase(_CommonBase):
    _rx_star = re.compile("^\*(\d*)$")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        self._cache = {}

    def _is_placeholder_arg(self, arg_name: str) -> bool:
        m = _DecBase._rx_star.match(arg_name)
        if m:
            return True
        return False

    def _drop_arg_first(self) -> bool:
        return self._ftype.value > DecFuncEnum.METHOD_STATIC.value

    def _get_args(self, args: Iterable[object]):
        if self._drop_arg_first():
            return args[1:]
        return args

    def _get_args_star(self, func: callable, args: Iterable[object]) -> Iterable[object]:
        """
        Get args accounting for ``*args`` postions in function and if function class method.

        Args:
            func (callable): function with args
            args (Iterable[object]): function current args

        Returns:
            Iterable[object]: New args that may be a subset of all of orignial ``args``.
        """
        pos = self._get_star_args_pos(func)
        drop_first = self._drop_arg_first()
        i = 0
        if pos > 0:
            i += pos
        if drop_first:
            i += 1
        if i > 0:
            return args[i:]
        return args

    def _get_signature(self, func) -> Signature:
        sig = self._cache.get("signature", False)
        if sig:
            return sig
        self._cache["signature"] = signature(func)
        return self._cache["signature"]

    def _get_args_dict(self, func: callable, fn_args: Iterable[object], fn_kwargs: Dict[str, object], **kwargs) -> Dict[str, object]:
        """
        [summary]

        Args:
            func (callable): Wrapped Function
            fn_args (Iterable[object]): Wrapped function *args
            fn_kwargs (Dict[str, object]): Wrapped function **kwargs

        Keyword Arguments:
            error_check (bool, optional): Determinse if errors are raise if there are missing
                keywords. This is the case when function has keywords without defaults assigned
                and no value is passed into function.

        Returns:
            Dict[str, object]: Dictionary of keys and values representing ``func`` keywords and values.
        """
        # Positional argument cannot appear after keyword arguments
        # no *args after **kwargs def foo(**kwargs, *args) not valid
        # def foo(name, age, *args) not valid
        #
        # When only args are passed in (no **kwargs present) with named args then
        # the last named args with defaults are like additional args
        error_check = kwargs.get("error_check", True)
        sig = self._get_signature(func)
        name_values = []
        i = 0
        args_pos = -1
        drop_first = self._drop_arg_first()
        for k, v in sig.parameters.items():
            if v.kind == _ParameterKind.VAR_POSITIONAL:  # args
                args_pos = i
                if drop_first:
                    args_pos -= 1
                continue
            if v.kind == _ParameterKind.VAR_KEYWORD:  # kwargs
                continue
            if not v.default is inspect._empty:
                name_values.append((k, v.default))
            else:
                name_values.append((k, NO_THING))
            i += 1
        arg_offset = 0 if args_pos == -1 else args_pos
        if drop_first and len(fn_args) > arg_offset:
            _args = fn_args[(arg_offset + 1):]
        else:
            _args = fn_args[arg_offset:]
        arg_len = len(_args)
        name_values_len = len(name_values)
        if drop_first and name_values_len > 0:
            del name_values[0]
            name_values_len -= 1
        offset = 0
        if args_pos >= 0 and name_values_len > 0:
            # count how many name, values from default
            # are default values
            reversed_list = list(reversed(name_values))
            for k, v in reversed_list:
                if not v is NO_THING:
                    offset += 1
                else:
                    break

        name_defaults = {}
        # add first keys of name_values
        if args_pos > 0:
            # there are name values before *args in function
            # add first args so they are in the same order as entered.
            for j in range(args_pos):
                nv = name_values[j]
                name_defaults[nv[0]] = nv[1]
        # add args
        if args_pos >= 0:
            # add args that are positional arguments
            for j, arg in enumerate(_args):
                key = "*" + str(j + arg_offset)
                name_defaults[key] = arg

        if args_pos > 0:
            # add any remaining keys for name_values
            remaining = len(name_values) - args_pos
            if remaining > 0:
                for j in range(remaining):
                    index = j + args_pos
                    nv = name_values[index]
                    name_defaults[nv[0]] = nv[1]
        else:
            # there were no positional args before *args keyword so
            # all all the name, values after postitioan args.
            for k, v in name_values:
                name_defaults[k] = v
        if args_pos != 0 and arg_len > 0:
            # if *args are not in position 0 and there are *args then
            # make a dictionary of name values and update the
            # name_defaults dictionary.
            argnames = []
            for j in range(len(name_values) - offset):
                el = name_values[j]
                argnames.append(el[0])
            if drop_first:
                _zip_args = fn_args[1:]
            else:
                _zip_args = fn_args
            d = {**dict(zip(argnames, _zip_args[:len(argnames)]))}
            name_defaults.update(d)
        if len(fn_kwargs) > 0:
            # update name_default with any kwargs that are passed in.
            # this will update any default values with the values passed
            # into function at call time.
            name_defaults.update(fn_kwargs)
        if error_check is True:
            # if any arg has a value of NO_THING then it is a missing arg.
            # if no error is raise here then python will raise TypeError such as:
            # TypeError: foo() missing 1 required positional argument: 'end'
            missing_args = []
            for k, v in name_defaults.items():
                if v is NO_THING:
                    missing_args.append(k)
            self._missing_args_error(func=func, missing_names=missing_args)
        return name_defaults

    def _missing_args_error(self, func: callable, missing_names: List[str]):
        missing_names_len = len(missing_names)
        if missing_names_len == 0:
            return
        msg = f"{func.__name__}() missing {missing_names_len} required positional"
        if missing_names_len == 1:
            msg = msg + " argument: "
        else:
            msg = msg + " arguments: "
        msg = msg +  self._get_formated_names(names=missing_names)
        msg = msg + self._get_class_dec_err()
        raise TypeError(msg)

    def _get_formated_names(self, names: List[str], **kwargs) -> str:
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
        wrapper = kwargs.get("wrapper","'")
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
                
    def _get_formated_types(self, types: Iterator[type], **kwargs) -> str:
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
        result = self._get_formated_names(names=t_names, **kwargs)
        return result

    def _get_ordinal(self, num: int) -> str:
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

    def _get_star_args_pos(self, func: callable) -> int:
        """
        Gets the zero base postion of *args in a function.

        Args:
            func (callable): function to get *args postion of.

        Returns:
            int: -1 if  *args not present; Otherwise zero based postion of *args
        """
        result = self._cache.get("star_args_pos", None)
        if not result is None:
            return result
        sig = self._get_signature(func)
        args_pos = -1
        drop_first = self._drop_arg_first()
        i = 0
        for k, v in sig.parameters.items():
            if v.kind == _ParameterKind.VAR_POSITIONAL:  # args
                args_pos = i
                if drop_first:
                    args_pos -= 1
                break
            i += 1
        self._cache["star_args_pos"] = args_pos
        return self._cache["star_args_pos"]

    def _get_class_dec_err(self, **kwargs) -> str:
        """
        Gets a string representing class decorator error.

        Keyword Args:
            nl (bool, optional): Determines if new line is prepended to return value. Default ``True``

        Returns:
            str: Formated string similar to ``SubClass decorator error.``
        """
        nl = kwargs.get('nl', True)
        result = ""
        if nl:
            result = result + '\n'
        result = result + f"{self.__class__.__name__} decorator error."
        return result

class _RuleBase(_DecBase):
    def _get_err(self, fn: callable, e: RuleError):
        err = RuleError.from_rule_error(e, fn_name=fn.__name__, msg=self._get_class_dec_err(nl=False))
        return err


class TypeCheck(_DecBase):
    """
    Decorator that decorates methods that requires args to match a type specificed in a list

    See Also:
        :doc:`../../usage/Decorator/TypeCheck`
    """

    def __init__(self, *args: Union[type, Iterable[type]], **kwargs):
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
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.

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
            try:
                is_valid = self._typechecker.validate(*_args, **kwargs)
                if self._typechecker.raise_error is False:
                    wrapper.is_types_valid = is_valid
                if is_valid is False and self._is_opt_return() is True:
                    return self._opt_return
            except TypeError as e:
                if self._is_opt_return():
                    return self._opt_return
                msg = str(e)
                msg = msg + self._get_class_dec_err()
                raise TypeError(msg)
            return func(*args, **kwargs)
        if self._typechecker.raise_error is False:
            wrapper.is_types_valid = True
        return wrapper

    @property
    def _typechecker(self) -> TypeChecker:
        if self._tc is None:
            self._tc = TypeChecker(*self._types, **self._kwargs)
        return self._tc


class AcceptedTypes(_DecBase):
    """
    Decorator that decorates methods that requires args to match types specificed in a list

    See Also:
        :doc:`../../usage/Decorator/AcceptedTypes`
    """

    def __init__(self, *args: Union[type, Iterable[type]], **kwargs):
        """
        Constructor

        Other Parameters:
            args (Union[type, Iterable[type]]): One or more types or Iterator[type] for validation.

        Keyword Arguments:
            type_instance_check (bool, optional): If ``True`` then args are tested also for ``isinstance()``
                if type does not match, rather then just type check. If ``False`` then values willl only be
                tested as type.
                Default ``True``
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
            opt_all_args (bool, optional): If ``True`` then the last subclass type passed into constructor will
                define any remaining args. This allows for one subclass to define required match of all arguments
                that decorator is applied to.
                Default ``False``
        """
        super().__init__(**kwargs)
        self._tc = None
        self._types = []
        ex_iterable_types = (Enum, str)
        for arg in args:
            if is_iterable(arg=arg, excluded_types=ex_iterable_types):
                arg_set = set()
                for arg_itm in arg:
                    arg_set.add(arg_itm)
                self._types.append(arg_set)
            else:
                self._types.append(tuple([arg]))
        if kwargs:
            # keyword args are passed to TypeChecker
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}
        self._all_args = bool(kwargs.get("opt_all_args", False))

    def _get_formated_types(self, types: Union[Tuple[type], Set[type]]) -> str:
        # multi is list of set, actually one set in a list
        # single is a tuple of a single type.
        # these types are set in constructor.
        if isinstance(types, tuple):
            return f"'{types[0].__name__}'"
        lst_multi = [t.__name__ for t in types]
        result = self._get_formated_names(names=lst_multi,
                                          conj='or')
        return result

    def _get_inst(self, types: Iterable[type]):
        return TypeChecker(*types, **self._kwargs)

    def _validate(self, func: callable, key: str, value: object, types: Iterable[type], arg_index: int, inst: SubClassChecker = None):
        if inst is None:
            tc = self._get_inst(types=types)
        else:
            tc = inst
        if self._is_placeholder_arg(key):
            try:
                tc.validate(value)
            except TypeError:
                if self._is_opt_return():
                    return self._opt_return
                raise TypeError(self._get_err_msg(name=None, value=value,
                                                    types=types, arg_index=arg_index,
                                                    fn=func))
        else:
            try:
                tc.validate(**{key: value})
            except TypeError:
                if self._is_opt_return():
                    return self._opt_return
                raise TypeError(self._get_err_msg(name=key, value=value,
                                                    types=types, arg_index=arg_index,
                                                    fn=func))
        return NO_THING

    def __call__(self, func: callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            arg_name_values = self._get_args_dict(
                func=func, fn_args=args, fn_kwargs=kwargs)
            arg_keys = list(arg_name_values.keys())
            arg_keys_len = arg_keys.__len__()
            if arg_keys_len is not len(self._types):
                if self._all_args is False:
                    if self._is_opt_return():
                        return self._opt_return
                    msg = 'Invalid number of arguments for {0}()'.format(
                        func.__name__)
                    msg = msg + self._get_class_dec_err()
                    raise ValueError(msg)
            arg_type = zip(arg_keys, self._types)
            i = 0
            for arg_info in arg_type:
                key = arg_info[0]
                result = self._validate(func=func, key=key,
                                        value=arg_name_values[key],
                                        types=arg_info[1], arg_index=i)
                if not result is NO_THING:
                    return result
                i += 1
            if arg_keys_len > i:
                # this only happens when _all_args is True
                # at this point remain args should match last last type in self._types
                r_args = arg_keys[i:]
                types = self._types[len(self._types) - 1] # tuple or set
                sc = self._get_inst(types=types)
                for r_arg in r_args:
                    result = self._validate(func=func, key=r_arg,
                                            value=arg_name_values[r_arg],
                                            types=types, arg_index=i,
                                            inst=sc)
                    if not result is NO_THING:
                        return result
                    i += 1
            return func(*args, **kwargs)
        return wrapper

    def _get_err_msg(self, name: Union[str, None], value: object, types: Iterator[type], arg_index: int, fn: callable):
        str_types = self._get_formated_types(types=types)
        str_ord = self._get_ordinal(arg_index + 1)
        if self._ftype == DecFuncEnum.PROPERTY_CLASS:
            msg = f"'{fn.__name__}' property error. Arg '{name}' expected type of {str_types} but got '{type(value).__name__}'."
            return msg
        if name:
            msg = f"Arg '{name}' in {str_ord} position is expected to be of {str_types} but got '{type(value).__name__}'."
        else:
            msg = f"Arg in {str_ord} position of is expected to be of {str_types} but got '{type(value).__name__}'."
        msg = msg + self._get_class_dec_err()
        return msg


class ArgsLen(_DecBase):
    """
    Decorartor that sets the number of args that can be added to a function

    Raises:
        ValueError: If wrong args are passed into construcor.
        ValueError: If validation of arg count fails.

    See Also:
        :doc:`../../usage/Decorator/ArgsLen`
    """

    def __init__(self, *args: Union[type, Iterable[type]], **kwargs):
        """
        Constructor

        Other Parameters:
            args (Union[int, iterable[int]]): One or more int or Iterator[int] for validation.

                * Single ``int`` values are to match exact.
                * ``iterable[int]`` must be a pair of ``int`` with the first ``int`` less then the second ``int``.

        Keyword Arguments:
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
        """
        super().__init__(**kwargs)
        self._ranges: Set[Tuple[int, int]] = set()
        self._lengths: Set[int] = set()
        for arg in args:
            if isinstance(arg, int):
                if arg >= 0:
                    self._lengths.add(arg)
            elif is_iterable(arg) and len(arg) == 2:
                arg1 = arg[0]
                arg2 = arg[1]
                if isinstance(arg1, int) and isinstance(arg2, int) \
                        and arg1 >= 0 and arg2 > arg1:
                    self._ranges.add((arg1, arg2))
        valid = len(self._lengths) > 0 or len(self._ranges) > 0
        if not valid:
            msg = f"{self.__class__.__name__} error. constructor must have valid args of of postive int and/or postive pairs of int."
            msg = msg + self._get_class_dec_err()
            raise ValueError(msg)

    def _get_valid_counts(self) -> str:
        str_len = ""
        str_rng = ""
        len_lengths = len(self._lengths)
        len_ranges = len(self._ranges)
        if len_lengths > 0:
            str_len = self._get_formated_names(
                names=sorted(self._lengths), conj='or')
        if len_ranges > 0:
            str_rng = self._get_formated_names(
                names=sorted(self._ranges), conj='or', wrapper="")
        result = ""
        
        if len_lengths > 0:
            if len_lengths == 1:
                result = result + "Expected Length: "
            else:
                result = result + "Expected Lengths: "
            result = result + f"{str_len}."
        if len_ranges > 0:
            if len_lengths > 0:
                result = result + " "
            if len_ranges == 1:
                result = result + "Expected Range: "
            else:
                result = result + "Expected Ranges: "
            result = result + str_rng + "."
        return result

    def __call__(self, func: callable):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _args = self._get_args_star(func=func, args=args)
            _args_len = len(_args)
            is_valid = False
            if _args_len >= 0:
                for i in self._lengths:
                    if _args_len == i:
                        is_valid = True
                        break
                if is_valid is False:
                    for range in self._ranges:
                        if _args_len >= range[0] and _args_len <= range[1]:
                            is_valid = True
                            break
            if is_valid is False:
                if self._is_opt_return():
                    return self._opt_return
                msg = f"Invalid number of args pass into '{func.__name__}'.\n{self._get_valid_counts()}"
                msg = msg + f" Got '{_args_len}' args."
                msg = msg + self._get_class_dec_err()
                raise ValueError(msg)
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper


class ArgsMinMax(_DecBase):
    """
    Decorartor that sets the min and or max number of args that can be added to a function


    See Also:
        :doc:`../../usage/Decorator/ArgsMinMax`
    """

    def __init__(self, min: Optional[int] = 0, max: Optional[int] = None, **kwargs):
        """
        Constructor

        Args:
            min (int, optional): Min number of args for a function. Defaults to 0.
            max (int, optional): Max number of args for a function. Defaults to None.

        Keyword Arguments:
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
        """
        super().__init__(**kwargs)
        self._min = int(min)
        if isinstance(max, int):
            self._max = max
        else:
            self._max = None

    def _get_min_max(self) -> Tuple[int, int]:
        _max = -1 if self._max is None else self._max
        _min = self._min
        return _min, _max

    def _get_valid_counts(self) -> str:

        _min, _max = self._get_min_max()
        msg = ""
        if _min > 0:
            msg = msg + "Expected min of '" + str(_min) + "'."
        if _max >= 0:
            if _min > 0:
                msg = msg + " "
            msg = msg + "Expected max of '" + str(_max) + "'."
        return msg

    def _get_error_msg(self, func: callable, args_len: int) -> str:
        msg = f"Invalid number of args pass into '{func.__name__}'.\n{self._get_valid_counts()}"
        msg = msg + f" Got '{args_len}' args."
        msg = msg + self._get_class_dec_err()
        return msg

    def __call__(self, func: callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _min, _max = self._get_min_max()
            has_rules = _min > 0 or _max >= 0
            if has_rules:
                _args = self._get_args_star(func=func, args=args)
                _args_len = len(_args)
                is_valid = True
                if _min > 0:
                    if _args_len < _min:
                        is_valid = False
                if is_valid == True and _max >= 0:
                    if _args_len > _max:
                        is_valid = False
                if is_valid is False:
                    if self._is_opt_return():
                        return self._opt_return
                    raise ValueError(self._get_error_msg(
                        func=func, args_len=_args_len))
            return func(*args, **kwargs)
        # wrapper.is_types_valid = self.is_valid
        return wrapper


class ReturnRuleAll(_RuleBase):
    """
    Decorator that decorates methods that require return value to match all rules specificed.

    See Also:
        :doc:`../../usage/Decorator/ReturnRuleAll`
    """

    def __init__(self, *args: IRule, **kwargs):
        """
        Constructor

        Args:
            args (IRule): One or more rules to use for validation
        Keyword Arguments:
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
                Default ``True``
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
        """
        super().__init__(**kwargs)
        self._rc = None
        self._rules = [arg for arg in args]
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func: callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return_value = func(*args, **kwargs)
            rc = self._rulechecker
            try:
                rc.validate_all(**{"return": return_value})
            except RuleError as e:
                if self._is_opt_return():
                    return self._opt_return
                err = self._get_err(fn=func, e=e)
                raise err
            return return_value
        return wrapper

    @property
    def _rulechecker(self) -> RuleChecker:
        if self._rc is None:
            self._rc = RuleChecker(rules_all=self._rules, **self._kwargs)
            self._rc.raise_error = True
        return self._rc


class ReturnRuleAny(_RuleBase):
    """
    Decorator that decorates methods that require return value to match any of the rules specificed.

    See Also:
        :doc:`../../usage/Decorator/ReturnRuleAny`
    """

    def __init__(self, *args: IRule, **kwargs):
        """
        Constructor

        Args:
            args (IRule): One or more rules to use for validation
        Keyword Arguments:
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
        """
        super().__init__(**kwargs)
        self._rc = None
        self._rules = [arg for arg in args]
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func: callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return_value = func(*args, **kwargs)
            rc = self._rulechecker
            # rc.current_arg = "return"
            try:
                rc.validate_any(**{"return": return_value})
            except RuleError as e:
                if self._is_opt_return():
                    return self._opt_return
                err = self._get_err(fn=func, e=e)
                raise err
            return return_value
        return wrapper

    @property
    def _rulechecker(self) -> RuleChecker:
        if self._rc is None:
            self._rc = RuleChecker(rules_any=self._rules, **self._kwargs)
            self._rc.raise_error = True
        return self._rc


class ReturnType(_DecBase):
    """
    Decorator that decorates methods that require return value to match a type specificed.

    See Also:
        :doc:`../../usage/Decorator/ReturnType`
    """

    def __init__(self, *args: type, **kwargs):
        """
        Constructor

        Args:
            args (type): One ore more types that is used to validate return type.

        Keyword Arguments:
            type_instance_check (bool, optional): If ``True`` then args are tested also for ``isinstance()``
                if type does not match, rather then just type check. If ``False`` then values willl only be
                tested as type.
                Default ``True``
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
        """
        super().__init__(**kwargs)
        self._tc = None
        self._types = [*args]
        if kwargs:
            # keyword args are passed to TypeChecker
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func: callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return_value = func(*args, **kwargs)
            try:
                self._typechecker.validate(return_value)
            except TypeError:
                if self._is_opt_return():
                    return self._opt_return
                # catch type error and raise a new one so a more fitting message is raised.
                raise TypeError(self._get_err_msg(return_value))
            return return_value
        return wrapper

    def _get_err_msg(self, value: object):
        str_types = self._get_formated_types(self._types, conj='or')
        msg = f"Return Value is expected to be of {str_types} but got '{type(value).__name__}'."
        msg = msg + self._get_class_dec_err()
        return msg

    @property
    def _typechecker(self) -> TypeChecker:
        if self._tc is None:
            self._tc = TypeChecker(*self._types, **self._kwargs)
            # ensure errors are raised if not valid
            self._tc.raise_error = True
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
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
        """
        super().__init__(**kwargs)
        self._raise_error = bool(kwargs.get("raise_error", True))
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
            arg_name_values = self._get_args_dict(
                func=func, fn_args=args, fn_kwargs=kwargs)
            arg_keys = arg_name_values.keys()
            tc = False
            for key in self._arg_index.keys():
                if key in arg_keys:
                    is_valid = False
                    types = self._get_types(key=key)
                    if len(types) == 0:
                        continue
                    value = arg_name_values[key]
                    tc = TypeChecker(*types, **self._kwargs)
                    try:
                        is_valid = tc.validate(**{key: value})
                        if is_valid is False:
                            break
                    except TypeError as e:
                        if self._is_opt_return():
                            return self._opt_return
                        msg = str(e)
                        msg = msg + self._get_class_dec_err()
                        raise TypeError(msg)
            if tc and tc.raise_error is False:
                wrapper.is_types_kw_valid = is_valid
                if is_valid == False and self._is_opt_return() == True:
                    return self._opt_return
            return func(*args, **kwargs)
        if self._raise_error is False:
            wrapper.is_types_kw_valid = True
        return wrapper


class RuleCheckAny(_RuleBase):
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
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
        """
        super().__init__(**kwargs)
        self._raise_error = bool(kwargs.get("raise_error", True))
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
            is_valid = False
            try:
                is_valid = self._rulechecker.validate_any(*_args, **kwargs)
            except RuleError as err:
                if self._is_opt_return():
                    return self._opt_return
                err_rule = self._get_err(fn=func, e=err)
                raise err_rule
            if self._raise_error is False:
                wrapper.is_rules_any_valid = is_valid
                if is_valid == False and self._is_opt_return() == True:
                    return self._opt_return
            return func(*args, **kwargs)
        if self._raise_error is False:
            wrapper.is_rules_any_valid = True
        return wrapper

    @property
    def _rulechecker(self) -> RuleChecker:
        if self._rc is None:
            self._rc = RuleChecker(rules_any=self._rules, **self._kwargs)
        return self._rc


class RuleCheckAll(_RuleBase):
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
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
        """
        super().__init__(**kwargs)
        self._raise_error = bool(kwargs.get("raise_error", True))
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
            is_valid = False
            try:
                is_valid = self._rulechecker.validate_all(*_args, **kwargs)
            except RuleError as err:
                if self._is_opt_return():
                    return self._opt_return
                err_rule = self._get_err(fn=func, e=err)
                raise err_rule
            if self._rulechecker.raise_error is False:
                wrapper.is_rules_all_valid = is_valid
                if is_valid == False and self._is_opt_return() == True:
                    return self._opt_return
            return func(*args, **kwargs)
        if self._raise_error is False:
            wrapper.is_rules_all_valid = True
        return wrapper

    @property
    def _rulechecker(self) -> RuleChecker:
        if self._rc is None:
            self._rc = RuleChecker(rules_all=self._rules, **self._kwargs)
        return self._rc


class RuleCheckAllKw(_RuleBase):
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
            raise_error (bool, optional): If ``True`` then an Exception will be raised if a
                validation fails. The kind of exception raised depends on the rule that is
                invalid. Typically a ``TypeError`` or a ``ValueError`` is raised.

                If ``False`` then an attribute will be set on decorated function
                named ``is_rules_kw_all_valid`` indicating if validation status.
                Default ``True``.
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
        """
        super().__init__(**kwargs)
        self._raise_error = bool(kwargs.get("raise_error", True))
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
            arg_name_values = self._get_args_dict(
                func=func, fn_args=args, fn_kwargs=kwargs)
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
                    is_valid = False
                    try:
                        is_valid = rc.validate_all(**{key: value})
                    except RuleError as err:
                        if self._is_opt_return():
                            return self._opt_return
                        err_rule = self._get_err(fn=func, e=err)
                        raise err_rule
                    if is_valid is False:
                        break
            if add_attrib:
                wrapper.is_rules_kw_all_valid = is_valid
                if is_valid == False and self._is_opt_return() == True:
                    return self._opt_return
            return func(*args, **kwargs)
        if self._raise_error is False:
            wrapper.is_rules_kw_all_valid = True
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
            arg_name_values = self._get_args_dict(
                func=func, fn_args=args, fn_kwargs=kwargs)
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
                        add_attrib = not self._raise_error
                    is_valid = False
                    try:
                        is_valid = rc.validate_any(**{key: value})
                    except RuleError as err:
                        if self._is_opt_return():
                            return self._opt_return
                        err_rule = self._get_err(fn=func, e=err)
                        raise err_rule
                    if is_valid is False:
                        break
            if add_attrib:
                wrapper.is_rules_any_valid = is_valid
                if is_valid == False and self._is_opt_return() == True:
                    return self._opt_return
            return func(*args, **kwargs)
        if self._raise_error is False:
            wrapper.is_rules_any_valid = True
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
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
        """
        super().__init__(**kwargs)
        self._args = []
        for arg in args:
            if isinstance(arg, str):
                self._args.append(arg)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            arg_name_values = self._get_args_dict(
                func=func, fn_args=args, fn_kwargs=kwargs)
            arg_keys = arg_name_values.keys()
            for key in self._args:
                if not key in arg_keys:
                    if self._is_opt_return():
                        return self._opt_return
                    raise ValueError(
                        f"'{func.__name__}', '{key}' is a required arg.")
            return func(*args, **kwargs)
        return wrapper


class DefaultArgs(_CommonBase):
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
        super().__init__(**kwargs)
        self._kwargs = {**kwargs}

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

    See Also:
        :doc:`../../usage/Decorator/calltracker`
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

    See Also:
        :doc:`../../usage/Decorator/callcounter`
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.call_count += 1
        return func(*args, **kwargs)
    wrapper.call_count = 0
    return wrapper


def singleton(orig_cls):
    """
    Decorator that makes a class a singleton class

    Example:
        .. code-block:: python

            @singleton
            class Logger:
                def log(self, msg):
                    print(msg)

            logger1 = Logger()
            logger2 = Logger()
            assert logger1 is logger

    See Also:
        :doc:`../../usage/Decorator/singleton`
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


class SubClass(_DecBase):
    """
    Decorator that requires args of a function to match or be a subclass of types specificed in constructor.

    See Also:
        :doc:`../../usage/Decorator/SubClass`
    """

    def __init__(self, *args: Union[type, Iterable[type]], **kwargs):
        """
        Constructor

        Other Parameters:
            args (Union[type, Iterable[type]]): One or more types or Iterator[type] for validation.

        Keyword Arguments:
            type_instance_check (bool, optional): If ``True`` then args are tested also for ``isinstance()``
                if type does not match, rather then just type check. If ``False`` then values willl only be
                tested as type.
                Default ``True``
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
            opt_inst_only (bool, optional): If ``True`` then validation will requires all values being tested to be an
                instance of a class. If ``False`` valadition will test class instance and class type.
                Default ``True``
            opt_all_args (bool, optional): If ``True`` then the last subclass type passed into constructor will
                define any remaining args. This allows for one subclass to define required match of all arguments
                that decorator is applied to.
                Default ``False``
        """
        super().__init__(**kwargs)
        self._types = []
        ex_iterable_types = (Enum, str)
        for arg in args:
            if is_iterable(arg=arg, excluded_types=ex_iterable_types):
                arg_set = set()
                for arg_itm in arg:
                    arg_set.add(arg_itm)
                self._types.append(arg_set)
            else:
                self._types.append(tuple([arg]))
        if kwargs:
            # keyword args are passed to TypeChecker
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}
        self._all_args = bool(kwargs.get("opt_all_args", False))

    def _get_formated_types(self, types: Union[Tuple[type], Set[type]]) -> str:
        # multi is list of set, actually one set in a list
        # single is a tuple of a single type.
        # these types are set in constructor.
        if isinstance(types, tuple):
            return f"'{types[0].__name__}'"
        lst_multi = [t.__name__ for t in types]
        result = self._get_formated_names(names=lst_multi,
                                          conj='or')
        return result

    def _get_inst(self, types: Iterable[type]):
        return SubClassChecker(*types, **self._kwargs)

    def _validate(self, func: callable, key: str, value: object, types: Iterable[type], arg_index: int, inst: SubClassChecker = None):
        if inst is None:
            sc = self._get_inst(types=types)
        else:
            sc = inst
        # ensure errors are raised if not valid
        sc.raise_error = True
        if self._is_placeholder_arg(key):
            try:
                sc.validate(value)
            except TypeError:
                if self._is_opt_return():
                    return self._opt_return
                raise TypeError(self._get_err_msg(name=None, value=value,
                                                  types=types, arg_index=arg_index,
                                                  fn=func))
        else:
            try:
                sc.validate(**{key: value})
            except TypeError:
                if self._is_opt_return():
                    return self._opt_return
                raise TypeError(self._get_err_msg(name=key, value=value,
                                                  types=types, arg_index=arg_index,
                                                  fn=func))
        return NO_THING

    def __call__(self, func: callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            arg_name_values = self._get_args_dict(
                func=func, fn_args=args, fn_kwargs=kwargs)
            arg_keys = list(arg_name_values.keys())
            arg_keys_len = arg_keys.__len__()
            if self._all_args is False:
                if arg_keys_len is not len(self._types):
                    if self._is_opt_return():
                        return self._opt_return
                    msg = 'Invalid number of arguments for {0}()'.format(
                        func.__name__)
                    msg = msg + self._get_class_dec_err()
                    raise ValueError(msg)
            arg_type = zip(arg_keys, self._types)
            i = 0
            for arg_info in arg_type:
                key = arg_info[0]
                result = self._validate(func=func, key=key,
                                        value=arg_name_values[key],
                                        types=arg_info[1], arg_index=i)
                if not result is NO_THING:
                    return result
                i += 1
            if arg_keys_len > i:
                # this only happens when _all_args is True
                # at this point remain args should match last last type in self._types
                r_args = arg_keys[i:]
                types = self._types[len(self._types) - 1]  # tuple or set
                sc = self._get_inst(types=types)
                for r_arg in r_args:
                    result = self._validate(func=func, key=r_arg,
                                            value=arg_name_values[r_arg],
                                            types=types, arg_index=i,
                                            inst=sc)
                    if not result is NO_THING:
                        return result
                    i += 1

            return func(*args, **kwargs)
        return wrapper

    def _get_err_msg(self, name: Union[str, None], value: object, types: Iterator[type], arg_index: int, fn: callable):
        str_types = self._get_formated_types(types=types)
        str_ord = self._get_ordinal(arg_index + 1)
        if self._ftype == DecFuncEnum.PROPERTY_CLASS:
            msg = f"'{fn.__name__}' property error. Arg '{name}' expected is expected be a subclass of {str_types}."
            return msg
        if name:
            msg = f"Arg '{name}' is expected be a subclass of {str_types}."
        else:
            msg = f"Arg in {str_ord} position is expected to be of a subclass of {str_types}."
        msg = msg + self._get_class_dec_err()
        return msg


class SubClasskKw(_DecBase):
    """
    Decorator that requires args of a function to match or be a subclass of types specificed in constructor.

    See Also:
        :doc:`../../usage/Decorator/SubClasskKw`
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
            type_instance_check (bool, optional): If ``True`` then args are tested also for ``isinstance()``
                if type does not match, rather then just type check. If ``False`` then values willl only be
                tested as type. Default ``True``
            ftype (DecFuncType, optional): Type of function that decorator is applied on.
                Default ``DecFuncType.FUNCTION``
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
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
        # set rais_error for SubClassChecker as this class does not support this option.
        self._kwargs['raise_error'] = True

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
            arg_name_values = self._get_args_dict(
                func=func, fn_args=args, fn_kwargs=kwargs)
            arg_keys = arg_name_values.keys()
            sc = False
            for key in self._arg_index.keys():
                if key in arg_keys:
                    is_valid = False
                    types = self._get_types(key=key)
                    if len(types) == 0:
                        continue
                    value = arg_name_values[key]
                    sc = SubClassChecker(*types, **self._kwargs)
                    try:
                        # error_raise is always True for sc.
                        # for this reason no need to capture results of validate.
                        sc.validate(**{key: value})
                    except TypeError as e:
                        if self._is_opt_return():
                            return self._opt_return
                        msg = str(e)
                        msg = msg + self._get_class_dec_err()
                        raise TypeError(msg)
            return func(*args, **kwargs)
        return wrapper
