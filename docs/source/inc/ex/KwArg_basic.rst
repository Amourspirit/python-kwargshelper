.. code-block:: python

    from kwhelp import KwArg

    def my_method(**kwargs) -> str:
        kw = KwArg(**kwargs)
        kw.kw_assign(key='first', require=True, types=[int])
        kw.kw_assign(key='second', require=True, types=[int])
        kw.kw_assign(key='msg', types=[str], default='Result:')
        kw.kw_assign(key='end', types=[str])
        first:int = kw.first
        second:int = kw.second
        msg: str = kw.msg
        _result = first + second
        if kw.is_attribute_exist('end'):
            return_msg = f'{msg} {_result}{kw.end}'
        else:
            return_msg = f'{msg} {_result}'
        return return_msg