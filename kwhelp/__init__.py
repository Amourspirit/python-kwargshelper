# coding: utf-8
VERSION = __version__ = '1.2.2'
from typing import Any, Dict, List, Optional, Set, Callable, Union
from collections import UserList
from typing import List, Optional, Callable
from warnings import warn
from . rules import IRule
from . helper.base import HelperBase
from .helper import NO_THING


# region Custom Errors


class CancelEventError(Exception):
    '''Cancel Event Error'''


class ReservedAttributeError(ValueError):
    '''Error when a reserved attribute is attempted to be set'''
# endregion Custom Errors

# region class HelperArgs


class HelperArgs(HelperBase):
    """
    Helper class that provides KwArgs arguments
    """
    def __init__(self, key: str, **kwargs):
        """
        Constructor

        Args:
            key (str): Key Arg
        
        Keyword Arguments:
            field (str, optional): field arg. Default ``None``
            require (bool: optional): require arg. Default ``False``
            types (set, optional): types arg. Default Empty set
            default (obj, optional): Default arg. Default ``NO_THING``
            rules (list, optional): rules list. Default Empty List.
        """
        self._key: str = ''
        self._field = None
        self._require = False
        self._types = set()
        self._default = NO_THING
        self._rules = []
        self.key = key
        keys = ('field', 'require', 'types', 'default', 'rules')
        for key in keys:
            if key in kwargs:
                setattr(self, key, kwargs[key])

    def to_dict(self) -> dict:
        '''Gets a dictionary representation of current instance fields'''
        arg = {'key': self.key, 'require': self.require}
        if self.field is not None:
            arg['field'] = self.field
        if self.types is not None and len(self.types) > 0:
            arg['types'] = [itm for itm in self.types]
        if self.default is not NO_THING:
            arg['default'] = self.default
        if self.rules is not None and len(self.rules) > 0:
            arg['rules'] = self.rules
        return arg

    # region Properties

    @property
    def default(self) -> object:
        """
        Default Value
        
        :getter: Gets default value
        :setter: Sets default value
        """
        return self._default

    @default.setter
    def default(self, value: object) -> None:
        self._default = value
        return None

    @property
    def key(self) -> str:
        """
        Key Value

        :getter: Gets Key Value
        :setter: Sets key value
        """
        return self._key

    @key.setter
    def key(self, value: str) -> None:
        self._is_prop_str(value=value, prop_name='key', raise_error=True)
        self._key = value.strip()
        return None

    @property
    def field(self) -> Union[str, None]:
        """
        Field Value
        
        :getter: Gets field value
        :setter: Sets field value
        """
        return self._field

    @field.setter
    def field(self, value: Union[str, None]) -> None:
        if value is None:
            self._field = None
            return None
        self._is_prop_str(value=value, prop_name='field', raise_error=True)
        self._field = value.strip()
        return None

    @property
    def require(self) -> bool:
        """
        Require Value
        
        :getter: Gets require value
        :setter: Sets require value
        """
        return self._require

    @require.setter
    def require(self, value: bool) -> None:
        self._is_prop_bool(value=value, prop_name='require', raise_error=True)
        self._require = value
        return None

    @property
    def types(self) -> Set[type]:
        """
        Types values

        :getter: Gets types values
        :setter: Sets types values
        """
        return self._types

    @types.setter
    def types(self, value: Union[list, set, tuple]) -> None:
        if not isinstance(value, (list, set, tuple)):
            self._prop_error('types', value, 'Iterable')
        if isinstance(value, set):
            self._types = value
            return None
        self._types = set([itm for itm in value])
        return None

    @property
    def rules(self) -> List[Callable[[IRule], bool]]:
        """
        Rules values

        :getter: Gets rules
        :setter: Sets rules
        """
        return self._rules

    @rules.setter
    def rules(self, value: List[Callable[[IRule], bool]]) -> None:
        self._isinstance_prop(value=value, prop_name='rules',
                              prop_type=list, raise_error=True)
        self._rules = value
    # endregion Properties
# endregion class HelperArgs

# region class AssignBuilder


