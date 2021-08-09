# coding: utf-8
from typing import Callable, List, Set, Union
from . base import HelperBase
from .. rules import IRule
# region class HelperArgs
class HelperArgs(HelperBase):
    def __init__(self, key: str, **kwargs):
        self._key: str = ''
        self._field = None
        self._require = False
        self._types = set()
        self._default = None
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
# endregion class HelperArgs
