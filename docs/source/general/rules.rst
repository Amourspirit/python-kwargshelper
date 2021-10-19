Rules
=====

Rules allow validation of ``kwargs`` values.

IRule
-----

New rules can be created by inheriting from :py:class:`~.rules.IRule` interface/class

**Example Rule:**

.. code-block:: python

    from kwhelp.rules import IRule
    class RuleIntRangeZeroNine(IRule):
        '''
        Rule to ensure a integer from 0 to 9.
        '''
        def validate(self) -> bool:
            if not isinstance(self.field_value, int):
                return False
            if self.field_value < 0 or self.field_value > 9:
                if self.raise_errors:
                    raise ValueError(
                        f"Arg error: '{self.key}' must be a num from 0 to 9")
                return False
            return True


Related
-------

  * :doc:`KwargsHelper Assign Rule Checking </source/usage/KwargsHelper/assign_rules>`
  * :doc:`KwArg Kw_assign Rule Checking </source/usage/KwArg/kw_assign_rules>`
  * :doc:`Simple Uasage Example <../example/simple_usage>`

Included Rules
--------------

.. include:: ../inc/rules_list.rst