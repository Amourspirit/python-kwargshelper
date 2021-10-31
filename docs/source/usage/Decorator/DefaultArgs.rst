DefaultArgs Usage
=================

:py:class:`~.decorator.DefaultArgs` decorator that defines default values for ``**kwargs`` of a function.

.. code-block:: python

    from kwhelp.decorator import DefaultArgs

    @DefaultArgs(speed=45, limit=60, name="John")
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

    >>> result = speed_msg()
    >>> print(result)
    Current speed is '45'. John may go faster as the limit is '60'.

.. code-block:: python

    >>> result = speed_msg(name="Sue", speed=47)
    >>> print(result)
    Current speed is '47'. Sue may go faster as the limit is '60'.

