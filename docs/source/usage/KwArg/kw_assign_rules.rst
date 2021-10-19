Kw_assign Rule Checking
=======================

Rule checking can be done by adding ``rules_all`` or ``rules_any`` to :py:meth:`~.KwArg.kw_assign` method.
Rule checking ensures a value of ``**kwargs`` values match rules before assigning to
current instance of class.

All rules
---------

In the following example args ``first`` and ``second`` must be a positive ``int`` with a maximum value of 100.
Arg ``rules_all`` of :py:meth:`~.KwArg.kw_assign` method validates as ``True`` only if all :py:class:`~.IRule` match.
Trying to assign any other type or value to ``first`` or ``second`` results in an error.

Custom Rule for a maximum ``int`` value of 100

.. include:: /source/inc/ex/RuleIntMax100.rst

.. code-block:: python

    from kwhelp import KwArg
    import kwhelp.rules as rules

    def my_method(**kwargs) -> str:
        kw = KwArg(**kwargs)
        kw.kw_assign(key='first', require=True, rules_all=[
                rules.RuleIntPositive,
                RuleIntMax100
            ])
        kw.kw_assign(key='second', require=True, rules_all=[
                rules.RuleIntPositive,
                RuleIntMax100
            ])
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

Assign positive ``int``.

.. code-block:: python

    >>> result = my_method(first = 10, second = 22)
    >>> print(result)
    Result: 32

Assign positive ``int`` and ``int`` greater than 100.

.. code-block:: python

    >>> result = my_method(first = 10, second = 122)
    ValueError: Arg error: 'second' must be equal or less than 100

Assign negative ``int``.

.. code-block:: python

    >>> result = my_method(first = -10, second = -22)
    ValueError: Arg error: 'first' must be a positive int value

Assigning ``float`` result is a ``TypeError``

.. code-block:: python

    >>> result = my_method(first = 10, second = 22.33)
    TypeError: Argument Error: 'second' is expecting type of 'int'. Got type of 'float'

Assigning negative ``int`` results in a ``ValueError``.

.. code-block:: python

    >>> result = my_method(first = 10, second = -5)
    ValueError: Arg error: 'second' must be a positive int value

Any rule
--------

In the following example args ``first`` and ``second`` can be a negative or zero ``float`` or ``int`` zero.
Arg ``rules_any`` of :py:meth:`~.KwArg.kw_assign` method validates as ``True`` if any :py:class:`~.IRule` matches.
Trying to assign any other type to ``first`` or ``second`` results in an error.

.. code-block:: python

    from kwhelp import KwArg
    import kwhelp.rules as rules

    def my_method(**kwargs) -> str:
        kw = KwArg(**kwargs)
        kw.kw_assign(key='first', require=True, rules_any=[
                rules.RuleFloatNegativeOrZero,
                rules.RuleIntZero
            ])
        kw.kw_assign(key='second', require=True, rules_any=[
                rules.RuleFloatNegativeOrZero,
                rules.RuleIntZero
            ])
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

Assign ``int`` zero and ``float`` negative.

.. code-block:: python

    >>> result = my_method(first = 0, second = -22.5)
    >>> print(result)
    Result: -22.5

Assign ``float`` zero and ``float`` negative.

.. code-block:: python

    >>> result = my_method(first = 0.0, second = -22.5)
    >>> print(result)
    Result: -22.5

Assign ``int`` zero and ``float`` zero.

.. code-block:: python

    >>> result = my_method(first = 0, second = 0.0)
    >>> print(result)
    Result: 0.0

Assign ``float`` negative and ``float`` negative.

.. code-block:: python

    >>> result = my_method(first = -10.8, second = -8.68)
    >>> print(result)
    Result: -19.48

Assign ``int`` and ``float`` zero.

.. code-block:: python

    >>> result = my_method(first = 12, second = 0.0)
    TypeError: Argument Error: 'first' is expecting type of 'float'. Got type of 'int'

Assign ``float`` positive and ``int``.

.. code-block:: python

    >>> result = my_method(first = 12.46, second = 0)
    ValueError: Arg error: 'first' must be equal to 0.0 or a negative float value

Assign ``float`` negative and ``float`` positive.

.. code-block:: python

    >>> result = my_method(first = -12.46, second = 1.2)
    ValueError: Arg error: 'second' must be equal to 0.0 or a negative float value

Assigning a ``str`` results in an error.

.. code-block:: python

    >>> result = my_method(first=-10.5, second="0")
    TypeError: Argument Error: 'second' is expecting type of 'float'. Got type of 'str'

Included Rules
--------------

.. include:: ../../inc/rules_list.rst