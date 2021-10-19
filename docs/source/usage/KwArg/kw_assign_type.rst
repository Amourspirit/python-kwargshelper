Kw_assign Type Checking
=======================

Type checking can be done by adding ``types`` to :py:meth:`~.KwArg.kw_assign` method.
Type checking ensures the type of ``**kwargs`` values that are assigned to attributes of current instance of class.

.. code-block:: python

    from kwhelp import KwArg

    def speed_msg(**kwargs) -> str:
        kw = KwArg(**kwargs)
        kw.kw_assign(key="speed", require=True, types=[int, float])
        if kw.speed > 100:
            msg = f"Speed of '{kw.speed}' is fast. Caution recommended."
        elif kw.speed < -40:
            msg = f"Reverse speed of '{kw.speed}' is fast. Caution recommended."
        elif kw.speed < 0:
            msg = f"Reverse speed of '{kw.speed}'. Normal operations."
        else:
            msg = f"speed of '{kw.speed}'. Normal operations."
        return msg

speed_msg ``float`` value.

.. code-block:: python

    >>> result = speed_msg(speed = 35.8)
    >>> print(result)
    speed of '35.8'. Normal operations.

speed_msg ``float`` fast value.

.. code-block:: python

    >>> result = speed_msg(speed = 227.59)
    >>> print(result)
    Speed of '227.59' is fast. Caution recommended.

speed_msg ``int`` value.

.. code-block:: python

    >>> result = speed_msg(speed = -43)
    >>> print(result)
    Reverse speed of '-43' is fast. Caution recommended.

speed_msg no params.

.. code-block:: python

    >>> result = speed_msg()
    ValueError: KwArg arg 'speed' is required

speed_msg wrong type.

.. code-block:: python

    >>> result = speed_msg(speed = "Fast")
    TypeError: KwArg arg 'speed' is expected to be of '<class 'float'> | <class 'int'>' but got 'str'
