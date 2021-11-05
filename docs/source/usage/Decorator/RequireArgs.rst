RequireArgs Usage
=================

:py:class:`~.decorator.RequireArgs` decorator defines required args for ``**kwargs`` of a function.

Includes features:

    * :doc:`/source/general/dec_feature/ftype`
    * :doc:`/source/general/dec_feature/opt_return`

.. code-block:: python

    from kwhelp.decorator import TypeCheckKw, RequireArgs

    @RequireArgs("speed", "limit", "name")
    @TypeCheckKw(arg_info={"speed": 0, "limit": 0, "hours": 0, "name": 1},
                    types=[(int, float), str])
    def speed_msg(**kwargs) -> str:
        name = kwargs.get('name')
        limit = kwargs.get('limit')
        speed = kwargs.get('speed')
        if limit > speed:
            msg = f"Current speed is '{speed}'. {name} may go faster as the limit is '{limit}'."
        elif speed == limit:
            msg = f"Current speed is '{speed}'. {name} are at the limit."
        else:
            msg = f"Please slow down limit is '{limit}' and current speed is '{speed}'."
        if 'hours' in kwargs:
            msg = msg + f" Current driving hours is '{kwargs['hours']}'."
        return msg

.. code-block:: python

    >>> result = speed_msg(speed=45, limit=60, name="John")
    >>> print(result)
    Current speed is '45'. John may go faster as the limit is '60'.

.. code-block:: python

    >>> result = speed_msg(speed=45, limit=60)
    >>> print(result)
    ValueError: 'name' is a required arg.

.. code-block:: python

    >>> result = speed_msg(speed="Fast", limit=60, name="John")
    >>> print(result)
    TypeError: Arg 'speed' is expected to be of '<class 'int'> | <class 'float'>' but got 'str'


