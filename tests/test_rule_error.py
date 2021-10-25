import unittest
import re
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp import rules
from kwhelp.exceptions import RuleError


class TestRuleError(unittest.TestCase):

    def raise_err(self, err_rule = None, rules_all = None, rules_any= None):
        raise RuleError(err_rule=err_rule,rules_all=rules_all, rules_any=rules_any)

    def test_no_args(self):
        with self.assertRaisesRegex(RuleError, "RuleError:"):
            self.raise_err()

    def test_rule(self):
        with self.assertRaisesRegex(RuleError, "RuleError:\s.*'RuleInt'"):
            self.raise_err(err_rule=rules.RuleInt)

    def test_rules_all_single(self):
        rx = re.compile(
            r"^RuleError:(?:\n|\s)Expected the following rule to match: RuleFloat.", re.MULTILINE)
        with self.assertRaisesRegex(RuleError, rx):
            self.raise_err(rules_all=[rules.RuleFloat])

    
    def test_rules_all(self):
        rx = re.compile(r"^RuleError:(?:\n|\s).*RuleInt", re.MULTILINE)
        with self.assertRaisesRegex(RuleError, rx):
            self.raise_err(rules_all=[rules.RuleInt])

    def test_rules_all_multi(self):
        rx = re.compile(
            r"^RuleError:(?:\n|\s).*all of.*match: RuleInt, RuleFloat", re.MULTILINE)
        with self.assertRaisesRegex(RuleError, rx):
            self.raise_err(rules_all=[rules.RuleInt, rules.RuleFloat])

    def test_rules_any(self):
        rx = re.compile(r"^RuleError:(?:\n|\s).*RuleInt", re.MULTILINE)
        with self.assertRaisesRegex(RuleError, rx):
            self.raise_err(rules_any=[rules.RuleInt])
    
    def test_rules_any_multi(self):
        rx = re.compile(
            r"^RuleError:(?:\n|\s).*one of.*match: RuleInt, RuleFloat", re.MULTILINE)
        with self.assertRaisesRegex(RuleError, rx):
            self.raise_err(rules_any=[rules.RuleInt, rules.RuleFloat])

    def test_rules_any_single(self):
        rx = re.compile(
            r"^RuleError:(?:\n|\s)Expected the following rule to match: RuleFloat.", re.MULTILINE)
        with self.assertRaisesRegex(RuleError, rx):
            self.raise_err(rules_any=[rules.RuleFloat])
    
    def test_any_all(self):
        err = RuleError(rules_any=[rules.RuleFloat, self], rules_all=[rules.RuleInt, self])
        self.assertTrue(len(err.rules_all), 1)
        self.assertTrue(len(err.rules_any), 1)
        self.assertIs(err.rules_any[0], rules.RuleFloat)
        self.assertIs(err.rules_all[0], rules.RuleInt)

    def test_errors(self):
        err = RuleError(errors=[])
        self.assertListEqual(err.errors, [])

    def test_arg_name(self):
        err = RuleError(arg_name="test")
        self.assertEqual(err.arg_name, "test")
    
        err = RuleError()
        self.assertIsNone(err.arg_name)

if __name__ == '__main__':
    unittest.main()