class AssignBuilder(UserList):
    '''Helper class for building list to use with "KwargsHelper.Assing() method'''

    def __init__(self) -> None:
        """
        Constructor
        """
        super().__init__(initlist=None)
        self._keys = set()

    def append(self, key: str, field: Optional[str] = None, require: bool = False, default: Optional[object] = None, types: Optional[List[type]] = None, rules: Optional[List[Callable[[IRule], bool]]] = None):
        """
        Appends dictionary item of parameters to list

        Args:
            key (str): the key of the key, value pair.
            field (Optional[str], optional): the name of the field.. Defaults to ``None``.
            require (bool, optional): Determins if ``key`` is required. Defaults to ``False``.
            default (Optional[object], optional): default value to assign if key value is missing. Defaults to ``None``.
            types (Optional[List[type]], optional): list of one or more types that the value of the key value pair must match. Defaults to ``None``.
            rules (Optional[List[Callable[[IRule], bool]]], optional): Rules to apply. Defaults to ``None``.

        Raises:
            TypeError: if ``key`` is not instance of``str``.
            ValueError: if ``key`` is empty or whitespace str.
            ValueError: if ``key`` has already exist.

        """

        if not isinstance(key, str):
            raise TypeError(self._get_type_error_method_msg(
                method_name='append', arg=key, arg_name='key', expected_type='str'
            ))
        _key = key.strip()
        if len(_key) == 0:
            raise ValueError(self._get_value_error_msg(
                method_name='append', arg=key, arg_name='key',
                msg="can not be empty or whitespace"
            ))
        if _key in self._keys:
            raise ValueError(
                self._get_value_error_msg(
                    method_name='append', arg=key, arg_name='key',
                    msg='already exist.'
                )
            )
        _args = HelperArgs(key=_key)
        _args.require = require
        if field is not None:
            _args.field = field
        if default is not None:
            _args.default = default
        if types is not None:
            _args.types = set(types)
        if rules is not None:
            _args.rules = rules

        super().append(_args)
        self._keys.add(_key)
        return None

    def append_helper(self, helper: HelperArgs):
        """
        Appends dictionary item of parameters to list

        Args:
            helper (HelperArgs): parameters to append

        Raises:
            TypeError: if ``helper`` is not instance of ``HelperArgs``
            ValueError: if ``helper.key`` is empty string.
            ValueError: if ``helper.key`` already exist.
        """
        if not isinstance(helper, HelperArgs):
            raise TypeError(self._get_type_error_method_msg(
                method_name='append_helper', arg=helper, arg_name='helper', expected_type='HelperArgs'
            ))
        if len(helper.key) == 0:
            raise ValueError(self._get_value_error_msg(
                method_name='append_helper', arg=helper, arg_name='helper.key',
                msg="can not be empty or whitespace"
            ))

        if helper.key in self._keys:
            raise ValueError(
                self._get_value_error_msg(
                    method_name='append_helper', arg=helper, arg_name='key',
                    msg='already exist.'
                )
            )
        super().append(helper)
        self._keys.add(helper.key)

    def remove(self, item: HelperArgs) -> None:
        """
        Removes an instance of ``HelperArgs`` from this instance

        Args:
            item (HelperArgs): Object to remove

        Raises:
            TypeError: if ``item`` is not instance of ``HelperArgs``

        Returns:
            [obj]: ``None``
        """
        if item is None:
            return None
        if not isinstance(item, HelperArgs):
            raise TypeError(self._get_type_error_method_msg(
                method_name='remove', arg=item, arg_name='item', expected_type='HelperArgs'
            ))
        _key = item.key
        super().remove(item)
        self._keys.remove(_key)
        return None

    def extend(self, other: 'AssignBuilder') -> None:
        """
        Extents this instance by merging values from other instance of ``AssignBuilder``.

        Args:
            other (AssignBuilder): instance to merge

        Raises:
            NotImplementedError: if ``other`` is not instance of ``AssignBuilder``.
        """
        if not isinstance(other, AssignBuilder):
            raise NotImplementedError(
                f"{self.__class__.__name__}.extend() only supports extending by instances of 'AssignBuilder'")
        for item in other:
            key: str = item.key
            if not key in self._keys:
                super().append(item)
                self._keys.add(key)

    def _get_type_error_method_msg(self, method_name: str, arg: object, arg_name: str, expected_type: str) -> str:
        result = f"{self.__class__.__name__}.{method_name}() arg '{arg_name}' is expecting type of '{expected_type}'. Got type of '{type(arg).__name__}'"
        return result

    def _get_value_error_msg(self, method_name: str, arg: object, arg_name: str, msg: str) -> str:
        result = f"{self.__class__.__name__}.{method_name}() arg '{arg_name}' {msg}"
        return result

    # region dunder methods
    def __getitem__(self, i: int) -> HelperArgs:
        return super().__getitem__(i)

    def __setitem__(self, i: int, helper: HelperArgs):
        if not isinstance(helper, HelperArgs):
            raise TypeError(self._get_type_error_method_msg(
                method_name='__setitem__', arg=helper, arg_name='helper', expected_type='HelperArgs'
            ))
        if i < 0 or i >= len(self):
            raise IndexError
        current = self[i]
        if helper.key != current.key:
            if helper.key in self._keys:
                raise ValueError(
                    self._get_value_error_msg(
                        method_name='__setitem__', arg=helper, arg_name='key',
                        msg='already exist.'
                    ))
        super().__setitem__(i, helper)
    # endregion dunder methods
# endregion class AssignBuilder

# region Event Args


