# region Custom Errors
from inspect import isclass
from typing import Iterable, List, Optional
from ..helper import is_iterable
from ..rules import IRule

class CancelEventError(Exception):
    '''Cancel Event Error'''


class ReservedAttributeError(ValueError):
    '''Error when a reserved attribute is attempted to be set'''


class RuleError(Exception):
    '''Rule Error'''

    def __init__(self, err_rule: Optional[IRule] = None, rules_all: Optional[Iterable[IRule]] = None, rules_any: Optional[Iterable[IRule]] = None):
        self.err_rule = err_rule
        self.rules_all = self._get_rules(rules=rules_all)
        self.rules_any = self._get_rules(rules=rules_any)

        msg = "RuleError:"
        if err_rule and isclass(err_rule) and issubclass(err_rule, IRule):
            msg = msg + f" Rule '{err_rule.__name__}' Failed validation."
        if len(self.rules_all) > 0:
            if len(self.rules_all) == 1:
                msg = msg + " Expected the following rule to match: "
            else:
                msg = msg + "\nExpected all of the following rules to match: "
            msg = msg + self._get_rules_str(self.rules_all) + "."
        if len(self.rules_any) > 0:
            if len(self.rules_any) == 1:
                msg = msg + " Expected the following rule to match: "
            else:
                msg = msg + "\nExpected at least one of the following rules to match: "
            msg = msg + self._get_rules_str(self.rules_any) + "."
        self.message = msg
        super().__init__(self.message)

    def _is_rule(self, rule) -> bool:
        if isclass(rule) and issubclass(rule, IRule):
            return True
        return False

    def _get_rules(self, rules: Iterable[IRule]) -> List[IRule]:
        result = []
        if rules and is_iterable(rules):
            for rule in rules:
                if self._is_rule(rule):
                    result.append(rule)
        return result

    def _get_rules_str(self, rules: List[IRule]) -> str:
        msg = ""
        for i, rule in enumerate(rules):
            if i > 0:
                msg = msg + ', '
            msg = f"{msg}{rule.__name__}"
        return msg



# endregion Custom Errors
