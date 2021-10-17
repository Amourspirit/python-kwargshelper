Kw_assign Rule Checking
=======================

Rule checking can be done by adding ``rules_all`` or ``rules_any`` to :py:meth:`~.KwArg.kw_assign` method.
Rule checking ensures a value of ``**kwargs`` values match rules before assigning to
current instance of class.

Any rule
--------

In the following example args ``first`` and ``second`` can be a positive ``float`` or a positive ``int``.
Arg ``rules_any`` of :py:meth:`~.KwArg.kw_assign` method validates as ``True`` if any :py:class:`~.IRule` matches.
Trying to assign any other type to ``first`` or ``second`` results in an error.

.. code-block:: python

    from kwhelp import KwArg
    import kwhelp.rules as rules

    def my_method(**kwargs) -> str:
        kw = KwArg(**kwargs)
        kw.kw_assign(key='first', require=True, rules_any=[
                rules.RuleIntPositive,
                rules.RuleFloatNegative
            ])
        kw.kw_assign(key='second', require=True, rules_any=[
                rules.RuleIntPositive,
                rules.RuleFloatNegative
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

Assign ``int``.

.. code-block:: python

    >>> result = my_method(first = 10, second = 22)
    >>> print(result)
    Result: 32

Assign ``int`` and ``float``.

.. code-block:: python

    >>> result = my_method(first = 10, second = -8.68)
    >>> print(result)
    Result: 1.3200000000000003

Assign ``float`` positive and ``int``.

.. code-block:: python

    >>> result = my_method(first = 12.46, second = 10)
    TypeError: Argument Error: 'first' is expecting type of 'int'. Got type of 'float'

Assigning a ``str`` results in an error.

.. code-block:: python

    >>> result = my_method(first=10, second="0")
    TypeError: Argument Error: 'second' is expecting type of 'int'. Got type of 'str'

All rules
---------

In the following example args ``first`` and ``second`` must be a positive ``int``.
Arg ``rules_all`` of :py:meth:`~.KwArg.kw_assign` method validates as ``True`` only if all :py:class:`~.IRule` match.
Trying to assign any other type or value to ``first`` or ``second`` results in an error.

.. code-block:: python

    from kwhelp import KwArg
    import kwhelp.rules as rules

    def my_method(**kwargs) -> str:
        kw = KwArg(**kwargs)
        kw.kw_assign(key='first', require=True, rules_all=[
                rules.RuleIntPositive,
                rules.RuleFloatNegative
            ])
        kw.kw_assign(key='second', require=True, rules_all=[
                rules.RuleIntPositive,
                rules.RuleFloatNegative
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

    >>> result = my_method(first=10, second=22)
    >>> print(result)
    Result: 32

Assigning ``float`` result is a ``TypeError``

.. code-block:: python

    >>> result = my_method(first=10, second=22.33)
    TypeError: Argument Error: 'second' is expecting type of 'int'. Got type of 'float'

Assigning negative ``int`` results in a ``ValueError``.

.. code-block:: python

    >>> result = my_method(first=10, second=-5)
    ValueError: Arg error: 'second' must be a positive int value

Included Rules
--------------

.. include:: ../../inc/rules_list.rst