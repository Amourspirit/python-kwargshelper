import functools
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union
from enum import Enum, IntEnum, IntFlag, auto
from collections import OrderedDict
from inspect import signature, isclass, Parameter, Signature
from logging import Logger
from ..checks import TypeChecker, RuleChecker, SubClassChecker
from ..rules import IRule
from ..helper import is_iterable, Formatter
from ..exceptions import RuleError
from ..helper import NO_THING
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


class DecArgEnum(IntFlag):
    """Represents options for the type of function arguments to process"""
    ARGS = auto()
    """Process ``*args``"""
    KWARGS = auto()
    """Process ``**kwargs``"""
    NAMED_ARGS = auto()
    """Process named keyword args"""
    NO_ARGS = NAMED_ARGS | KWARGS
    """Process Named Keyword args and ``**kwargs`` only"""
    All_ARGS = ARGS | KWARGS | NAMED_ARGS
    """Process All Args"""


class _FuncInfo(object):
    # foo(*args)
    #   assert info.index_args == 0
    #   assert info.index_kwargs == -1
    #   assert len(info.lst_kw_only) == 0
    #   assert len(info.lst_pos_only) == 0
    #   assert len(info.lst_pos_or_kw) == 0
    #
    # foo(**kwargs)
    #   assert info.index_args == -1
    #   assert info.index_kwargs == 0
    #   assert len(info.lst_kw_only) == 0
    #   assert len(info.lst_pos_only) == 0
    #   assert len(info.lst_pos_or_kw) == 0
    #
    # foo(one, two, three, four)
    #   assert info.index_args == -1
    #   assert info.index_kwargs == -1
    #   assert len(info.lst_kw_only) == 0
    #   assert len(info.lst_pos_only) == 0
    #   self.assertListEqual(info.lst_pos_or_kw, ['one', 'two', 'three', 'four'])
    #
    # foo(one, two, three, four, **kwargs)
    #   assert info.index_args == -1
    #   assert info.index_kwargs == 4
    #   assert len(info.lst_kw_only) == 0
    #   assert len(info.lst_pos_only) == 0
    #   self.assertListEqual(info.lst_pos_or_kw, ['one', 'two', 'three', 'four'])
    #
    # foo(*args, one, two, three, four, **kwargs)
    #   assert info.index_args == 0
    #   assert info.index_kwargs == 5
    #   self.assertListEqual(info.lst_kw_only, ['one', 'two', 'three', 'four'])
    #   assert len(info.lst_pos_only) == 0
    #   assert len(info.lst_pos_or_kw) == 0
    #
    # foo(neg_two, neg_one, *args, one, two, three, four, **kwargs)
    #   assert info.index_args == 2
    #   assert info.index_kwargs == 7
    #   self.assertListEqual(info.lst_kw_only, ['one', 'two', 'three', 'four'])
    #   assert len(info.lst_pos_only) == 0
    #   self.assertListEqual(info.lst_pos_or_kw, ['neg_two', 'neg_one'])

    # region init
    def __init__(self, func: callable, ftype: DecFuncEnum):
        self._len_pos_only = None
        self._len_kw_only = None
        self._len_pos_or_kw = None
        self._all_keys: Union[None, Tuple[str]] = None
        self.index_args: int = -1
        self.index_kwargs = -1
        self.lst_pos_only: List[str] = []
        self.lst_kw_only: List[str] = []
        self.lst_pos_or_kw: List[str] = []
        self.signature: Signature = signature(func)
        self._name = func.__name__
        self.ftype = ftype
        self._defaults = {}

        self._set_info()

    def _drop_arg_first(self) -> bool:
        return self.ftype.value > DecFuncEnum.METHOD_STATIC.value

    def _set_info(self):
        drop_first = self._drop_arg_first()
        i = 0
        for k, v in self.signature.parameters.items():
            if drop_first and i == 0:
                i += 1
                continue
            if v.kind == v.VAR_POSITIONAL:  # args
                self.index_args = i
                if drop_first:
                    self.index_args -= 1
            elif v.kind == v.VAR_KEYWORD:  # kwargs
                self.index_kwargs = i
                if drop_first:
                    self.index_kwargs -= 1
            elif v.kind == v.KEYWORD_ONLY:
                self.lst_kw_only.append(v.name)
                if v.default != v.empty:
                    self._defaults[k] = v.default
            elif v.kind == v.POSITIONAL_ONLY:  # pragma: no cover
                self.lst_pos_only.append(v.name)
                if v.default != v.empty:
                    self._defaults[k] = v.default
            elif v.kind == v.POSITIONAL_OR_KEYWORD:
                self.lst_pos_or_kw.append(v.name)
                if v.default != v.empty:
                    self._defaults[k] = v.default
            i += 1
    # endregion init

    # region public Methods
    def is_default(self, key: str) -> bool:
        """Gets if key exist in defaults"""
        return key in self._defaults
    # endregion public Methods

    # region Property
    @property
    def defauts(self) -> Dict[str, Any]:
        """Defalut value for any args that has defaults"""
        return self._defaults

    @property
    def len_positon_only(self) -> int:
        """Length of Position only args"""
        if self._len_pos_only is None:
            self._len_pos_only = len(self.lst_pos_only)
        return self._len_pos_only

    @property
    def len_kw_only(self) -> int:
        """Length of Keyword only args"""
        if self._len_kw_only is None:
            self._len_kw_only = len(self.lst_kw_only)
        return self._len_kw_only

    @property
    def len_pos_or_kw(self) -> int:
        """Length of Position or Keyword args"""
        if self._len_pos_or_kw is None:
            self._len_pos_or_kw = len(self.lst_pos_or_kw)
        return self._len_pos_or_kw

    @property
    def is_args_only(self) -> bool:
        """Gets if function is *args only"""
        if self.index_args != 0:
            return False
        if self.index_kwargs >= 0:
            return False
        result = True
        result = result and self.len_positon_only == 0
        result = result and self.len_kw_only == 0
        result = result and self.len_pos_or_kw == 0
        return result

    @property
    def is_kwargs_only(self) -> bool:
        """Gets if function is **kwargs only"""
        if self.index_args >= 0:
            return False
        if self.index_kwargs != 0:
            return False
        result = True
        result = result and self.len_positon_only == 0
        result = result and self.len_kw_only == 0
        result = result and self.len_pos_or_kw == 0
        return result

    @property
    def is_named_args_only(self) -> bool:
        """Gets if function is named only. No *args or **kwargs"""
        if self.index_args >= 0:
            return False
        if self.index_kwargs >= 0:
            return False
        result = True
        result = result and self.len_pos_or_kw > 0
        result = result and self.len_positon_only == 0
        result = result and self.len_kw_only == 0
        return result

    @property
    def is_args(self) -> bool:
        """Gets if function has any *args"""
        return self.index_args >= 0

    @property
    def is_noargs(self) -> bool:
        """Gets if function has any arguments after excluding any *args"""
        if self.is_kwargs:
            return True
        count = self.len_kw_only
        count += self.len_pos_or_kw
        count += self.len_positon_only
        return count > 0

    @property
    def is_kwargs(self) -> bool:
        """Gets if function has any **kwargs"""
        return self.index_kwargs >= 0

    @property
    def all_keys(self) -> Tuple[str]:
        """Gets combined keys for ``pos_or_kw``, ``kw_only``, ``pos_only``"""
        if self._all_keys is None:
            keys = []
            for key in self.lst_pos_or_kw:
                keys.append(key)
            for key in self.lst_kw_only:
                keys.append(key)
            for key in self.lst_pos_only:  # pragma: no cover
                keys.append(key)
            self._all_keys = tuple(keys)
        return self._all_keys

    @property
    def is_drop_first(self) -> bool:
        """Gets of the first arg is to be dropped. Thsi is determined by ftype (DecFuncEnum)"""
        return self._drop_arg_first()

    @property
    def name(self) -> str:
        """Gets the name of the function"""
        return self._name
    # endregion Property


