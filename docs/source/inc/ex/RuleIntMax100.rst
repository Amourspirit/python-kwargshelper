.. code-block:: python

    import kwhelp.rules as rules

    class RuleIntMax100(rules.IRule):
        def validate(self) -> bool:
            if self.field_value > 100:
                if self.raise_errors:
                    raise ValueError(
                        f"Arg error: '{self.key}' must be equal or less than 100")
                return False
            return True
