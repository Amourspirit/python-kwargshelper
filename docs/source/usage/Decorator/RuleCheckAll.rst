RuleCheckAll Usage
==================

:py:class:`~.decorator.RuleCheckAll` decorator reqires that each args of a function match all rules specified.

Includes features:

    * :doc:`/source/general/dec_feature/ftype`
    * :doc:`/source/general/dec_feature/opt_args_filter`
    * :doc:`/source/general/dec_feature/opt_logger`
    * :doc:`/source/general/dec_feature/opt_return`
    * :doc:`/source/general/dec_feature/raise_error`

Decorating with ``*args``
-------------------------

This example requires that all args positive ``int`` 

.. code-block:: python

    from kwhelp.decorator import RuleCheckAll
    import kwhelp.rules as rules

    @RuleCheckAll(rules.RuleIntPositive)
    def add_positives(*args) -> float:
        result = 0
        for arg in args:
            result += arg
        return result

Adding positive numbers works as expected.

.. code-block:: python

    >>> result = add_positives(1, 4, 6, 3, 10)
    >>> print(result)
    24

Because decorator rules dictate that only postiive numbers are allowed.
A negative number will raise an error.

.. code-block:: python

    >>> result = add_positives(2, 1, -1)
    kwhelp.exceptions.RuleError: RuleError: 'add_positives' error.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    RuleCheckAll decorator error.
    Inner Error Message: ValueError: Arg error: 'arg' must be a positive int value

Rules dictate that if a type is not ``int`` then an error will be raised.

.. code-block:: python

    >>> result = add_positives(2, 1, 3.55)
    kwhelp.exceptions.RuleError: RuleError: 'add_positives' error.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    RuleCheckAll decorator error.
    Inner Error Message: TypeError: Argument Error: 'arg' is expecting type of 'int'. Got type of 'float'

Decorating with Key, Value
--------------------------

This example requires that all args positive ``int``.

.. code-block:: python

    from kwhelp.decorator import RuleCheckAll
    import kwhelp.rules as rules

    @RuleCheckAll(rules.RuleIntPositive)
    def speed_msg(speed, limit, **kwargs) -> str:
        if limit > speed:
            msg = f"Current speed is '{speed}'. You may go faster as the limit is '{limit}'."
        elif speed == limit:
            msg = f"Current speed is '{speed}'. You are at the limit."
        else:
            msg = f"Please slow down limit is '{limit}' and you are currenlty going '{speed}'."
        if 'hours' in kwargs:
            msg = msg + f" Current driving hours is '{kwargs['hours']}'."
        return msg

Adding positive numbers works as expected.

.. code-block:: python

    >>> result = speed_msg(speed=45, limit=60)
    >>> print(result)
    Current speed is '45'. You may go faster as the limit is '60'.

.. code-block:: python

    >>> result = speed_msg(speed=66, limit=60, hours=3)
    >>> print(result)
    Please slow down limit is '60' and you are currenlty going '66'. Current driving hours is '3'.

Because decorator rules dictate that only postiive numbers are allowed.
A negative number will raise an error.

.. code-block:: python

    >>> result = speed_msg(speed=-2, limit=60)
    kwhelp.exceptions.RuleError: RuleError: 'speed_msg' error. Argument: 'speed' failed validation.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    RuleCheckAll decorator error.
    Inner Error Message: ValueError: Arg error: 'speed' must be a positive int value


.. code-block:: python

    >>> result = speed_msg(speed=66, limit=60, hours=-2)
    kwhelp.exceptions.RuleError: RuleError: 'speed_msg' error. Argument: 'hours' failed validation.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    RuleCheckAll decorator error.
    Inner Error Message: ValueError: Arg error: 'hours' must be a positive int value

Rules dictate that if a type is not ``int`` then an error will be raised.

.. code-block:: python

    >>> result = speed_msg(speed=45, limit="Fast")
    kwhelp.exceptions.RuleError: RuleError: 'speed_msg' error. Argument: 'limit' failed validation.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    RuleCheckAll decorator error.
    Inner Error Message: TypeError: Argument Error: 'limit' is expecting type of 'int'. Got type of 'str'

Opton opt_args_filter
---------------------

The arguments are validated by :py:class:`~.decorator.RuleCheckAll` can be filtered by setting ``opt_args_filter`` option. 

For more examples see :doc:`/source/general/dec_feature/opt_args_filter`.

In the following example all ``*args`` must be positive ``int``.
``opt_args_filter=DecArgEnum.ARGS`` filters ``RuleCheckAll`` to only process ``*args``.

.. code-block:: python

    from kwhelp.decorator import RuleCheckAll, DecArgEnum
    from kwhelp import rules

    @RuleCheckAll(rules.RuleIntPositive, opt_args_filter=DecArgEnum.ARGS)
    def foo(*args, first, last="!", **kwargs):
        return [*args] + [first, last] + [v for _, v in kwargs.items()]

.. code-block:: python

    >>> result = foo(101, 223, 778, 887, first="1st", one='one', two="2nd")
    >>> print(result)
    [101, 223, 778, 887, '1st', '!', 'one', '2nd']
    >>> result = foo(101, 223, -778, 887, first="1st", one='one', two="2nd")
    kwhelp.exceptions.RuleError: RuleError: 'foo' error.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    RuleCheckAll decorator error.
    Inner Error Message: ValueError: Arg error: 'arg' must be a positive int value


Included Rules
--------------

.. include:: ../../inc/rules_list.rst
