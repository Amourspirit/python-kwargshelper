ReturnRuleAny Usage
===================

:py:class:`~.decorator.ReturnRuleAny` decorator that decorates methods that require return value to match at least one of the rules specificed.

Includes features:

    * :doc:`/source/general/dec_feature/ftype`
    * :doc:`/source/general/dec_feature/opt_logger`
    * :doc:`/source/general/dec_feature/opt_return`

Function Usage
--------------

In the following example return value must be an ``int`` or a negative ``float`` value.

.. code-block:: python

    from kwhelp.decorator import ReturnRuleAny
    from kwhelp import rules

    @ReturnRuleAny(rules.RuleInt, rules.RuleFloatNegative)
    def req_test(*arg):
        return sum(arg)

Postiive return ``int`` value is valid

.. code-block:: python

    >>> result = req_test(2, 4)
    >>> print(result)
    6

Negative return ``float`` value is valid

.. code-block:: python

    >>> result = req_test(2, -5.2)
    >>> print(result)
    -3.2

Positive return ``float`` value raised error.

.. code-block:: python

    >>> result = req_test(2, 2.4)
    kwhelp.exceptions.RuleError: RuleError: 'req_test' error. Argument: 'return' failed validation.
    Rule 'RuleInt' Failed validation.
    Expected at least one of the following rules to match: RuleInt, RuleFloatNegative.
    Inner Error Message: TypeError: Argument Error: 'return' is expecting type of 'int'. Got type of 'float'

Class Usage
-----------

In the following example ``ReturnRuleAny`` is applied to a class method.
Note that ``ftype`` arg is set to ``DecFuncEnum.METHOD`` for class methods.

.. code-block:: python

    from kwhelp.decorator import ReturnRuleAny
    from kwhelp import rules

    class T:
        @ReturnRuleAny(rules.RuleInt, rules.RuleFloatNegative, ftype=DecFuncEnum.METHOD)
        def req_test(self, *arg):
            return sum(arg)


.. code-block:: python

    >>> t = T()
    >>> result = t.req_test(2, 4)
    >>> print(result)
    6

Returning a postitive float result in an error.

.. code-block:: python

    >>> t = T()
    >>> result = t.req_test(2, 2.5)
    kwhelp.exceptions.RuleError: RuleError: 'req_test' error. Argument: 'return' failed validation.
    Rule 'RuleInt' Failed validation.
    Expected at least one of the following rules to match: RuleInt, RuleFloatNegative.
    Inner Error Message: TypeError: Argument Error: 'return' is expecting type of 'int'. Got type of 'float'

Included Rules
--------------

.. include:: ../../inc/rules_list.rst