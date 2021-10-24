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

    def __init__(self, **kwargs):
        """
        Constructor

        Keyword Arguments:
            err_rule (IRule, optional): Rule that caused exception.
            rules_all (Iterable[IRule], optional): List of rules that were to all be matched.
                One of these rules is usually the reason this exception is being raised.
            rules_any (Iterable[IRule], optional): List of rules that required on or matches.
                One of these rules is usually the reason this exception is being raised.
            arg_name (str, optional): The name of  the argument for this exception.
            errors: (Union[IRule, Iterable[IRule]], optional): Rule or Rules was being validated.
        """
        key = 'err_rule'
        if key in kwargs:
            self.err_rule = kwargs[key]
        else:
            self.err_rule = None
        key = 'rules_all'
        if key in kwargs:
            self.rules_all = self._get_rules(rules=kwargs[key])
        else:
            self.rules_all = []
        key = 'rules_any'
        if key in kwargs:
            self.rules_any = self._get_rules(rules=kwargs[key])
        else:
            self.rules_any = []
        key = 'arg_name'
        if key in kwargs:
            self.arg_name = kwargs[key]
        else:
            self.arg_name = None
        key = 'errors'
        if key in kwargs:
            self.errors = kwargs[key]
        else:
            self.errors = None

        msg = "RuleError:"
        if self.arg_name:
            msg = msg + f" Argument: '{self.arg_name}' failed validation."
        if self.err_rule and isclass(self.err_rule) and issubclass(self.err_rule, IRule):
            msg = msg + f" Rule '{self.err_rule.__name__}' Failed validation."
        if len(self.rules_all) > 0:
            if len(self.rules_all) == 1:
                msg = msg + "\nExpected the following rule to match: "
            else:
                msg = msg + "\nExpected all of the following rules to match: "
            msg = msg + self._get_rules_str(self.rules_all) + "."
        if len(self.rules_any) > 0:
            if len(self.rules_any) == 1:
                msg = msg + " Expected the following rule to match: "
            else:
                msg = msg + "\nExpected at least one of the following rules to match: "
            msg = msg + self._get_rules_str(self.rules_any) + "."
        if self._is_errors() is True:
            msg = msg + "\nInner Error Message: " + self._get_inner_error_msg()
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

    def _is_errors(self) -> bool:
        if self.errors:
            if is_iterable(self.errors):
                if len(self.errors) == 0:
                    return False
                return isinstance(self.errors[0], Exception)
            return isinstance(self.errors, Exception)
        return False

    def _get_first_error(self):
        if is_iterable(self.errors):
            return self.errors[0]
        return self.errors
    
    def _get_inner_error_msg(self) -> str:
        err = self._get_first_error()
        msg = err.__class__.__name__ + ": "
        msg = msg + str(err)
        return msg


# endregion Custom Errors
