# coding: utf-8
__version__ = '0.3.0'
from typing import List, Optional, Set, Callable
from . rules import IRule
from . helper.base import HelperBase
from . error import CancelEventError
from . helper.args import HelperArgs
from . event_args import AfterAssignEventArgs, BeforeAssignEventArgs

# region class KwargsHelper
class KwargsHelper(HelperBase):
    '''
    kwargs helper class. Assigns attributes to class with various checks
    @example:
    ```
    class MyClass:
        def __init__(self, **kwargs):
            self._msg = ''
            kw = KwargsHelper(self, {**kwargs})
            kw.assign(key='msg', require=True, types=['str'])
            kw.assign(key='length', types=['int'], default=-1)

        @property
        def msg(self) -> str:
            return self._msg

        @property
        def length(self) -> str:
            return self._length

    my_class = MyClass(msg='Hello World')
    print(my_class.msg) # Hello World
    print(my_class.length) # -1
    ```
    '''
    # region init

    def __init__(self, originator: object, obj_kwargs: dict, **kwargs):
        '''
        Class Constructor
        @originator: Type:object, object that attributes are assigned to via `assign()` method. This is usually a class.
        @obj_kwargs: Type:dict, The dictionary of key value args used to set values of attributes.
        Often passed in as `obj_kwargs = {**kwargs}`
        @field_prefix: (optional) Type:bool, sets the `field_prefix` property
        @name: (optional) Type:str, sets the `name` property
        @cancel_error: (optional) Type:bool, sets the `cancel_error` property
        @rule_error: (optional) Type:bool, sets the `rule_error` property
        @rule_test_before_assign: (optional) Type:bool, sets the `rule_test_before_assign` property
        @assign_true_not_required: (optional): Type:bool, sets the `assign_true_not_required` property
        '''
        self._callbacks = None
        self._obj: object = originator
        self._kwargs = obj_kwargs
        m_name = '__init__'
        key = 'field_prefix'
        if key in kwargs:
            self._field_prefix = kwargs[key]
            self._is_arg_str(
                method_name=m_name, arg=self._field_prefix, arg_name=key, raise_error=True)
        else:
            self._field_prefix = '_'
        key = 'name'
        if key in kwargs:
            self._name = kwargs[key]
            self._is_arg_str(
                method_name=m_name, arg=self._name, arg_name=key, raise_error=True)
        else:
            self._name = type(originator).__name__

        key = 'rule_error'
        if key in kwargs:
            self._rule_error: bool = kwargs[key]
            self._is_arg_bool(
                method_name=m_name, arg=self._rule_error, arg_name=key, raise_error=True)
        else:
            self._rule_error: bool = True

        key = 'rule_test_before_assign'
        if key in kwargs:
            self._rule_test_early: bool = kwargs[key]
            self._is_arg_bool(
                method_name=m_name, arg=self._rule_test_early, arg_name=key, raise_error=True)
        else:
            self._rule_test_early = True

        key = 'cancel_error'
        if key in kwargs:
            self._cancel_error: bool = kwargs[key]
            self._is_arg_bool(
                method_name=m_name, arg=self._cancel_error, arg_name=key, raise_error=True)
        else:
            self._cancel_error: bool = True

        key = 'assign_true_not_required'
        if key in kwargs:
            self._assign_true_not_required: bool = kwargs[key]
            self._is_arg_bool(
                method_name=m_name, arg=self._assign_true_not_required, arg_name=key, raise_error=True)
        else:
            self._assign_true_not_required: bool = True
    # endregion init

    # region Public Methods
    def assign(self, key: str, field: Optional[str] = None, require: bool = False, default: Optional[object] = None, types: Optional[List[type]] = None, rules: Optional[List[Callable[[IRule], bool]]] = None) -> bool:
        '''
        Assigns attribue value to `obj` passed in to constructor. Attributes are created if they do not exist.
        @key: Type:str, the key of the key, value pair that is required or optional in `obj_kwargs` passed into to constructor.
        @field: (optional) Type:str the name of the field to assign a value. If `field` is omitted then filed name is built using
        `instance.field_prefix` + `key`. If included then `instance.field_prefix` will be ignored.
        @require: (optional) Type:bool, Determins if `key` is required to be in `obj_kwargs` passed into to constructor.
        if `default` is passed in then `require` is ignored. Default: `False`
        @default: (optional) Type:str, default value to assign to key attribute if no value is found in `obj_kwargs` passed into to constructor.
        If `default` is passed in then `require` is ignored
        @types: (optional) Type:List[str], a string list of one or more types that the value of the key value pair must match.
        For example if a value is required to be only `str` then `types=['str']. In this example if value is not type str then `TypeError` is raised
        If value is required to be `str` or `int` then `types=['str', 'int']`.
        If `types` is omitted then a value can be any type.

        @rules: (optional) Type:List[Callable[[IRule], bool]]
        '''
        m_name = 'assign'
        self._is_arg_str(
            method_name=m_name, arg=key, arg_name='key', raise_error=True)
        self._is_arg_bool(
            method_name=m_name, arg=require, arg_name='require', raise_error=True)

        if types == None:
            types = []
        if rules == None:
            rules = []
        _args = HelperArgs(key=key, require=require)
        _args.field = field
        # _args.require = require
        _args.types = set(types)
        _args.rules = rules
        if default is not None:
            _args.default = default
        before_args = BeforeAssignEventArgs(_args, self._obj)

        after_args = AfterAssignEventArgs(_args, self._obj)
        self._assign(args=_args, before_args=before_args,
                     after_args=after_args)
        self._on_after_assign(after_args)
        result = after_args.success

        if result == False and self._assign_true_not_required == True and require == False:
            result = True
        return result

    def assign_helper(self, helper: HelperArgs) -> bool:
        self._isinstance_method(method_name='assign_helper', arg=helper, arg_name='helper',arg_type=HelperArgs, raise_error=True)
        d = helper.to_dict()
        return self.assign(**d)
    # endregion Public Methods

    # region private methods
    def _assign(self, args: HelperArgs, before_args: BeforeAssignEventArgs, after_args: AfterAssignEventArgs) -> None:
        result = False
        key = args.key
        if key in self._kwargs:
            value = self._kwargs[key]
            if len(args.types) > 0:
                if not type(value) in args.types:
                    msg = f"{self._name} arg '{key}' is expected to be of '{self._get_formated_types(args.types)}' but got '{type(value).__name__}'"
                    raise TypeError(msg)
            if args.field:
                result = self._setattr(
                    args.field, value, before_args, after_args, args=args)
            else:
                result = self._setattr(f"{self._field_prefix}{key}",
                                       value, before_args, after_args, args=args)
        else:
            if args.default is not None:
                if args.field:
                    result = self._setattr(args.field, args.default,
                                           before_args, after_args, args=args)
                else:
                    result = self._setattr(f"{self._field_prefix}{key}",
                                           args.default, before_args, after_args, args=args)
            elif args.require:
                # only test for required when default is not included
                raise ValueError(f"{self._name} arg '{key}' is required")
        after_args._success = result
        after_args._success
        return None

    # def _get_type_error_msg_method(self, method_name: str, arg: object, arg_name: str, expected_type: str) -> str:
    #     result = f"{self.__class__.__name__}.{method_name}() arg '{arg_name}' is expecting type of '{expected_type}'. Got type of '{type(arg).__name__}'"
    #     return result

    # def _get_type_error_msg_property(self, property_name: str, value: object, expected_type: str) -> str:
    #     result = f"{self.__class__.__name__}.{property_name} is expecting type of '{expected_type}'. Got type of '{type(value).__name__}'"
    #     return result

    def _get_formated_types(self, types: Set[str]) -> str:
        result = ''
        for i, t in enumerate(types):
            if i > 0:
                result = result + ' | '
            result = f"{result}{t}"
        return result

    def _setattr(self, field: str, value: object, before_args: BeforeAssignEventArgs, after_args: AfterAssignEventArgs, args: HelperArgs) -> bool:
        before_args.field_name = field
        before_args.field_value = value

        self._on_before_assign(before_args=before_args)

        after_args._canceled = before_args.cancel
        if before_args.cancel == True:
            if self._cancel_error == False:
                return False
            raise CancelEventError(
                f"{self.__class__.__name__}.assign() canceled in 'BeforeAssignEventArgs'")
        _field = before_args.field_name
        _value = before_args.field_value
        result = True
        if self._rule_test_early:
            result = self._validate_rules(
                args=args, field=_field, value=_value, after_args=after_args)
            if result == False:
                return result
        setattr(self._obj, _field, _value)
        if self._rule_test_early == False:
            result = self._validate_rules(
                args=args, field=_field, value=_value, after_args=after_args)
            if result == False:
                return result
        after_args._field_name = _field
        after_args._field_value = _value
        return result

    def _validate_rules(self, args: HelperArgs, field: str, value: object,  after_args: AfterAssignEventArgs) -> bool:
        key = after_args.key
        if len(args.rules) > 0:
            for rule in args.rules:
                if not issubclass(rule, IRule):
                    raise TypeError('Rules must implement IRule')
                rule_instance: IRule = rule(
                    key=key, name=field, value=value, raise_errors=self._rule_error, originator=self._obj)
                if rule_instance.validate() == False:
                    after_args._rules_passed = False
                    return False
        after_args._rules_passed = True
        return True

    # endregion private methods

    # region callback funcs

    def _on(self, event_name, callback):
        if self._callbacks is None:
            self._callbacks = {}

        if event_name not in self._callbacks:
            self._callbacks[event_name] = [callback]
        else:
            self._callbacks[event_name].append(callback)

    def _trigger(self, event_name, eventArgs):
        if self._callbacks is not None and event_name in self._callbacks:
            for callback in self._callbacks[event_name]:
                callback(self, eventArgs)

    # endregion callback funcs

    # region raise events
    def _on_before_assign(self, before_args: BeforeAssignEventArgs):
        self._trigger("on_before_assign", before_args)

    def _on_after_assign(self, event_args: AfterAssignEventArgs):
        self._trigger("on_after_assign", event_args)
    # endregion raise events

     # region Handlers
    def add_handler_before_assign(self, callback: Callable[['KwargsHelper', BeforeAssignEventArgs], None]):
        self._on("on_before_assign", callback)

    def add_handler_after_assign(self, callback: Callable[['KwargsHelper', AfterAssignEventArgs], None]):
        self._on("on_after_assign", callback)
    # endregion

    # region Properties
    @property
    def assign_true_not_required(self) -> bool:
        '''
        Gets assign_true_not_required option

        If `True` then and a non-required arg is assigned via `assign()`
        then `assign()` returns `True` even if the arg failed to be applied. In an 'after callback' method set by `add_handler_after_assign()`
        success in `AfterAssignEventArgs.success` property is `False` if arg was not assigned.
        Default: `True`
        '''
        return self._assign_true_not_required

    @assign_true_not_required.setter
    def assign_true_not_required(self, value: bool) -> None:
        '''
        Sets assign_true_not_required option

        If `True` then and a non-required arg is assigned via `assign()`
        then `assign()` returns `True` even if the arg failed to be applied. In an 'after callback' method set by `add_handler_after_assign()`
        success in `AfterAssignEventArgs.success` property is `False` if arg was not assigned.
        '''
        self._is_prop_bool(
            value=value, prop_name='assign_true_not_required', raise_error=True)
        self._assign_true_not_required = value
        return None

    @property
    def cancel_error(self) -> bool:
        '''
        Gets cancel_error option

        Determins if an error will be raised if cancel is set in
        `BeforeAssignEventArgs` of a callback : Default `True`
        '''
        return self._cancel_error

    @cancel_error.setter
    def cancel_error(self, value: bool) -> None:
        '''
        Sets cancel_error option

        Determins if an error will be raised if cancel is set in
        `BeforeAssignEventArgs` of a callback
        '''
        self._is_prop_bool(
            value=value, prop_name='cancel_error', raise_error=True)
        self._cancel_error = value
        return None

    @property
    def name(self) -> str:
        '''
        Gets the name option

        `name` that represents the `originator` in error messages. Default: `type(originator)__name__`
        '''
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        '''Sets the name used to represent the class or object in error messages.'''
        self._is_prop_str(
            value=value, prop_name='name', raise_error=True)
        self._name = value
        return None

    @property
    def field_prefix(self) -> str:
        '''
        Gets the field prefix option

        The prefix use when setting attributes: Default: `_`.

        To add args without a prefix set the value `field_prefix = ''`

        This parameter is ignored when `field` is used in `assign()` method scuh as: `assign(msg='hi', field='message')`
        '''
        return self._field_prefix

    @field_prefix.setter
    def field_prefix(self, value: str) -> None:
        '''
        Sets the field prefix option

        The prefix use when setting attributes.

        To add args without a prefix set the value `field_prefix = ''`

        This parameter is ignored when `field` is used in `assign()` method scuh as: `assign(msg='hi', field='message')`
        '''
        self._is_prop_str(
            value=value, prop_name='field_prefix', raise_error=True)
        self._field_prefix = value
        return None

    @property
    def originator(self) -> object:
        '''
        Gets originator option

        object that attributes are assigned to via `assign()` method.
        This is usually a class.
        '''
        return self._obj

    @property
    def rule_error(self) -> bool:
        '''
        Get rule_error option

        Determins if rules can raise errors: Default `True`
        '''
        return self._rule_error

    @rule_error.setter
    def rule_error(self, value: bool) -> None:
        '''
        Get rule_error option

        Determins if rules can raise errors.
        '''
        self._is_prop_bool(
            value=value, prop_name='rule_error', raise_error=True)
        self._rule_error = value
        return None

    @property
    def rule_test_before_assign(self) -> bool:
        '''
        Gets rule_test_before_assign option

        If `True` rule testing will occur before assign value to attribute.
        If `True` and `rule_error` is `True` then rule errors will prevent assigning value.
        If `False` then attribute values will be assigned even if rules does not validate.
        Validation can still fail and errors can still be raised, except now the validation
        will take place after attribute value has been assigned.
        Default: `True`
        '''
        return self._rule_test_early

    @rule_test_before_assign.setter
    def rule_test_before_assign(self, value: bool) -> None:
        '''
        Sets rule_test_before_assign option.

        If `True` rule testing will occur before assign value to attribute.
        If `True` and `rule_error` is `True` then rule errors will prevent assigning value.
        If `False` then attribute values will be assigned even if rules does not validate.
        Validation can still fail and errors can still be raised, except now the validation
        will take place after attribute value has been assigned.
        '''
        self._is_prop_bool(
            value=value, prop_name='rule_test_before_assign', raise_error=True)
        self._rule_test_early = value
        return None

    # endregion Properties

# endregion class KwargsHelper