class _FnInstInfo(object):
    # region init
    def __init__(self, fninfo: _FuncInfo, fn_args: tuple, fn_kwargs: "OrderedDict[str, Any]"):
        """
        [summary]

        Args:
            fninfo (_FuncInfo): [description]
            fn_args (tuple): [description]
            fn_kwargs (Dict[str, Any]): [description]
        """
        self._fn_info = fninfo
        self._fn_name = self._fn_info.name
        self._kw = OrderedDict()
        self._real_kw = OrderedDict()
        self._real_args = []
        self._cache = {}
        self._process_kwargs(args=fn_args, kwargs=fn_kwargs)
        self._process_args(args=fn_args)

    def _process_kwargs(self, args: tuple, kwargs: Dict[str, Any]):
        if self._fn_info.is_args_only:
            return
        if self._fn_info.is_drop_first:
            tmp_args = [*args[1:]]
        else:
            tmp_args = [*args]

        def process_kw(keys: Iterable[str]):
            missing_args = []
            ignore_keys = set()
            for key in keys:
                if key in self._kw and not key in kwargs:
                    continue
                try:
                    self._kw[key] = kwargs[key]
                except KeyError:
                    pass
                    # will be a default
                    if key in self._fn_info.defauts:
                        self._kw[key] = self._fn_info.defauts[key]
                    else:
                        missing_args.append(key)
                ignore_keys.add(key)
            if len(missing_args) > 0:
                self._missing_args_error(missing_names=missing_args)
            for k, v in kwargs.items():
                if not k in ignore_keys:
                    self._real_kw[k] = v
            return

        if self._fn_info.is_kwargs_only is True:
            self._real_kw.update(**kwargs)
            return
        if self._fn_info.is_named_args_only is True:
            if len(tmp_args) > 0:
                self._kw.update(zip(self._fn_info.lst_pos_or_kw, tmp_args))
            process_kw(keys=self._fn_info.lst_pos_or_kw)
            return
        # at this point the are kwargs but not all are assigned to real key names.
        # is it posible at this point that some of the values are contained within args.
        if self._fn_info.is_args is False:
            if len(tmp_args) > 0:
                self._kw.update(zip(self._fn_info.lst_pos_or_kw, tmp_args))
            keys = self._fn_info.lst_pos_or_kw
            process_kw(keys=keys)
            return
        # at this point there are definatly args
        # check to see if there are any pre *args names.
        if self._fn_info.index_args > 0:
            if len(tmp_args) > 0 and self._fn_info.len_pos_or_kw > 0:
                self._kw.update(zip(self._fn_info.lst_pos_or_kw, tmp_args))
            process_kw(keys=self._fn_info.lst_kw_only)
            return
        # at this point there are *args but they do not contain any keyword arg values.
        process_kw(keys=self._fn_info.all_keys)

    def _process_args(self, args: tuple):
        if self._fn_info.is_args is False:
            return
        if self._fn_info.is_drop_first:
            tmp_args = [*args[1:]]
        else:
            tmp_args = [*args]
        if self._fn_info.is_args_only:
            self._real_args = tmp_args
            return
        if self._fn_info.index_args > 0:
            # lst_pos_or_kw contains pre *arg keys
            # if there are key, values after *args then they will be in lst_kw_only
            tmp_args = tmp_args[self._fn_info.index_args:]
            self._real_args = tmp_args
            return
        self._real_args = tmp_args
        return
    # endregion init

    # region Private Methods
    def _get_all_kw(self) -> "OrderedDict[str, Any]":
        """Get all keword args combined into one dictionary"""
        key = 'all_kw'
        if key in self._cache:
            return self._cache[key]

        kw = OrderedDict(**self.key_word_args)
        kw.update(self.kwargs)
        self._cache[key] = kw
        return self._cache[key]

    def _missing_args_error(self, missing_names: List[str]):
        fn_name = self.name + "()"
        msg = Formatter.get_missing_args_error_msg(
            missing_names=missing_names, name=fn_name)
        raise TypeError(msg)

    # endregion Private Methods

    # region Public Methods

    def get_filter_arg(self) -> "OrderedDict[str, Any]":
        """
        Get a dictionary of args only.

        All arg keys will be in the format of *#. Eg {'*0': 22, '*1': -5.67}

        Returns:
            Dict[str, Any]: Args as dictionary
        """
        cache_key = 'filter_arg'
        if cache_key in self._cache:
            return self._cache[cache_key]
        result = OrderedDict()
        if self.info.is_args is False:
            return result
        offset = self.info.index_args
        for i, arg in enumerate(self.args):
            key = '*' + str(i + offset)
            result[key] = arg
        self._cache[cache_key] = result
        return self._cache[cache_key]

    def get_filter_noargs(self) -> "OrderedDict[str, Any]":
        """
        Gets a dictionary of all keyword args that has all plain args omitted.

        Returns:
            Dict[str, Any]: dictionary with args ommited
        """
        return self._get_all_kw()

    def get_filtered_kwargs(self) -> "OrderedDict[str, Any]":
        """
        Gets a dictionary of only kwargs

        Returns:
            Dict[str, Any]: dictionary of kwargs only
        """
        key = 'filtered_kwargs'
        if key in self._cache:
            return self._cache[key]
        self._cache[key] = OrderedDict(self.kwargs)
        return self._cache[key]

    def get_filtered_key_word_args(self) -> "OrderedDict[str, Any]":
        """
        Gets a dictionary of only keyword args

        Returns:
            Dict[str, Any]: dictionary of keyword args only
        """
        key = 'filtered_key_word_args'
        if key in self._cache:
            return self._cache[key]
        self._cache[key] = OrderedDict(self.key_word_args)
        return self._cache[key]

    def get_all_args(self) -> "OrderedDict[str, Any]":
        """
        Gets all keyword, kwarg and args in a single dictionary

        Returns:
            Dict[str, Any]: dictionay containing all args
        """
        key = 'filtered_all_args'
        if key in self._cache:
            return self._cache[key]

        def get_pre_star_keys() -> Tuple[str]:
            pre_keys = tuple()
            if self.info.index_args > 0:
                # there are keys before *args
                # when there are pre keys they are held in lst_pos_or_kw
                pre_keys = tuple(self.info.lst_pos_or_kw)
            return pre_keys
        result = OrderedDict()
        # pre list is needed to preserve order of keys
        pre = get_pre_star_keys()
        i = 0
        for key in pre:
            result[key] = self.key_word_args[key]
            i += 1
        for arg in self.args:
            key = '*' + str(i)
            result[key] = arg
            i += 1
        for key, value in self.key_word_args.items():
            if not key in pre:
                result[key] = value

        result.update(self.kwargs)
        self._cache[key] = result
        return self._cache[key]
    # endregion Public Methods

    # region Properties
    @property
    def name(self) -> str:
        return self._fn_name

    @property
    def info(self) -> _FuncInfo:
        return self._fn_info

    @property
    def key_word_args(self) -> "OrderedDict[str, Any]":
        return self._kw

    @property
    def kwargs(self) -> "OrderedDict[str, Any]":
        return self._real_kw

    @property
    def args(self) -> list:
        return self._real_args
    # endregion Properties


