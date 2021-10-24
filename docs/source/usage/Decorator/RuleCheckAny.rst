RuleCheckAny
============

RuleCheckAny decorator reqires that each args of a function match one or more rules.

Decorating with ``*args``
-------------------------

This example requires that all args positive ``int`` or positive ``float``.

.. code-block:: python

    from kwhelp.decorator import RuleCheckAny
    import kwhelp.rules as rules

    @RuleCheckAny(rules=[rules.RuleIntPositive, rules.RuleFloatPositive])
    def add_positives(*args) -> float:
        result = 0.0
        for arg in args:
            result += float(arg)
        return result

Adding positive numbers works as expected.

.. code-block:: python

    >>> result = add_positives(1, 4, 6.9, 3.9, 7.3)
    >>> print(result)
    23.1

Because decorator rules dictate that only postiive numbers are allowed.
A negative number will raise an error.

.. code-block:: python

    >>> result = add_positives(2, 1.2, -1)
    kwhelp.error.RuleError: RuleError: Rule 'RuleIntPositive' Failed validation.
    Expected at least one of the following rules to match: RuleIntPositive, RuleFloatPositive.
    Inner Error Message: ValueError: Arg error: 'arg' must be a positive int value


Rules dictate that if a type is not ``int`` or ``float`` then an error will be raised.

.. code-block:: python

    >>> result = add_positives(2, 1.2, "4")
    kwhelp.error.RuleError: RuleError: Rule 'RuleIntPositive' Failed validation.
    Expected at least one of the following rules to match: RuleIntPositive, RuleFloatPositive.
    Inner Error Message: TypeError: Argument Error: 'arg' is expecting type of 'int'. Got type of 'str'


Decorating with Key, Value
--------------------------

This example requires that all args positive ``int`` or positive ``float``.

.. code-block:: python

    from kwhelp.decorator import RuleCheckAny
    import kwhelp.rules as rules

    @RuleCheckAny(rules=[rules.RuleIntPositive, rules.RuleFloatPositive])
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


Because decorator rules dictate that only postiive numbers are allowed.
A negative number will raise an error.

.. code-block:: python

    >>> result = speed_msg(speed=-2, limit=60)
    kwhelp.error.RuleError: RuleError: Argument: 'speed' failed validation. Rule 'RuleIntPositive' Failed validation.
    Expected at least one of the following rules to match: RuleIntPositive, RuleFloatPositive.
    Inner Error Message: ValueError: Arg error: 'speed' must be a positive int value



.. code-block:: python

    >>> result = speed_msg(speed=66, limit=60, hours=-0.2)
    kwhelp.error.RuleError: RuleError: Argument: 'hours' failed validation. Rule 'RuleIntPositive' Failed validation.
    Expected at least one of the following rules to match: RuleIntPositive, RuleFloatPositive.
    Inner Error Message: TypeError: Argument Error: 'hours' is expecting type of 'int'. Got type of 'float'


Rules dictate that if a type is not ``int`` or ``float`` then an error will be raised.

.. code-block:: python

    >>> result = speed_msg(speed=45, limit="Fast")
    kwhelp.error.RuleError: RuleError: Argument: 'limit' failed validation. Rule 'RuleIntPositive' Failed validation.
    Expected at least one of the following rules to match: RuleIntPositive, RuleFloatPositive.
    Inner Error Message: TypeError: Argument Error: 'limit' is expecting type of 'int'. Got type of 'str'

Included Rules
--------------

.. include:: ../../inc/rules_list.rst