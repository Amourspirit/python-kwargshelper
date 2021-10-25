TypeCheckerAny Usage
====================

:py:class:`~.decorator.TypeCheckerAny` decorator reqires that each args of a function match a ``type``.

Decorating with ``*args``
-------------------------

This example requires that all args positive ``int`` or positive ``float``.

.. code-block:: python

    from kwhelp.decorator import RuleCheckAny
    import kwhelp.rules as rules

    @TypeCheckerAny(types=[int, float])
    def add_numbers(*args) -> float:
        result = 0.0
        for arg in args:
            result += float(arg)
        return result

Adding numbers works as expected.

.. code-block:: python

    >>> result = add_numbers(1, 4, 6.9, 3.9, 7.3)
    >>> print(result)
    23.1

Types dictate that if a type is not ``int`` or ``float`` then an error will be raised.

.. code-block:: python

    >>> result = add_numbers(2, 1.2, "4")
    TypeError: Arg Value is expected to be of '<class 'int'> | <class 'float'>' but got 'str'

Decorating with Key, Value
--------------------------

This example requires that all args are ``int`` or ``float``.

.. code-block:: python

    from kwhelp.decorator import RuleCheckAny
    import kwhelp.rules as rules

    @TypeCheckerAny(types=[int, float])
    def speed_msg(speed, limit, **kwargs) -> str:
        if limit > speed:
            msg = f"Current speed is '{speed}'. You may go faster as the limit is '{limit}'."
        elif speed == limit:
            msg = f"Current speed is '{speed}'. You are at the limit."
        else:
            msg = f"Please slow down limit is '{limit}' and you are currenlty going '{speed}'."
        if 'hours' in kwargs:
            msg = msg + f" Current driving hours is '{kwargs['hours']}'"
        return msg

Adding positive numbers works as expected.

.. code-block:: python

    >>> result = speed_msg(speed=45, limit=60)
    >>> print(result)
    Current speed is '45'. You may go faster as the limit is '60'.

.. code-block:: python

    >>> result = speed_msg(speed=66, limit=60, hours=4.7)
    >>> print(result)
    Please slow down limit is '60' and you are currenlty going '66'. Current driving hours is '4.7

Types dictate that if a type is not ``int`` or ``float`` then an error will be raised.

.. code-block:: python

    >>> result = speed_msg(speed=45, limit="Fast")
    TypeError: Arg 'limit' is expected to be of '<class 'int'> | <class 'float'>' but got 'str'