class _CommonBase(object):
    def __init__(self, **kwargs):
        """
        Constructor

        Keyword Arguments:
            opt_return (object, optional): Return value when decorator is invalid.
                By default an error is rasied when validation fails. If ``opt_return`` is
                supplied then it will be return when validation fails and no error will be raised.
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
        """
        self._opt_return = kwargs.get("opt_return", NO_THING)
        self._logger: Optional[Logger] = kwargs.get("opt_logger", None)
        # and option check for fn value in kwargs. can be used for testing
        self._fn: Optional[callable] = kwargs.get('_option_fn', None)
    
    def _log_err(self, err: Exception):
        """
        [summary]

        Args:
            err (Exception): [description]
        """
        if isinstance(self._logger, Logger):
            self._logger.exception(err)

    def _is_opt_return(self) -> bool:
        """
        Gets if opt_return value has been set in constructor

        Returns:
            bool: True if opt_return value is set; Otherwise, False
        """
        return not self._opt_return is NO_THING

    def _call_init(self, **kwargs):
        """
        Call Init. Provides args for base methhods.

        Keyword Arguments:
            func (callable): Function that is being wrapped
        """
        fn = kwargs.get('func', None)
        if not fn is None:
            self._fn = fn

    # region Properties
    @property
    def fn(self) -> callable:
        if self._fn is None:
            raise ValueError(
                "fn has not been set. Check if _call_init is called.")
        return self._fn
    # endregion Properties
