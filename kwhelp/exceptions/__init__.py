# region Custom Errors
from inspect import isclass
from typing import Iterable, List, Type, Union
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
            err_rule (Type[IRule], optional): Rule that caused exception.
            rules_all (Iterable[Type[IRule]], optional): List of rules that were to all be matched.
                One of these rules is usually the reason this exception is being raised.
            rules_any (Iterable[Type[IRule]], optional): List of rules that required one or more matches.
                One of these rules is usually the reason this exception is being raised.
            arg_name (str, optional): Name of the argument for this exception.
            errors (Union[Exception, Iterable[Exception]], optional): Exception or Exceptions
                that cause this error.
            fn_name (str, optional): Name of function/property that raise error.
            msg (str, optional): Optional message to append.
        """
        self._fn_name = kwargs.get('fn_name', None)
        self._err_rule = kwargs.get('err_rule', None)
        _rules = kwargs.get('rules_all', False)
        self._rules_all = self._get_rules(_rules)
        _rules = kwargs.get('rules_any', False)
        self._rules_any = self._get_rules(_rules)
        _rules = None
        self._arg_name = kwargs.get('arg_name', None)
        self._errors = kwargs.get('errors', None)
        self._msg = kwargs.get('msg', None)
        msg = "RuleError:"
        if self._fn_name:
            msg = msg + f" '{self._fn_name}' error."
        if self._arg_name:
            msg = msg + f" Argument: '{self._arg_name}' failed validation."
        if self.err_rule and self._is_rule(self.err_rule):
            msg = msg + f"\nRule '{self.err_rule.__name__}' Failed validation."
        if len(self._rules_all) > 0:
            if len(self._rules_all) == 1:
                msg = msg + "\nExpected the following rule to match: "
            else:
                msg = msg + "\nExpected all of the following rules to match: "
            msg = msg + self._get_rules_str(self._rules_all) + "."
        if len(self._rules_any) > 0:
            if len(self._rules_any) == 1:
                msg = msg + "\nExpected the following rule to match: "
            else:
                msg = msg + "\nExpected at least one of the following rules to match: "
            msg = msg + self._get_rules_str(self._rules_any) + "."
        if self._msg:
            msg = msg + '\n' + str(self._msg)
        if self._is_errors() is True:
            msg = msg + "\nInner Error Message: " + self._get_inner_error_msg()
        self.message = msg
        super().__init__(self.message)

    # region private methods
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
        if self._errors:
            if is_iterable(self._errors):
                return isinstance(self._errors[0], Exception)
            return isinstance(self._errors, Exception)
        return False

    def _get_first_error(self):
        if is_iterable(self._errors):
            return self._errors[0]
        return self._errors
    
    def _get_inner_error_msg(self) -> str:
        err = self._get_first_error()
        msg = err.__class__.__name__ + ": "
        msg = msg + str(err)
        return msg
    # endregion private methods

    # region Properties
    @property
    def arg_name(self) -> Union[str, None]:
        """Gets Name of the argument for this exception"""
        return self._arg_name

    @property
    def msg(self) -> Union[str, None]:
        """Gets any messsage that is appended"""
        return self._msg

    @property
    def err_rule(self) -> Union[Type[IRule], None]:
        """Gets rule that caused exception."""
        return self._err_rule

    @property
    def errors(self) -> Union[Exception, Iterable[Exception], None]:
        """Gets Exception or Exceptions that cause this error"""
        return self._errors

    @property
    def rules_all(self) -> List[Type[IRule]]:
        """Gets list of rules that were to all be matched."""
        return self._rules_all

    @property
    def rules_any(self) -> List[Type[IRule]]:
        """Gets of rules that required one or more matches."""
        return self._rules_any
    
    @property
    def fn_name(self) -> Union[None, str]:
        """Gets the function/property name that raised the error"""
        return self._fn_name
    # endregion Properties
    # region Static Methods
    @staticmethod
    def from_rule_error(rule_error: 'RuleError', **kwargs) -> 'RuleError':
        """
        Creates a new RuleError from an existing RuleError
        
        Args:
            rule_error (RuleError): Current instance of RuleError use to base return value on.
        
        Keyword Arguments:
            kwargs: One or more Key, Value properties that will replace property of ``rule_error``.

        Returns:
            RuleError: New RuleError instance with updated properties included in ``**kwargs``.
        """
        rule_dict = {
            "err_rule": rule_error.err_rule,
            "rules_all": rule_error.rules_all,
            "rules_any": rule_error.rules_any,
            "arg_name": rule_error.arg_name,
            "errors": rule_error.errors,
            "fn_name": rule_error.fn_name,
            "msg": rule_error.msg
        }
        rule_dict.update({**kwargs})
        return RuleError(**rule_dict)
    # endregion Static Methods
# endregion Custom Errors
