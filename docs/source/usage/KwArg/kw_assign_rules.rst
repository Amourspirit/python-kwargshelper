Kw_assign Rule Checking
=======================

Rule checking can be done by adding ``rules`` to :py:meth:`~.KwArg.kw_assign` method.
Rule checking ensures a value of ``**kwargs`` values match rules before assigning to
current instance of class.

Any rule
--------

In the following example args ``first`` and ``second`` can be a positive ``float`` or a positive ``int``.
Trying to assign any other type to ``first`` or ``second`` results in an error.
By defalult arg ``all_rules`` of :py:meth:`~.KwArg.kw_assign` method is ``False``. This results in
a postivie validation if any rule matches that are passed in via the ``rules`` arg.

.. code-block:: python

    from kwhelp import KwArg
    import kwhelp.rules as rules

    def my_method(**kwargs) -> str:
        kw = KwArg(**kwargs)
        kw.kw_assign(key='first', require=True, rules=[
                rules.RuleIntPositive,
                rules.RuleFloatPositive
            ])
        kw.kw_assign(key='second', require=True, rules=[
                rules.RuleIntPositive,
                rules.RuleFloatPositive
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

Assign ``int`` and ``float``.

.. code-block:: python

    >>> result = my_method(first=10, second=22.33)
    >>> print(result)
    Result: 32.33

Assigning a ``str`` results in an error.

.. code-block:: python

    >>> result = my_method(first=10, second="0")
    TypeError: Argument Error: 'second' is expecting type of 'int'. Got type of 'str'

All rules
---------

In the following example args ``first`` and ``second`` must be a positive ``int``.
Trying to assign any other type or value to ``first`` or ``second`` results in an error.
By setting ``all_rules`` of :py:meth:`~.KwArg.kw_assign` method to ``True`` forces all rules
to pass validation. This results in
a postivie validation only if all rules match that are passed in via ``rules`` arg.

.. code-block:: python

    from kwhelp import KwArg
    import kwhelp.rules as rules

    def my_method(**kwargs) -> str:
        kw = KwArg(**kwargs)
        kw.kw_assign(key='first', require=True, rules=[
                rules.RuleInt,
                rules.RuleIntPositive
            ],
            all_rules=True)
        kw.kw_assign(key='second', require=True, rules=[
                rules.RuleInt,
                rules.RuleIntPositive
            ],
            all_rules=True)
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