class _DecBase(_CommonBase):

    # region Init
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
        self._cache = {
            'args': [],
            'kwargs': OrderedDict()
        }
        self._w_cache = None

    def _call_init(self, **kwargs):
        """
        Call Init. Provides args for base methhods.

        Keyword Arguments:
            func (callable): Function that is being wrapped
        """
        super()._call_init(**kwargs)

    def _wrapper_init(self, **kwargs):
        """
        Wrapper Init. Provides args for base methods.
        This method usually called right after Wrapper method

        Keyword Arguments:
            args (Iterable[object]): Wrapped function ``args``
            kwargs (Dict[str, Any]): Wrapped function ``kwargs``
        """
        clear_cache = kwargs.get("clear_cache", True)
        if clear_cache:
            self._w_cache = {}
        key = 'args'
        if key in kwargs:
            self.args = kwargs[key]
        key = 'kwargs'
        if key in kwargs:
            self.kwargs = kwargs[key]
    # endregion Init

    # region Property
    
    # region Function cache Properties

    @property
    def fn_cache(self) -> Dict[str, object]:
        """Gets function level cache"""
        if not self._w_cache:
            self._w_cache = {}
        return self._w_cache

    @property
    def args(self) -> Iterable[object]:
        """Gets/sets wrapped function args"""
        return self.fn_cache['args']

    @args.setter
    def args(self, value: Iterable[object]):
        self.fn_cache['args'] = [*value]

    @property
    def kwargs(self) -> Dict[str, Any]:
        """Gets/sets wrapped function kwargs"""
        return self.fn_cache['kwargs']

    @kwargs.setter
    def kwargs(self, value: Dict[str, Any]):
        od = OrderedDict()
        for k, v in value.items():
            od[k] = v
        self.fn_cache['kwargs'] = od

    @property
    def fn_inst_info(self) -> _FnInstInfo:
        cache = self.fn_cache
        key = '_fn_instance_info'
        if key in cache:
            return cache[key]
        cache[key] = self._get_inst_info()
        return cache[key]
    # endregion Function cache Properties
    # endregion Property

    def _drop_arg_first(self) -> bool:
        return self._ftype.value > DecFuncEnum.METHOD_STATIC.value

    def _get_args(self):
        # return self.fn_inst_info.args
        if self._drop_arg_first():
            return self.args[1:]
        return self.args

    def _get_args_star(self) -> Iterable[object]:
        """
        Get args accounting for ``*args`` postions in function and if function class method.

        Args:
            func (callable): function with args
            args (Iterable[object]): function current args

        Returns:
            Iterable[object]: New args that may be a subset of all of orignial ``args``.
        """
        pos = self._get_star_args_pos()
        drop_first = self._drop_arg_first()
        i = 0
        if pos > 0:
            i += pos
        if drop_first:
            i += 1
        if i > 0:
            return self.args[i:]
        return self.args

    def _get_fn_info(self) -> _FuncInfo:
        info = self._cache.get("_fn_info", False)
        if info:
            return info
        self._cache['_fn_info'] = _FuncInfo(func=self.fn, ftype=self._ftype)
        return self._cache['_fn_info']

    def _get_inst_info(self, **kwargs) -> _FnInstInfo:
        """
        Gets Function Info

        Keyword Arguments:
            error_check (bool, optional): Determinse if errors are raise if there are missing
                keywords. This is the case when function has keywords without defaults assigned
                and no value is passed into function.

        Returns:
            _FnInstInfo: Function Instance Info
        """
        err_chk = bool(kwargs.get("error_check", True))
        try:
            info = _FnInstInfo(fninfo=self._get_fn_info(),
                               fn_args=self.args, fn_kwargs=self.kwargs)
        except TypeError as e:
            if err_chk:
                msg = str(e)
                msg += self._get_class_dec_err()
                raise TypeError(msg)
        return info

    def _get_args_dict(self, **kwargs) -> "OrderedDict[str, Any]":
        """
        Gets OrderedDict of all Args, and Keyword args.

        All ``*arg`` values will have a key of ``*#`` Eg: ``'*0', 12``, ``'*1': 45.77``, ``'*3': 'flat'``

        Keyword Arguments:
            error_check (bool, optional): Determinse if errors are raise if there are missing
                keywords. This is the case when function has keywords without defaults assigned
                and no value is passed into function.

        Returns:
            OrderedDict[str, Any]: Dictionary of keys and values representing ``func`` keywords and values.
        """
        info = self._get_inst_info(kwargs=kwargs)
        return info.get_all_args()

    def _get_filtered_args_dict(self, opt_filter: DecArgEnum = DecArgEnum.All_ARGS) -> "OrderedDict[str, Any]":
        """
        Gets filtered dictionary

        Args:
            filter (DecArgEnum): Filter option
        Returns:
            OrderedDict[str, Any]: of based on filter
        """
        fn_info = self.fn_inst_info
        if opt_filter & DecArgEnum.All_ARGS == DecArgEnum.All_ARGS:
            return fn_info.get_all_args()
        if opt_filter & DecArgEnum.NO_ARGS == DecArgEnum.NO_ARGS:
            return fn_info.get_filter_noargs()
        result = OrderedDict()
        if DecArgEnum.ARGS in opt_filter:
            if fn_info.info.is_args:
                result.update(fn_info.get_filter_arg())
        if DecArgEnum.KWARGS in opt_filter:
            if fn_info.info.is_kwargs:
                result.update(fn_info.get_filtered_kwargs())
        if DecArgEnum.NAMED_ARGS in opt_filter:
            result.update(fn_info.get_filtered_key_word_args())
        return result

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
        result = Formatter.get_formated_names(names=t_names, **kwargs)
        return result

    def _get_star_args_pos(self) -> int:
        """
        Gets the zero base postion of *args in a function.

        Args:
            func (callable): function to get *args postion of.

        Returns:
            int: -1 if  *args not present; Otherwise zero based postion of *args
        """
        info = self._get_fn_info()
        return info.index_args

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
    def _get_err(self, e: RuleError):
        err = RuleError.from_rule_error(
            e, fn_name=self.fn.__name__, msg=self._get_class_dec_err(nl=False))
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
            opt_args_filter (DecArgEnum, optional): Filters the arguments that are validated. Default ``DecArgEnum.ALL``.
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
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
        self._opt_args_filter = DecArgEnum(
            kwargs.get("opt_args_filter", DecArgEnum.All_ARGS))

    def __call__(self, func: callable):
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            arg_name_values = self._get_filtered_args_dict(
                self._opt_args_filter)
            try:
                is_valid = self._typechecker.validate(**arg_name_values)
                if self._typechecker.raise_error is False:
                    wrapper.is_types_valid = is_valid
                if is_valid is False and self._is_opt_return() is True:
                    return self._opt_return
            except TypeError as e:
                if self._is_opt_return():
                    return self._opt_return
                msg = str(e)
                msg = msg + self._get_class_dec_err()
                ex = TypeError(msg)
                self._log_err(ex)
                raise ex
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
            opt_args_filter (DecArgEnum, optional): Filters the arguments that are validated. Default ``DecArgEnum.ALL``.
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
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
        self._opt_args_filter = DecArgEnum(
            kwargs.get("opt_args_filter", DecArgEnum.All_ARGS))

    def _get_formated_types(self, types: Union[Tuple[type], Set[type]]) -> str:
        # multi is list of set, actually one set in a list
        # single is a tuple of a single type.
        # these types are set in constructor.
        if isinstance(types, tuple):
            return f"'{types[0].__name__}'"
        lst_multi = [t.__name__ for t in types]
        result = Formatter.get_formated_names(names=lst_multi,
                                              conj='or')
        return result

    def _get_inst(self, types: Iterable[type]):
        return TypeChecker(*types, **self._kwargs)

    def _validate(self, func: callable, key: str, value: object, types: Iterable[type], arg_index: int, inst: SubClassChecker = None):
        if inst is None:
            tc = self._get_inst(types=types)
        else:
            tc = inst
        if Formatter.is_star_num(name=key):
            try:
                tc.validate(value)
            except TypeError:
                if self._is_opt_return():
                    return self._opt_return
                ex = TypeError(self._get_err_msg(name=None, value=value,
                                                  types=types, arg_index=arg_index,
                                                  fn=func))
                self._log_err(err=ex)
                raise ex
        else:
            try:
                tc.validate(**{key: value})
            except TypeError:
                if self._is_opt_return():
                    return self._opt_return
                ex = TypeError(self._get_err_msg(name=key, value=value,
                                                  types=types, arg_index=arg_index,
                                                  fn=func))
                self._log_err(err=ex)
                raise ex
        return NO_THING

    def __call__(self, func: callable):
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            arg_name_values = self._get_filtered_args_dict(
                self._opt_args_filter)
            arg_keys = list(arg_name_values.keys())
            arg_keys_len = arg_keys.__len__()
            i = 0
            if arg_keys_len is not len(self._types):
                if self._all_args is False:
                    if self._is_opt_return():
                        return self._opt_return
                    msg = 'Invalid number of arguments for {0}()'.format(
                        func.__name__)
                    msg = msg + self._get_class_dec_err()
                    ex = ValueError(msg)
                    self._log_err(err=ex)
                    raise ex
            arg_type = zip(arg_keys, self._types)

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
        str_ord = Formatter.get_ordinal(arg_index + 1)
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
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
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
            str_len = Formatter.get_formated_names(
                names=sorted(self._lengths), conj='or')
        if len_ranges > 0:
            str_rng = Formatter.get_formated_names(
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
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            _args = self._get_args_star()
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
                ex = ValueError(msg)
                self._log_err(err=ex)
                raise ex
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
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
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

    def _get_error_msg(self, args_len: int) -> str:
        msg = f"Invalid number of args pass into '{self.fn.__name__}'.\n{self._get_valid_counts()}"
        msg = msg + f" Got '{args_len}' args."
        msg = msg + self._get_class_dec_err()
        return msg

    def __call__(self, func: callable):
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            _min, _max = self._get_min_max()
            has_rules = _min > 0 or _max >= 0
            if has_rules:
                _args = self._get_args_star()
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
                    ex = ValueError(self._get_error_msg(args_len=_args_len))
                    self._log_err(err=ex)
                    raise ex
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
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
        """
        super().__init__(**kwargs)
        self._rc = None
        self._rules = [arg for arg in args]
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func: callable):
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            return_value = func(*args, **kwargs)
            rc = self._rulechecker
            try:
                rc.validate_all(**{"return": return_value})
            except RuleError as e:
                if self._is_opt_return():
                    return self._opt_return
                err = self._get_err(e=e)
                self._log_err(err=err)
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
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
        """
        super().__init__(**kwargs)
        self._rc = None
        self._rules = [arg for arg in args]
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}

    def __call__(self, func: callable):
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            return_value = func(*args, **kwargs)
            rc = self._rulechecker
            # rc.current_arg = "return"
            try:
                rc.validate_any(**{"return": return_value})
            except RuleError as e:
                if self._is_opt_return():
                    return self._opt_return
                err = self._get_err(e=e)
                self._log_err(err=err)
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
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
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
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            return_value = func(*args, **kwargs)
            try:
                self._typechecker.validate(return_value)
            except TypeError:
                if self._is_opt_return():
                    return self._opt_return
                # catch type error and raise a new one so a more fitting message is raised.
                ex = TypeError(self._get_err_msg(return_value))
                self._log_err(err=ex)
                raise ex
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
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
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
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            is_valid = True
            arg_name_values = self._get_args_dict()
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
                        ex = TypeError(msg)
                        self._log_err(err=ex)
                        raise ex
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
            opt_args_filter (DecArgEnum, optional): Filters the arguments that are validated. Default ``DecArgEnum.ALL``.
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
        """
        super().__init__(**kwargs)
        self._raise_error = bool(kwargs.get("raise_error", True))
        self._rc = None
        self._rules = [arg for arg in args]
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}
        self._opt_args_filter = DecArgEnum(
            kwargs.get("opt_args_filter", DecArgEnum.All_ARGS))

    def __call__(self, func):
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            arg_name_values = self._get_filtered_args_dict(
                self._opt_args_filter)
            is_valid = False
            try:
                is_valid = self._rulechecker.validate_any(**arg_name_values)
            except RuleError as err:
                if self._is_opt_return():
                    return self._opt_return
                err_rule = self._get_err(e=err)
                self._log_err(err=err_rule)
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
            opt_args_filter (DecArgEnum, optional): Filters the arguments that are validated. Default ``DecArgEnum.ALL``.
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
        """
        super().__init__(**kwargs)
        self._raise_error = bool(kwargs.get("raise_error", True))
        self._rc = None
        self._rules = [arg for arg in args]
        if kwargs:
            self._kwargs = {**kwargs}
        else:
            self._kwargs = {}
        self._opt_args_filter = DecArgEnum(
            kwargs.get("opt_args_filter", DecArgEnum.All_ARGS))

    def __call__(self, func):
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            arg_name_values = self._get_filtered_args_dict(
                self._opt_args_filter)
            is_valid = False
            try:
                is_valid = self._rulechecker.validate_all(**arg_name_values)
            except RuleError as err:
                if self._is_opt_return():
                    return self._opt_return
                err_rule = self._get_err(e=err)
                self._log_err(err=err_rule)
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
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
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
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            is_valid = True
            arg_name_values = self._get_args_dict()
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
                        err_rule = self._get_err(e=err)
                        self._log_err(err=err_rule)
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
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            is_valid = True
            arg_name_values = self._get_args_dict()
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
                        err_rule = self._get_err(e=err)
                        self._log_err(err=err_rule)
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
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
        """
        super().__init__(**kwargs)
        self._args = []
        for arg in args:
            if isinstance(arg, str):
                self._args.append(arg)

    def __call__(self, func):
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            arg_name_values = self._get_args_dict()
            arg_keys = arg_name_values.keys()
            for key in self._args:
                if not key in arg_keys:
                    if self._is_opt_return():
                        return self._opt_return
                    ex = ValueError(
                        f"'{func.__name__}', '{key}' is a required arg.")
                    self._log_err(err=ex)
                    raise ex
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
        super()._call_init(func=func)
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
            opt_args_filter (DecArgEnum, optional): Filters the arguments that are validated. Default ``DecArgEnum.ALL``.
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
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
        self._opt_args_filter = DecArgEnum(
            kwargs.get("opt_args_filter", DecArgEnum.All_ARGS))

    def _get_formated_types(self, types: Union[Tuple[type], Set[type]]) -> str:
        # multi is list of set, actually one set in a list
        # single is a tuple of a single type.
        # these types are set in constructor.
        if isinstance(types, tuple):
            return f"'{types[0].__name__}'"
        lst_multi = [t.__name__ for t in types]
        result = Formatter.get_formated_names(names=lst_multi,
                                              conj='or')
        return result

    def _get_inst(self, types: Iterable[type]):
        return SubClassChecker(*types, **self._kwargs)

    def _validate(self, key: str, value: object, types: Iterable[type], arg_index: int, inst: SubClassChecker = None):
        if inst is None:
            sc = self._get_inst(types=types)
        else:
            sc = inst
        # ensure errors are raised if not valid
        sc.raise_error = True
        if Formatter.is_star_num(name=key):
            try:
                sc.validate(value)
            except TypeError:
                if self._is_opt_return():
                    return self._opt_return
                ex = TypeError(self._get_err_msg(name=None, value=value,
                                                  types=types, arg_index=arg_index))
                self._log_err(err=ex)
                raise ex
        else:
            try:
                sc.validate(**{key: value})
            except TypeError:
                if self._is_opt_return():
                    return self._opt_return
                ex = TypeError(self._get_err_msg(name=key, value=value,
                                                  types=types, arg_index=arg_index))
                self._log_err(err=ex)
                raise ex
        return NO_THING

    def __call__(self, func: callable):
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            arg_name_values = self._get_filtered_args_dict(
                self._opt_args_filter)
            arg_keys = list(arg_name_values.keys())
            arg_keys_len = arg_keys.__len__()
            if self._all_args is False:
                if arg_keys_len is not len(self._types):
                    if self._is_opt_return():
                        return self._opt_return
                    msg = 'Invalid number of arguments for {0}()'.format(
                        func.__name__)
                    msg = msg + self._get_class_dec_err()
                    ex = ValueError(msg)
                    self._log_err(err=ex)
                    raise ex
            arg_type = zip(arg_keys, self._types)
            i = 0
            for arg_info in arg_type:
                key = arg_info[0]
                result = self._validate(key=key,
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
                    result = self._validate(key=r_arg,
                                            value=arg_name_values[r_arg],
                                            types=types, arg_index=i,
                                            inst=sc)
                    if not result is NO_THING:
                        return result
                    i += 1

            return func(*args, **kwargs)
        return wrapper

    def _get_err_msg(self, name: Union[str, None], value: object, types: Iterator[type], arg_index: int):
        str_types = self._get_formated_types(types=types)
        str_ord = Formatter.get_ordinal(arg_index + 1)
        if self._ftype == DecFuncEnum.PROPERTY_CLASS:
            msg = f"'{self.fn.__name__}' property error. Arg '{name}' expected is expected be a subclass of {str_types}."
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
            opt_logger (Logger, optional): Logger that logs exceptions when validation fails.
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
        super()._call_init(func=func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._wrapper_init(args=args, kwargs=kwargs)
            arg_name_values = self._get_args_dict()
            arg_keys = arg_name_values.keys()
            sc = False
            for key in self._arg_index.keys():
                if key in arg_keys:
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
                        ex = TypeError(msg)
                        self._log_err(err=ex)
                        raise ex
            return func(*args, **kwargs)
        return wrapper