class BeforeAssignAutoEventArgs:
    """
    Before Assign Auto Event Args
    """
    def __init__(self, key: str, value: object, field: str, originator: object):
        """
        Constructor

        Args:
            key (str): Key arg
            value (object): Value to be assigned
            field (str): Field that ``value`` is to be assigned to.
            originator (object): Object that ``value`` is to be assigned to.
        """
        self._key = key
        self._field_value = value
        self._cancel = False
        self._originator = originator
        self._field_name = field

    # region Properties
    @property
    def key(self) -> str:
        '''
        Gets the key of the key value pair
        '''
        return self._key

    @property
    def field_name(self) -> str:
        '''
        The field that will be assigned representing ``key``
        
        :getter: Gets the field that will be assigned representing ``key``
        :setter: Setts the field that will be assigned representing ``key``
        '''
        return self._field_name

    @field_name.setter
    def field_name(self, value: str) -> str:
        self._field_name = str(value).strip()

    @property
    def field_value(self) -> object:
        '''
        The value to be blindly assigned to property
        
        :getter: Gets the value to be blindly assigned to property
        :setter: Sets the value to be blindly assigned to property
        '''
        return self._field_value

    @field_value.setter
    def field_value(self, value: object) -> None:
        self._field_value = value

    @property
    def originator(self) -> object:
        '''Gets object that attributes assigned/modified for '''
        return self._originator

    @property
    def cancel(self) -> bool:
        """
        Cancel arg. If ``True`` process will be canceled.

        :getter: Gets cancel arg
        :setter: Sets cancel arg
        """
        return self._cancel

    @cancel.setter
    def cancel(self, value: bool) -> None:
        self._cancel = bool(value)
    # endregion Properties


class AfterAssignAutoEventArgs:
    """
    After Assign Auto Event Args
    """
    def __init__(self, key: str, originator: object):
        """
        Constructor

        Args:
            key (str): key arg
            originator (object): object that originated event
        """
        self._key = key
        self._field_value: object = None
        self._originator = originator
        self._field_name: str = ''
        self._success = False
        self._canceled = False

    # region Properties
    @property
    def key(self) -> str:
        '''
        Gets the key of the key value pair
        '''
        return self._key

    @property
    def field_name(self) -> str:
        '''
        The field that will be assigned representing ``key``.
        
        :getter: Gets the field that will be assigned representing ``key``.
        :setter: Sets the field that will be assigned representing ``key``.
        '''
        return self._field_name

    @property
    def field_value(self) -> object:
        return self._field_value

    @property
    def originator(self) -> object:
        '''Gets object that attributes assigned/modified for '''
        return self._originator

    @property
    def success(self) -> bool:
        '''Get assigning of attribue/value succeeded'''
        return self._success

    @property
    def canceled(self) -> bool:
        '''Get if assigment was canceled by before events'''
        return self._canceled
    # endregion Properties


class BeforeAssignEventArgs:
    """
    Before assign event args
    """
    def __init__(self, help_args: HelperArgs, originator: object):
        """
        Constructor

        Args:
            help_args (HelperArgs): HelperArgs object
            originator (object): Origanating object
        """
        self._helper_args = help_args
        self._originator = originator
        self._field_name: str = ''
        self._field_value: object = None
        self._cancel = False
    # region Properties

    @property
    def field_name(self) -> str:
        """
        The name of the field that value will be assigned
        
        :getter: Gets the name of the field that value will be assigned.
        :setter: Sets the name of the field that value will be assigned.
        """
        return self._field_name

    @field_name.setter
    def field_name(self, value: str) -> None:
        self._field_name = str(value)

    @property
    def field_value(self) -> object:
        """
        The value that will be assigned ``field_name``.

        :getter: Gets the value that will be assigned ``field_name``.
        :setter: Sets the value that will be assigned ``field_name``.
        """
        return self._field_value

    @field_value.setter
    def field_value(self, value: object) -> None:
        self._field_value = value

    @property
    def key(self) -> str:
        '''Gets the key currently being read'''
        return self._helper_args.key

    @property
    def helper_args(self) -> HelperArgs:
        ''''Get the args used to for modify/creating attribute'''
        return self._helper_args

    @property
    def originator(self) -> object:
        '''Gets object that attributes assigned/modified for '''
        return self._originator

    @property
    def cancel(self) -> bool:
        """
        Cancel arg. If ``True`` process will be canceled.

        :getter: Gets cancel arg
        :setter: Sets cancel arg
        """
        return self._cancel

    @cancel.setter
    def cancel(self, value: bool) -> None:
        self._cancel = bool(value)
    # endregion Properties


