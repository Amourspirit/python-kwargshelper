Rules
=====

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


Included Rules
--------------

.. exec::

    import glob
    import os
    r_path = os.path.join(os.path.abspath('.'), "source/kwhelp/rules")
    rules_pattern = r_path + os.sep + "Rule*.rst"
    rule_list = glob.glob(rules_pattern)
    rule_list.sort()
    i_trim = len(r_path) + 1
    print("\n")
    for rule in rule_list:
        name = str(rule)[i_trim:-4]
        print("* :py:class:`~.rules.{}`".format(name))
        print("\n")