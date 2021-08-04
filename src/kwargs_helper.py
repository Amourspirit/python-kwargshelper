# coding: utf-8
from typing import List, Optional, Set, Union

class KwargsHelper:
    def __init__(self, obj: object, obj_kwargs:dict, **kwargs):
        self._obj: object = obj
        self._kwargs = obj_kwargs

        key = 'field_prefix'
        if key in kwargs:
            self._field_prefix = str(kwargs[key])
        else:
            self._field_prefix = '_'
        key = 'name'
        if key in kwargs:
            self._name = str(kwargs[key])
        else:
            self._name = type(obj).__name__

    def add(self, key: str, field: Optional[str] = None, require: bool = False, types: Optional[List[str]] = None, default: Optional[any] = None):
        if types == None:
            types = []
        _args = {
            "field": field,
            'require': require,
            'type': set(types)
        }
        if default is not None:
            _args['default'] = default
        self._assign(key, _args)

    def _assign(self, key: str, args:dict) -> None:
        if key in self._kwargs:
            value = self._kwargs[key]
            if len(args['type']) > 0:
                if not type(value).__name__ in args['type']:
                    msg = f"{self._name} arg '{key}'' is expected to be of '{self._get_formated_types(args['type'])}' but got '{type(value).__name__}'"
                    raise TypeError(msg)
            if args['field']:
                self._setattr(args['field'], value)
            else:
                self._setattr(f"{self._field_prefix}{key}", value)
        else:
            if 'default' in args:
                if args['field']:
                    self._setattr(args['field'], args['default'])
                else:
                    self._setattr(f"{self._field_prefix}{key}", args['default'])
            elif args['require']:
                # only test for required when default is not included
                raise ValueError(f"{self._name} arg '{key}' is required")

    def _get_formated_types(self, types: Set[str]) -> str:
        result = ''
        for i, t in enumerate(types):
            if i > 0:
                result = result + ' | '
            result = f"{result}{t}"
        return result

    def _setattr(self, field: str, value: any) -> None:
        setattr(self._obj, field, value)
        return None

    # region Properties
    @property
    def name(self)-> str:
        return self._name
    
    @name.setter
    def name(self, value:str) -> None:
        self._name = str(value)
    
    @property
    def field_prefix(self) -> str:
        return self._field_prefix
    
    @field_prefix.setter
    def field_prefix(self, value: str) -> None:
        self._field_prefix = str(value)
    # endregion Properties
