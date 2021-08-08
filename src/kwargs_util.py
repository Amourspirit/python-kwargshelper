# coding: utf-8
from collections import UserList
from typing import List, Optional, Set, Callable, Union
from abc import ABC, abstractmethod
from . kwarg_rules import IRule

# region class HelperBase
class HelperBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        '''Class Constructor'''

    # region private methods

    def _get_type_error_method_msg(self, method_name: str, arg: object, arg_name: str, expected_type: str) -> str:
        result = f"{self.__class__.__name__}.{method_name}() arg '{arg_name}' is expecting type of '{expected_type}'. Got type of '{type(arg).__name__}'"
        return result

    def _get_value_error_msg(self, method_name: str, arg: object, arg_name: str, msg: str) -> str:
        result = f"{self.__class__.__name__}.{method_name}() arg '{arg_name}' {msg}"
        return result

    # region Property Helpers
    def _get_type_error_prop_msg(self, prop_name: str, value: object, expected_type: str) -> str:
        result = f"{self.__class__.__name__}.{prop_name} is expecting type of '{expected_type}'. Got type of '{type(value).__name__}'"
        return result

    def _isinstance_prop(self, value: object, prop_name: str, prop_type: object, raise_error: Optional[bool] = False):
        result = isinstance(value, prop_type)
        if result == False and raise_error == True:
            self._prop_error(prop_name=prop_name,
                             value=value, expected_type=self._get_name_type_obj(prop_type))
        return result

    def _prop_error(self, prop_name: str, value: object, expected_type: str):
        raise TypeError(self._get_type_error_prop_msg(
            prop_name=prop_name, value=value, expected_type=expected_type
        ))

    def _is_prop_str(self, value: object, prop_name: str, raise_error: Optional[bool] = False) -> bool:
        result = self._isinstance_prop(
            value=value, prop_name=prop_name, prop_type=str, raise_error=raise_error)
        return result

    def _is_prop_bool(self, value: object, prop_name: str, raise_error: Optional[bool] = False) -> bool:
        result = self._isinstance_prop(
            value=value, prop_name=prop_name, prop_type=bool, raise_error=raise_error)
        return result

    def _is_prop_int(self, value: object, prop_name: str, raise_error: Optional[bool] = False) -> bool:
        result = self._isinstance_prop(
            value=value, prop_name=prop_name, prop_type=int, raise_error=raise_error)
        return result
    # endregion Property Helpers

    # region method Arg Helpers
    def _isinstance_method(self, method_name: str, arg: object, arg_name: str, arg_type: object, raise_error: Optional[bool] = False) -> bool:
        result = isinstance(arg, arg_type)
        if result == False and raise_error == True:
            self._arg_type_error(self._get_type_error_method_msg(
                method_name=method_name, arg=arg, arg_name=arg_name,
                expected_type=self._get_name_type_obj(
                    arg_type)
            ))
        return result

    def _is_arg_str(self, method_name: str, arg: object, arg_name: str, raise_error: Optional[bool] = False) -> bool:
        result = self._isinstance_method(
            method_name=method_name, arg=arg, arg_name=arg_name, arg_type=str, raise_error=raise_error)
        return result
    
    def _is_arg_bool(self, method_name: str, arg: object, arg_name: str, raise_error: Optional[bool] = False) -> bool:
        result = self._isinstance_method(
            method_name=method_name, arg=arg, arg_name=arg_name, arg_type=bool, raise_error=raise_error)
        return result
    # endregion method Arg Helpers

    def _arg_type_error(self, method_name: str, arg: object, arg_name: str, expected_type: str):
        raise TypeError(self._get_type_error_method_msg(
            method_name=method_name, arg=arg, arg_name=arg_name, expected_type=expected_type
        ))

    def _get_name_type_obj(self, obj: object) -> str:
        '''
        Gets the name of an object instance name or type name
        '''
        if isinstance(obj, type):
            return str(obj.__name__)
        return str(obj.__class__.__name__)
    # endregion private methods
# endregion class HelperBase

# region class HelperArgs
class HelperArgs(HelperBase):
    def __init__(self, key:str, **kwargs):
        m_name = '__init__'
        self._key: str = ''
        self._field = None
        self._require = False
        self._types = set()
        self._default = None
        self._rules = []
        self.key = key
        keys = ('field','require', 'types','default', 'rules')
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
        if self.default is not None:
            arg['default'] = self.default
        if self.rules is not None and len(self.rules) > 0:
            arg['rules'] = self.rules
        return arg

    # region Properties

    @property
    def default(self) -> object:
        return self._default

    @default.setter
    def default(self, value: object) -> None:
        self._default = value
        return None

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, value: str) -> None:
        self._is_prop_str(value=value, prop_name='key', raise_error=True)
        self._key = value.strip()
        return None

    @property
    def field(self) -> Union[str, None]:
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
        return self._require

    @require.setter
    def require(self, value: bool) -> None:
        self._is_prop_bool(value=value, prop_name='require', raise_error=True)
        self._require = value
        return None

    @property
    def types(self) -> Set[str]:
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
        return self._rules

    @rules.setter
    def rules(self, value: List[Callable[[IRule], bool]]) -> None:
        self._isinstance_prop(value=value, prop_name='rules',
                              prop_type=list, raise_error=True)
        self._rules = value
    # endregion Properties
# region Event Args
# endregion class HelperArgs

class CancelEventError(Exception):
    '''Cancel Event Error'''


class BeforeAssignEventArgs:
    def __init__(self, help_args: HelperArgs, originator: object):
        self._helper_args = help_args
        self._originator = originator
        self._field_name: str = ''
        self._field_value: object = None
        self._cancel = False
    # region Properties

    @property
    def field_name(self) -> str:
        '''The name of the field that value will be assigned'''
        return self._field_name

    @field_name.setter
    def field_name(self, value: str) -> None:
        self._field_name = str(value)

    @property
    def field_value(self) -> object:
        '''The value that will be assigned`field_name`'''
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
        return self._cancel

    @cancel.setter
    def cancel(self, value: bool) -> None:
        self._cancel = bool(value)
    # endregion Properties


class AfterAssignEventArgs:
    def __init__(self, help_args: HelperArgs, originator: object) -> None:
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
        '''Get assigning of attribue/value succeeded'''
        return self._success

    @success.setter
    def success(self, value: bool) -> None:
        '''Set assigning of attribue/value succeeded'''
        self._success = bool(value)
    # endregion Properties
# endregion Event Args

# region class KwargsHelper

# region class AssignBuilder
class AssignBuilder(UserList):
    '''Helper class for building list to use with "KwargsHelper.Assing() method'''

    def __init__(self) -> None:
        super().__init__(initlist=None)
        self._keys = set()

    def append(self, key: str, field: Optional[str] = None, require: bool = False, default: Optional[object] = None, types: Optional[List[str]] = None, rules: Optional[List[Callable[[IRule], bool]]] = None):
        '''
        Appends dictionary item of parameters to list
        @key: Type:str, the key of the key, value pair.
        @field: (optional) Type:str the name of the field.
        @require: (optional) Type:bool Default: `False`
        @default: (optional) Type:str, default value to assign.
        @types: (optional) Type:List[str], a string list of one or more types that the value of the key value pair must match.
        @rules: (optional) Type:List[Callable[[IRule], bool]]
        '''
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
        '''
        Appends dictionary item of parameters to list
        @helper: args to add
        '''
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
