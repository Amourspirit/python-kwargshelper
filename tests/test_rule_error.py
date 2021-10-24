import unittest
import re
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp import rules
from kwhelp.error import RuleError


class TestRuleError(unittest.TestCase):

    def raise_err(self, err_rule = None, rules_all = None, rules_any= None):
        raise RuleError(err_rule=err_rule,rules_all=rules_all, rules_any=rules_any)

    def test_no_args(self):
        with self.assertRaisesRegex(RuleError, "RuleError:"):
            self.raise_err()

    def test_rule(self):
        with self.assertRaisesRegex(RuleError, "RuleError:\s.*'RuleInt'"):
            self.raise_err(err_rule=rules.RuleInt)
    
    def test_rules_all(self):
        rx = re.compile(r"^RuleError:\s.*RuleInt", re.MULTILINE)
        with self.assertRaisesRegex(RuleError, rx):
            self.raise_err(rules_all=[rules.RuleInt])

    def test_rules_all_multi(self):
        rx = re.compile(
            r"^RuleError:\s.*all of.*match: RuleInt \| RuleFloat", re.MULTILINE)
        with self.assertRaisesRegex(RuleError, rx):
            self.raise_err(rules_all=[rules.RuleInt, rules.RuleFloat])

    def test_rules_any(self):
        rx = re.compile(r"^RuleError:\s.*RuleInt", re.MULTILINE)
        with self.assertRaisesRegex(RuleError, rx):
            self.raise_err(rules_any=[rules.RuleInt])
    
    def test_rules_any_multi(self):
        rx = re.compile(
            r"^RuleError:\s.*one of.*match: RuleInt \| RuleFloat", re.MULTILINE)
        with self.assertRaisesRegex(RuleError, rx):
            self.raise_err(rules_any=[rules.RuleInt, rules.RuleFloat])

if __name__ == '__main__':
    unittest.main()