class AfterAssignEventArgs:
    """
    After Assign Event Args
    """
    def __init__(self, help_args: HelperArgs, originator: object) -> None:
        """
        Constructor

        Args:
            help_args (HelperArgs): HelperArgs object
            originator (object): Origanating object
        """
        self._helper_args = help_args
        self._field_name: str = ''
        self._field_value: object = None
        self._originator = originator
        self._rules_passed = True
        self._canceled = False
        self._success = False
    # region Properties

    @property
    def key(self) -> str:
        '''Gets the key currently being read'''
        return self._helper_args.key

    @property
    def field_name(self) -> str:
        '''The name of the field that value was assigned'''
        return self._field_name

    @property
    def field_value(self) -> object:
        '''The value that is assigned to `field_name`'''
        return self._field_value

    @property
    def helper_args(self) -> HelperArgs:
        ''''Get the args used to for modify/creating attribute'''
        return self._helper_args

    @property
    def originator(self) -> object:
        '''Gets object that attributes assigned/modified for '''
        return self._originator

    @property
    def rules_passed(self) -> bool:
        '''Get if all applied rules passed'''
        return self._rules_passed

    @property
    def canceled(self) -> bool:
        '''Get if assigment was canceled by before events'''
        return self._canceled

    @property
    def success(self) -> bool:
        """
        Determinins if assigning of attribue/value succeeded

        :getter: Get assigning of attribue/value succeeded
        :setter: Sets assigning of attribue/value succeeded
        """
        return self._success

    @success.setter
    def success(self, value: bool) -> None:
        self._success = bool(value)
    # endregion Properties
# endregion Event Args

# region class KwargsHelper


