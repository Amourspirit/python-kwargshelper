# coding: utf-8
from inspect import isclass
from typing import Iterable, Optional, Union
from ..rules import IRule
from ..helper import is_iterable
from ..exceptions import RuleError
class TypeChecker:
    """Class that validates args match a give type"""

    def __init__(self, *args: type, **kwargs): 
        """
        Constructor

        Other Arguments:
            args (type): One or more types used for Validation purposes.

        Keyword Arguments:
            raise_error: (bool, optional): If ``True`` then an error will be raised if a :py:meth:`~.TypeChecker.validate` fails:
                Othwewise :py:meth:`~.TypeChecker.validate` will return a boolean value indicationg success or failure.
            type_instance_check (bool, optional): If ``True`` then :py:meth:`~.TypeChecker.validate` args
                are tested also for isinstance if type does not match, rather then just type check if type is a match.
                If ``False`` then values willl only be tested as type.
                Default ``True``
        """
        self._types = [arg for arg in args]

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
        def _is_type_instance(_types: Iterable[type], _value):
            result = False
            for t in _types:
                if isinstance(_value, t):
                    result = True
                    break
            return result
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
                        msg = f"Arg Value is expected to be of '{self._get_formated_types()}' but got '{type(value).__name__}'"
                    else:
                        msg = f"Arg '{key}' is expected to be of '{self._get_formated_types()}' but got '{type(value).__name__}'"
                    raise TypeError(msg)
        return result

    def validate(self, *args, **kwargs) -> bool:
        """
        Validates all ``*args`` and all ``**kwargs`` against ``types`` that are passed
        into constructor.

        Returns:
            bool: ``True`` if all ``*args`` and all ``**kwarg`` match a type; Otherwise;
            ``False``.

        Raises:
            TypeError: if ``raise_error`` is ``True`` and validation fails.
        """
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
        :setter: Sets type_instance_check value
        """
        return self._type_instance_check

    @type_instance_check.setter
    def type_instance_check(self, value: bool) -> bool:
        self._type_instance_check = bool(value)

    @property
    def raise_error(self) -> bool:
        """
        Determines if errors will be raised during validation

        If ``True`` then errors will be raised when validation fails.

        :getter: Gets if errors can be raised.
        :setter: Sets if errors can be raised.
        """
        return self._raise_error

    @raise_error.setter
    def raise_error(self, value: bool) -> bool:
        self._raise_error = bool(value)
    
    @property
    def types(self) -> Iterable[type]:
        """
        Gets the types passed into constructor that are used for validating args
        """
        return self._types
    # endregion Properties


class RuleChecker:
    """Class that validates args match a given rule"""

    def __init__(self, rules_all: Optional[Iterable[IRule]] = None, rules_any: Optional[Iterable[IRule]] = None, ** kwargs):
        """
        Constructor

        Args:
            rules_all (Iterable[IRule], optional): List of rules that must all be matched. Defaults to ``None``.
            rules_any (Iterable[IRule], optional): List of rules that any one must be matched. Defaults to ``None``.

        Keyword Arguments:
            raise_error (bool, optional): If ``True`` then rules can raise errors when validation fails.
                Default ``False``.

        Raises:
            TypeError: If ``rule_all`` is not an iterable object
            TypeError: If ``rule_any`` is not an iterable object
        """
        if rules_all is None:
            self._rules_all = []
            self._len_all = 0
        else:
            if is_iterable(rules_all) == False:
                raise TypeError(
                    "rules_all arg must be an iterable object such as list or tuple.")
            self._rules_all = rules_all
            self._len_all = len(self._rules_all)
        if rules_any is None:
            self._rules_any = []
            self._len_any = 0
        else:
            if is_iterable(rules_any) == False:
                raise TypeError(
                    "rules_aany arg must be an iterable object such as list or tuple.")
            self._rules_any = rules_any
            self._len_any = len(self._rules_any)
            
        
        key = 'raise_error'
        if key in kwargs:
            self._raise_error: bool = bool(kwargs[key])
        else:
            self._raise_error: bool = True

    # region internal validation methods

    def _validate_rules_all(self, key: str, field: str, value: object) -> bool:
        # if all rules pass then validations is considered a success
        valid_arg = self._is_valid_arg(key)
        if valid_arg:
            _key = key
            _field = field
        else:
            _key = 'arg'
            _field = 'arg'
           
        result = True
        if self._len_all > 0:
            for rule in self._rules_all:
                if not isclass(rule) or not issubclass(rule, IRule):
                    raise TypeError('Rules must implement IRule')
                rule_instance: IRule = rule(
                    key=_key, name=_field, value=value, raise_errors=self._raise_error, originator=self)
                try:
                    result = result & rule_instance.validate()
                except Exception as e:
                    arg_name = _key if valid_arg else None
                    raise RuleError(
                        err_rule=rule, rules_all=self._rules_all, arg_name=arg_name, errors=e) from e
                if result is False:
                    break
        return result

    def _validate_rules_any(self, key: str, field: str, value: object) -> bool:
        # if any rule passes then validations is considered a success
        valid_arg = self._is_valid_arg(key)
        if valid_arg:
            _key = key
            _field = field
        else:
            _key = 'arg'
            _field = 'arg'
        error_lst = []
        result = True
        failed_rules = []
        if self._len_any > 0:
            for rule in self._rules_any:
                if not isclass(rule) or not issubclass(rule, IRule):
                    raise TypeError('Rules must implement IRule')
                rule_instance: IRule = rule(
                    key=_key, name=_field, value=value, raise_errors=self._raise_error, originator=self)
                rule_valid = False
                try:
                    rule_valid = rule_instance.validate()
                except Exception as e:
                    error_lst.append(e)
                    failed_rules.append(rule)
                    rule_valid = False
                result = rule_valid
                if rule_valid is True:
                    break
        if result is False and self._raise_error is True and len(error_lst) > 0:
            # raise the last error in error list
            arg_name = _key if valid_arg else None
            raise RuleError(rules_any=self._rules_any,
                            err_rule=failed_rules[0], arg_name=arg_name, errors=error_lst) from error_lst[0]
            
        return result

    def _is_valid_arg(self, arg:str) -> bool:
        return arg != '..arg'
    
    # endregion internal validation methods

    def validate_all(self, *args, **kwargs) -> bool:
        """
        Validates all. All ``*args`` and ``**kwargs`` must match :py:attr:`~.RuleChecker.rules_all`

        Returns:
            bool: ``True`` if all ``*args`` and ``**kwargs`` are valid; Otherwise, ``False``

        Raises:
            Exception: If :py:attr:`~.RuleChecker.raise_error` is ``True`` and validation Fails.
                The type of exception raised is dependend on the :py:class:`.IRule` that caused validation
                failure. Most rules raise a ``ValueError`` or a ``TypeError``.
        """
        if self._len_all == 0:
            return True
        result = True
        for arg in args:
            result = result & self._validate_rules_all(
                key="..arg", field="arg", value=arg)
            if result is False:
                break
        if result is False:
            return result
        for k, v in kwargs.items():
            result = result & self._validate_rules_all(key=k, field=k, value=v)
            if result is False:
                break
        return result

    def validate_any(self, *args, **kwargs) -> bool:
        """
        Validates any. All ``*args`` and ``**kwargs`` must match on ore more of :py:attr:`~.RuleChecker.rules_any`

        Returns:
            bool: ``True`` if all ``*args`` and ``**kwargs`` are valid; Otherwise, ``False``

        Raises:
            Exception: If :py:attr:`~.RuleChecker.raise_error` is ``True`` and validation Fails.
                The type of exception raised is dependend on the :py:class:`.IRule` that caused validation
                failure. Most rules raise a ``ValueError`` or a ``TypeError``.
        """
        if self._len_any == 0:
            return True
        result = True
        for arg in args:
            result = self._validate_rules_any(
                key="..arg", field="arg", value=arg)
            if result is False:
                break
        if result is False:
            return result
        for k, v in kwargs.items():
            result = result & self._validate_rules_any(key=k, field=k, value=v)
            if result is False:
                break
        return result

    # region Properties
    @property
    def rules_all(self) -> Iterable[IRule]:
        """
        Gets rules passed into ``rules_all`` of constructor used for validation of args.
        """
        return self._rules_all

    @property
    def rules_any(self) -> Iterable[IRule]:
        """
        Gets rules passed into ``rules_any`` of constructor used for validation of args.
        """
        return self._rules_any

    @property
    def raise_error(self) -> bool:
        """
        Determines if errors will be raised during validation

        If ``True`` then errors will be raised when validation fails.
        Default value is ``True``.

        :getter: Gets if errors can be raised.
        :setter: Sets if errors can be raised.
        """
        return self._raise_error

    @raise_error.setter
    def raise_error(self, value: bool) -> bool:
        self._raise_error = bool(value)
    # endregion Properties
