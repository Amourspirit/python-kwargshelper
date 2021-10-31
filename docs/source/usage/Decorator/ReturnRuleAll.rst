ReturnRuleAll usage
===================

:py:class:`~.decorator.ReturnRuleAll` decorator that decorates methods that require return value to match all of the rules specificed.

Function Usage
--------------

In the following example return value must be an ``int`` or a negative ``float`` value.

.. code-block:: python

    from kwhelp.decorator import ReturnRuleAll
    from kwhelp import rules

    @ReturnRuleAll(rules.RuleIntPositive)
    def req_test(*arg):
        return sum(arg)



.. code-block:: python

    >>> result = req_test(2, 4)
    >>> print(result)
    6

Argument of ``float`` raised error.

.. code-block:: python

    >>> result = req_test(2, 2.4)
    kwhelp.exceptions.RuleError: RuleError: 'req_test' error. Argument: 'return' failed validation.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    Inner Error Message: TypeError: Argument Error: 'return' is expecting type of 'int'. Got type of 'float'

Negative return value raises error.

.. code-block:: python

    >>> result = req_test(2, -3)
    kwhelp.exceptions.RuleError: RuleError: 'req_test' error. Argument: 'return' failed validation.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    Inner Error Message: ValueError: Arg error: 'return' must be a positive int value


Class Usage
-----------

In the following example ``ReturnRuleAll`` is applied to a class method.
Note that ``ftype`` arg is set to ``DecFuncEnum.METHOD`` for class methods.

.. code-block:: python

    from kwhelp.decorator import ReturnRuleAll
    from kwhelp import rules

    class T:
        @ReturnRuleAll(rules.RuleIntPositive, ftype=DecFuncEnum.METHOD)
        def req_test(self, *arg):
            return sum(arg)


.. code-block:: python

    >>> t = T()
    >>> result = t.req_test(2, 4)
    >>> print(result)
    6

Argument of ``float`` raised error.

.. code-block:: python

    >>> t = T()
    >>> result = t.req_test(2, 2.5)
    kwhelp.exceptions.RuleError: RuleError: 'req_test' error. Argument: 'return' failed validation.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    Inner Error Message: TypeError: Argument Error: 'return' is expecting type of 'int'. Got type of 'float'

Negative return value raises error.

.. code-block:: python

    >>> t = T()
    >>> result = t.req_test(2, -3)
    kwhelp.exceptions.RuleError: RuleError: 'req_test' error. Argument: 'return' failed validation.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    Inner Error Message: ValueError: Arg error: 'return' must be a positive int value

Included Rules
--------------

.. include:: ../../inc/rules_list.rst