class KwargsHelper(HelperBase):
    """
    kwargs helper class. Assigns attributes to class with various checks

    Example:
        .. code-block:: python

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
    """
    # region init

    def __init__(self, originator: object, obj_kwargs: dict, **kwargs):
        """
        Constructor

        Args:
            originator (object): object that attributes are assigned to via ``assign()`` method. This is usually a class.
            obj_kwargs (dict): The dictionary of key value args used to set values of attributes.
                Often passed in as ``obj_kwargs = {**kwargs}``

        Keyword Arguments:
            field_prefix (str, optional): sets the ``field_prefix`` property. Default ``_``.
            name (str, optional): sets the `field_prefix` property.
                Default is the name of ``originator`` object.
            cancel_error (bool, optional): sets the `cancel_error` property. Default ``True``.
            rule_error (bool, optional): sets the ``rule_error`` property. Default ``False``.
            assign_true_not_required (bool, optional): sets the ``assign_true_not_required`` property.
                Default ``True``.
            type_instance_check (bool, optional): If ``True`` and :py:meth:`.KwargsHelper.assign`` arg ``types`` is set
                then values will be tested also for isinstance rather then just type check if type check is ``False``.
                If ``False`` then values willl only be tested as type.
                Default ``True``

        Raises:
            TypeError: if any arg is not of the correct type.
        """
        if not isinstance(obj_kwargs, dict):
            raise TypeError(self._get_type_error_method_msg(
                method_name='__init__', arg=obj_kwargs,
                arg_name='obj_kwargs', expected_type=dict
            ))
        self._obj: object = originator
        self._callbacks = None
        self._kwargs = obj_kwargs
        self._auto_assigned = False
        self._keys: set = set(self._kwargs.keys())
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

        key = 'type_instance_check'
        if key in kwargs:
            self._type_instance_check: bool = kwargs[key]
            self._is_arg_bool(
                method_name=m_name, arg=self._type_instance_check, arg_name=key, raise_error=True)
        else:
            self._type_instance_check: bool = True

    # endregion init

    # region Public Methods
    def auto_assign(self) -> bool:
        """
        Assigns all of the key, value pairs of ``obj_kwargs`` passed into constructor to ``originator``,
        unless the event is canceled in ``BeforeAssignBlindEventArgs`` then key, value pair will be added automacally to ``originator``.

        Returns:
            bool: ``True`` of all key, value pairs are added; Otherwise, ``False``.

        Note:
            Call back events are supported via :py:meth:`~.KwargsHelper.add_handler_before_assign_auto`
            and :py:meth:`~.KwargsHelper.add_handler_after_assign_auto` methods.
        """
        if self._is_auto_assign_handlers():
            return self._auto_assign_with_cb()
        return self._auto_assign_no_cb()

    def assign(self, key: str, field: Optional[str] = None, require: bool = False, default: Optional[object] = NO_THING, types: Optional[List[type]] = None, rules: Optional[List[Callable[[IRule], bool]]] = None) -> bool:
        """
        Assigns attribute value to ``obj`` passed in to constructor. Attributes are created if they do not exist.

        Args:
            key (str): the key of the key, value pair that is required or optional in ``obj_kwargs`` passed into to constructor.
            field (str, optional): the name of the field to assign a value. If ``field``
                is omitted then field name is built using ``instance.field_prefix`` + ``key``.
                If included then ``instance.field_prefix`` will be ignored.
                Defaults to ``None``.
            require (bool, optional): Determins if ``key`` is required to be in ``obj_kwargs`` passed into to constructor.
                if ``default`` is passed in then ``require`` is ignored.
                Defaults to ``False``.
            default (object, optional): default value to assign to key attribute if no value is found in
                ``obj_kwargs`` passed into to constructor.
                If ``default`` is passed in then ``require`` is ignored.
                Defaults to ``NO_THING``.
            types (List[type], optional): a type list of one or more types that the value of the key value pair must match.
                For example if a value is required to be only ``str`` then ``types=[str]``.
                If value is required to be ``str`` or ``int`` then ``types=[str, int]``.
                In this example if value is not type ``str`` then ``TypeError`` is raised.
                If ``types`` is omitted then a value can be any type unless there is a rule in ``rules`` that is otherwise.
                Defaults to ``None``.
            rules (List[Callable[[IRule], bool]], optional): List of rules that must be passed before assignment can take place.
                Defaults to ``None``.

        Returns:
            bool: ``True`` if attribute assignment is successful; Otherwise, ``False``
        """
        m_name = 'assign'
        self._is_arg_str_empty_null(
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
        if default is not NO_THING:
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
        """
        Assigns attribute value using instance of HelperArgs. See :py:meth:`~.KwargsHelper.assign` method.

        Args:
            helper (HelperArgs): instance to assign.

        Returns:
            bool: ``True`` if attribute assignment is successful; Otherwise, ``False``.
        """
        self._isinstance_method(method_name='assign_helper', arg=helper,
                                arg_name='helper', arg_type=HelperArgs, raise_error=True)
        d = helper.to_dict()
        return self.assign(**d)

    def is_key_existing(self, key: str) -> bool:
        """
        Gets if the key exist in  kwargs dictionary passed in to the constructor by ``obj_kwargs`` arg.

        Args:
            key (str): Key value to check for existance.

        Returns:
            bool: ``True`` if ``key`` exist; Otherwise, ``False``.
        """
        valid_key = self._is_arg_str_empty_null(
            method_name='is_key_existing', arg=key, arg_name='key', raise_error=False)
        if valid_key == False:
            return False
        return key in self._kwargs
    # endregion Public Methods

    # region private methods
    def _auto_assign_no_cb(self) -> bool:
        for k, v in self._kwargs.items():
            field_name = f"{self._field_prefix}{k}"
            setattr(self._obj, field_name, v)
            # self._obj.__dict__[field_name] = v
            self._remove_key(key=k)
        return True

    def _auto_assign_with_cb(self) -> bool:
        '''
        Assigns all key, value pairs blindly unless interupted by event cancel
        @return: `True` if all key, values have been added; Otherwise, `False`
        '''
        self._auto_assigned == True
        result = True
        for k, v in self._kwargs.items():
            field_name = f"{self._field_prefix}{k}"
            before_args = BeforeAssignAutoEventArgs(
                key=k, value=v, field=field_name, originator=self._obj)
            self._on_before_assign_auto(event_args=before_args)
            _field = before_args.field_name
            _value = before_args.field_value
            after_args = AfterAssignAutoEventArgs(key=k, originator=self._obj)
            after_args._canceled = before_args.cancel
            if before_args.cancel == True:
                if self._cancel_error == True:
                    raise CancelEventError(
                        f"{self.__class__.__name__}.assign() canceled in 'BeforeAssignBlindEventArgs'")
                else:
                    result = False
            else:
                # self._obj.__dict__[_field] = _value
                setattr(self._obj, _field, _value)
                after_args._success = True
                after_args._field_name = _field
                after_args._field_value = _value
                self._remove_key(key=k)
            self._on_after_assign_auto(event_args=after_args)
        return result

    def _assign(self, args: HelperArgs, before_args: BeforeAssignEventArgs, after_args: AfterAssignEventArgs) -> None:
        def _is_type_instance(_types:Set[type], _value ):
            result = False
            for t in _types:
                if isinstance(_value, t):
                    result = True
                    break
            return result

        result = False
        key = args.key
        if key in self._kwargs:
            value = self._kwargs[key]
            if len(args.types) > 0:
                if not type(value) in args.types:
                    # object such as PosixPath inherit from more than on class (Path, PurePosixPath)
                    # testing if PosixPath is type of Path is False.
                    # for this reason will do an instace check as well. isinstance(_posx, Path) is True
                    is_valid_type = False
                    if self._type_instance_check == True and _is_type_instance(args.types, value):
                        is_valid_type = True
                    
                    if is_valid_type is False:
                        msg = f"{self._name} arg '{key}' is expected to be of '{self._get_formated_types(args.types)}' but got '{type(value).__name__}'"
                        raise TypeError(msg)
            if args.field:
                result = self._setattr(
                    args.field, value, before_args, after_args, args=args)
            else:
                result = self._setattr(f"{self._field_prefix}{key}",
                                       value, before_args, after_args, args=args)
        else:
            if args.default is not NO_THING:
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

        self._on_before_assign(event_args=before_args)

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
        # self._obj.__dict__[_field] = _value
        self._remove_key(args.key)
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

    def _remove_key(self, key: str) -> bool:
        '''
        Removes a key from the internal keys.
        @return: `True` if key was removed; Otherwise, `False`
        '''
        if key in self._keys:
            self._keys.remove(key)
            return True
        return False

    def _is_auto_assign_handlers(self) -> bool:
        '''
        Gets if any handler are set for Auto Assign
        '''
        if self._callbacks is None:
            return False
        if 'on_before_assign_auto' in self._callbacks:
            return True
        if 'on_after_assign_auto' in self._callbacks:
            return True
        return False
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
    def _on_before_assign(self, event_args: BeforeAssignEventArgs):
        self._trigger("on_before_assign", event_args)

    def _on_after_assign(self, event_args: AfterAssignEventArgs):
        self._trigger("on_after_assign", event_args)

    def _on_before_assign_auto(self, event_args: BeforeAssignAutoEventArgs):
        self._trigger("on_before_assign_auto", event_args)

    def _on_after_assign_auto(self, event_args: AfterAssignAutoEventArgs):
        self._trigger("on_after_assign_auto", event_args)
    # endregion raise events

     # region Handlers
    def add_handler_before_assign(self, callback: Callable[['KwargsHelper', BeforeAssignEventArgs], None]):
        """
        Add handler before assign

        Args:
            callback (Callable[['KwargsHelper', BeforeAssignEventArgs], None]): Callback Method
        """
        self._on("on_before_assign", callback)

    def add_handler_after_assign(self, callback: Callable[['KwargsHelper', AfterAssignEventArgs], None]):
        """
        Add handler afer assign

        Args:
            callback (Callable[['KwargsHelper', AfterAssignEventArgs], None]): Callback Method
        """
        self._on("on_after_assign", callback)

    def add_handler_before_assign_auto(self, callback: Callable[['KwargsHelper', BeforeAssignAutoEventArgs], None]):
        """
        Adds handler for before assigne auto

        Args:
            callback (Callable[['KwargsHelper', BeforeAssignAutoEventArgs], None]): Callback Method
        """
        self._on("on_before_assign_auto", callback)

    def add_handler_after_assign_auto(self, callback: Callable[['KwargsHelper', AfterAssignAutoEventArgs], None]):
        """
        Adds handler for after assign auto

        Args:
            callback (Callable[['KwargsHelper', AfterAssignAutoEventArgs], None]): Callback Method
        """
        self._on("on_after_assign_auto", callback)
    # endregion

    # region Properties
    @property
    def assign_true_not_required(self) -> bool:
        """
        Determines ``assign_true_not_required`` Option.
        If ``True`` then and a non-required arg is assigned via :py:meth:`~.KwargsHelper.assign`.
        then :py:meth:`~.KwargsHelper.assign` returns ``True`` even if the arg failed to be applied.
        In an ``after callback`` method set by :py:meth:`~.KwargsHelper.add_handler_after_assign`
        success in :py:attr:`.AfterAssignEventArgs.success` property is ``False`` if arg was not assigned.
        Default ``True``

        :getter: Gets option value.
        :setter: Sets option value.
        """
        return self._assign_true_not_required

    @assign_true_not_required.setter
    def assign_true_not_required(self, value: bool) -> None:
        self._is_prop_bool(
            value=value, prop_name='assign_true_not_required', raise_error=True)
        self._assign_true_not_required = value
        return None

    @property
    def cancel_error(self) -> bool:
        """
        Determins if an error will be raised if cancel is set in
        :py:class:`BeforeAssignEventArgs` of a callback. Default ``True``.

        :getter: Gets cancel_error option.
        :setter: Sets cancel_error option.
        """
        return self._cancel_error

    @cancel_error.setter
    def cancel_error(self, value: bool) -> None:
        self._is_prop_bool(
            value=value, prop_name='cancel_error', raise_error=True)
        self._cancel_error = value
        return None

    @property
    def name(self) -> str:
        """
        Determins name option.
        ``name`` that represents the ``originator`` in error messages. Default: ``type(originator)__name__``

        :getter: Gets name option.
        :setter: Sets name option
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._is_prop_str(
            value=value, prop_name='name', raise_error=True)
        self._name = value
        return None

    @property
    def field_prefix(self) -> str:
        """
        Determines the field prefix option.
        The prefix use when setting attributes: Default: ``_``.
        To add args without a prefix set the value ``field_prefix = ''``
        This parameter is ignored when ``field`` is used in :py:meth:`~.KwargsHelper.assign` method such as: ``assign(msg='hi', field='message')``

        :getter: Gets the field prefix option.
        :setter: Sets the field prefix option.
        """
        return self._field_prefix

    @field_prefix.setter
    def field_prefix(self, value: str) -> None:
        self._is_prop_str(
            value=value, prop_name='field_prefix', raise_error=True)
        self._field_prefix = value
        return None

    @property
    def originator(self) -> object:
        '''
        Gets originator option

        object that attributes are assigned to via :py:meth:`~.KwargsHelper.assign` method.
        This is usually a class.
        '''
        return self._obj

    @property
    def rule_error(self) -> bool:
        """
        Determins rule_error option.
        Default ``True``

        :getter: Gets rule_error option.
        :setter: Sets rule_error option.
        """
        return self._rule_error

    @rule_error.setter
    def rule_error(self, value: bool) -> None:
        self._is_prop_bool(
            value=value, prop_name='rule_error', raise_error=True)
        self._rule_error = value
        return None

    @property
    def rule_test_before_assign(self) -> bool:
        """
        Determines rule_test_before_assign option.
        If ``True`` rule testing will occur before assign value to attribute.
        If ``True`` and :py:attr:`~.KwargsHelper.rule_error` is ``True`` then rule errors will prevent assigning value.
        If ``False`` then attribute values will be assigned even if rules does not validate.
        Validation can still fail and errors can still be raised, except now the validation
        will take place after attribute value has been assigned.
        Default: ``True``

        :getter: Gets rule_test_before_assign option.
        :setter: Sets rule_test_before_assign option.
        """
        return self._rule_test_early

    @rule_test_before_assign.setter
    def rule_test_before_assign(self, value: bool) -> None:
        self._is_prop_bool(
            value=value, prop_name='rule_test_before_assign', raise_error=True)
        self._rule_test_early = value
        return None

    @property
    def kw_args(self) -> Dict[str, Any]:
        '''Gets the kwargs dictionary passed in to the constructor by ``obj_kwargs`` arg'''
        return self._kwargs

    @property
    def unused_keys(self) -> Set[str]:
        '''
        Gets any unused keys passed into constructor via ``obj_kwargs``

        This would be a set of keys that were never used passed into the constructor.
        '''
        return self._keys
    # endregion Properties

# endregion class KwargsHelper

# region class KwArg


class KwArg(HelperBase):
    '''Class for assigning kwargs to autogen fields with type checking and testing'''
    _RESERVED_INTERNAL_FIELDS: Set[str] = set(
        ['kwargs_helper', 'assign', 'assign_helper', '_kw_args_helper_class_instance',
         '__init__', 'is_attribute_exist', 'is_key_existing',
         '_get_type_error_method_msg', '_get_value_error_msg',
         '_get_type_error_prop_msg', '_isinstance_prop',
         '_prop_error', '_is_prop_str', '_is_prop_bool', '_is_prop_int',
         '_isinstance_method', '_is_arg_str', '_is_arg_bool',
         '_arg_type_error', '_get_name_type_obj', 'kw_unused_keys', 'kw_auto_assign', 'kw_assign', 'kw_assign_helper'])

    def __init__(self, **kwargs):
        """
        Constructor

        Keyword Arguments:
            kwargs (dict): dictionary of args

        Example:
            .. code-block:: python

                def my_method(**kwargs) -> str:
                    kw = KwArg(**kwargs)
                    kw.assign(key='first', require=True, types=[int])
                    kw.assign(key='second', require=True, types=[int])
                    kw.assign(key='msg', types=[str], default='Result:')
                    kw.assign(key='end', types=[str])
                    first:int = kw.first
                    second:int = kw.second
                    msg: str = kw.msg
                    _result = first + second
                    if kw.is_attribute_exist('end'):
                        return_msg = f'{msg} {_result}{kw.end}'
                    else:
                        return_msg = f'{msg} {_result}'
                    return return_msg
        """
        self._kw_args_helper_class_instance = KwargsHelper(
            originator=self, obj_kwargs={**kwargs})
        self._kw_args_helper_class_instance.field_prefix = ''

    def kw_auto_assign(self) -> bool:
        """
        Assigns all of the key, value pairs of `obj_kwargs` passed into constructor to ``originator``,
        unless the event is canceled in :py:class:`.BeforeAssignAutoEventArgs` then key, value pair
        will be added automacally to ``originator``.
        
        Call back events are supported via :py:meth:`.kwargs_helper.add_handler_before_assign_auto`
        and :py:meth:`.kwargs_helper.add_handler_after_assign_auto` methods.
        
        Wrapper method for :py:meth:`.KwargsHelper.auto_assign`

        Returns:
            bool: ``True`` of all key, value pairs are added; Otherwise, ``False``
        """
        return self._kw_args_helper_class_instance.auto_assign()

    def assign(self, key: str, field: Optional[str] = None, require: bool = False, default: Optional[object] = NO_THING, types: Optional[List[type]] = None, rules: Optional[List[Callable[[IRule], bool]]] = None) -> bool:
        """
        .. deprecated:: 1.2.0
            use :py:meth:`~.KwArg.kw_assign` instead
        """
        # https://docs.python.org/3/library/warnings.html#warnings.warn
        warn("use kw_assign instead", DeprecationWarning, stacklevel=2)
        return self.kw_assign(key=key,field=field,require=require,default=default,types=types,rules=rules)
    
    def kw_assign(self, key: str, field: Optional[str] = None, require: bool = False, default: Optional[object] = NO_THING, types: Optional[List[type]] = None, rules: Optional[List[Callable[[IRule], bool]]] = None) -> bool:
        """
        Assigns attribute value to current instance passed in to constructor. Attributes automatically.

        Args:
            key (str): the key of the key, value pair that is required or optional in ``kwargs`` passed into to constructor.
            field (str, optional): the name of the field to assign a value. 
                if ``field`` is omitted then field name is built using ``key``.
                If included then ``kwargs_helper.field_prefix`` will be ignored.
                Defaults to ``None``.
            require (bool, optional): Determins if ``key`` is required to be in `kwargs` passed into to constructor.
                if ``default`` is passed in then ``require`` is ignored.
                Defaults to ``False``.
            default (object, optional): default value to assign to key attribute if no value is
                found in ``kwargs`` passed into to constructor.
                If ``default`` is passed in then ``require`` is ignored.
                Defaults to ``NO_THING``.
            types (List[type], optional): a type list of one or more types that the value of the
                key value pair must match.
                For example if a value is required to be only ``str`` then ``types=[str]``.
                In this example if value is not type ``str`` then ``TypeError`` is raised
                If value is required to be `str` or `int` then ``types=[str, int]``.
                Defaults to ``None``.
            rules (List[Callable[[IRule], bool]], optional): List of callable rules.
                All rules must pass in order for attribute assignment to be a success.
                Defaults to `None`.

        Raises:
            ReservedAttributeError: if ``key`` is a reserved keyword
            ReservedAttributeError: if ``field`` is a reserved keyword

        Returns:
            bool: ``True`` if attribute assignment is successful; Otherwise, ``False``
        """
        m_name = 'assign'
        self._is_arg_str_empty_null(
            method_name=m_name, arg=key, arg_name='key', raise_error=True)
        if field is None:
            if key in KwArg._RESERVED_INTERNAL_FIELDS:
                raise ReservedAttributeError(
                    f"{self.__class__.__name__}.{key} is a reserved keyword. Try using the 'field' arg for a different field name")
        else:
            if field in KwArg._RESERVED_INTERNAL_FIELDS:
                raise ReservedAttributeError(
                    f"{self.__class__.__name__}.{field} is a reserved keyword. Try using a differne field name.")
        return self._kw_args_helper_class_instance.assign(key=key, field=field, require=require, default=default, types=types, rules=rules)

    def assign_helper(self, helper: HelperArgs) -> bool:
        # https://docs.python.org/3/library/warnings.html#warnings.warn
        warn("use kw_assign_helper instead", DeprecationWarning, stacklevel=2)
        return self.kw_assign_helper(helper=helper)

    def kw_assign_helper(self, helper: HelperArgs) -> bool:
        """
        Assigns attribute value using instance of HelperArgs. See :py:meth:`~.KwArg.kw_assign` method.

        Args:
            helper (HelperArgs): instance to assign.

        Returns:
            bool: ``True`` if attribute assignment is successful; Otherwise, ``False``
        """
        self._isinstance_method(method_name='assign_helper', arg=helper,
                                arg_name='helper', arg_type=HelperArgs, raise_error=True)
        d = helper.to_dict()
        return self.kw_assign(**d)

    # region Public Methods
    def is_attribute_exist(self, attrib_name: str) -> bool:
        """
        Gets if ``attrib_name`` exist the current instance.
        
        Use this method when:

        * When assigning a key that is not required it may not exist in the current instance.
        * When assing key that are required then the field will exist in the current instance.

        Args:
            attrib_name (str): This is usually the ``key`` value of :py:meth:`~.KwArg.kw_assign`
                or ``field`` value of :py:meth:`~.KwArg.kw_assign`.

        Returns:
            bool: ``True`` if ``attrib_name`` exist in current instance; Otherwise, ``False``.
        """
        # if an key is assigned and not required it may not exist in curren instance
        valid_key = self._is_arg_str_empty_null(
            method_name='has_attribute', arg=attrib_name, arg_name='key', raise_error=False)
        if valid_key == False:
            return False
        _key = attrib_name.strip()
        return hasattr(self, _key)

    def is_key_existing(self, key: str) -> bool:
        '''
        Gets if the key exist in current kwargs.
        Basically shortcut for `key in kwargs`
        '''
        return self._kw_args_helper_class_instance.is_key_existing(key)
    # endregion Public Methods

    # region Properties

    @property
    def kwargs_helper(self) -> KwargsHelper:
        '''Get instance of KwargsHelper used to add fields current instance'''
        return self._kw_args_helper_class_instance

    @property
    def kw_unused_keys(self) -> Set[str]:
        '''
        Gets any unused keys passed into constructor via ``**kwargs``

        This would be a set of keys that were never used passed into the constructor.
        '''
        return self._kw_args_helper_class_instance.unused_keys
    # endregion Properties

# endregion class KwArg
