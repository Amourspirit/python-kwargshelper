raise_error
===========

Some decorators supports *optoinal* ``raise_error`` bool option.
``raise_error`` sets if a an error will be validation fails.

If ``raise_error`` is set to ``False`` then a attribute will be
added to the decorated funciton.

.. code-block:: python

    from kwhelp.decorator import RuleCheckAll
    from kwhelp import rules

    @RuleCheckAll(rules.RuleIntPositive, raise_error=False)
    def add_positives(*args) -> float:
        result = 0
        for arg in args:
            result += arg
        return result

.. code-block:: python

    >>> print(add_positives.is_rules_all_valid)
    True
    >>> result = add_positives(2, -4)
    >>> print(add_positives.is_rules_all_valid)
    False
    >>> result = add_positives(2, 4)
    >>> print(add_positives.is_rules_all_valid)
    True
    >>> print(result)
    6