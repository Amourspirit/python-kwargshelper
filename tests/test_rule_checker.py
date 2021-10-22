import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.checks import RuleChecker
from kwhelp.decorator import RuleCheckAny, RuleCheckAll, RuleCheckAllKw, RuleCheckAnyKw, TypeCheckerKw
from kwhelp import rules


class TestRuleChecker(unittest.TestCase):

    def test_main(self):
        rc = RuleChecker(rules_all=[rules.RuleInt], rules_any=[
                         rules.RuleIntPositive, rules.RuleFloatPositive])
        assert rc.validate_all(one=2, two=2) == True
        with self.assertRaises(TypeError):
            rc.validate_all(one=2, two="2")

        assert rc.validate_all(1, 3, 4, 5, 7) == True
        assert rc.validate_all(first=1, second=3, third=4,
                               fourth=5, fifth=7) == True
        assert rc.validate_all(0, 1, 8, 9, first=1, second=3, third=4,
                               fourth=5, fifth=7) == True
        assert rc.validate_any(1, 3, 4.6, 5, 5.8) == True
        with self.assertRaises(TypeError):
            rc.validate_all(4.6, 5, 5.8)
        with self.assertRaises(TypeError):
            rc.validate_any(1, 2, "4", 5)
        with self.assertRaises(TypeError):
            rc.validate_any(start=1, end="2")


class TestRuleDecorators(unittest.TestCase):

    def test_rule_check_any_dec(self):

        @RuleCheckAny(rules=[rules.RuleIntPositive, rules.RuleFloatPositive])
        def rule_test(one, two) -> float:
            return float(one) + float(two)

        result = rule_test(10, 12.3)
        assert rule_test.is_rules_any_valid == True
        assert result == 22.3

        with self.assertRaises(TypeError):
            result = rule_test(3, "")
        with self.assertRaises(TypeError):
            result = rule_test(3, -2.3)

    def test_rule_str(self):
        @RuleCheckAll(rules=[rules.RuleStrNotNullEmptyWs])
        def rule_test(start, middle, end) -> str:
            return f"{start} {middle} {end}"

        result = rule_test("1", "2", ".")
        assert result == "1 2 ."
        result = rule_test(start="1", middle="2", end=".")
        assert result == "1 2 ."
        with self.assertRaises(TypeError):
            rule_test("1", "2", 1)
        with self.assertRaises(TypeError):
            rule_test(start="1", middle=2, end=".")

    def test_rules_any_kw(self):
        @RuleCheckAllKw(arg_index={"start": 0, "middle": 0, "end": 1},
                        rules=[(rules.RuleStrNotNullEmptyWs,), (rules.RuleIntZero,)])
        def rule_test(start, middle, end) -> str:
            return f"{start} {middle} {end}"
        result = rule_test("1", "2", 0)
        assert result == "1 2 0"

        with self.assertRaises(ValueError):
            rule_test("1", "2", 1)
        with self.assertRaises(TypeError):
            rule_test("1", "2", "0")
        with self.assertRaises(TypeError):
            rule_test(None, "2", 0)
        with self.assertRaises(TypeError):
            rule_test(22, "2", 0)
        with self.assertRaises(TypeError):
            rule_test("1", 2, 1)

    def test_rules_all_kw(self):
        @RuleCheckAnyKw(arg_index={"start": 0, "middle": 1, "end": 2},
                        rules=[(rules.RuleInt,), (rules.RuleIntPositive, rules.RuleFloatPositive),
                               (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
        def rule_test(start, middle, end) -> tuple:
            return (start, middle, end)
        result = rule_test(-1, 2, 0)
        assert result == (-1, 2, 0)
        
        result = rule_test(99, 2.6, 0)
        assert result == (99, 2.6, 0)
        with self.assertRaises(ValueError):
            rule_test(-1, -2, 0)
        with self.assertRaises(TypeError):
            rule_test("-1", -2, 0)

    def test_rules_any_all_kw(self):
        @RuleCheckAllKw(arg_index={"start": 0},
                        rules=[(rules.RuleStrNotNullEmptyWs,)])
        @RuleCheckAnyKw(arg_index={"middle": 0, "end": 1},
                        rules=[(rules.RuleIntPositive, rules.RuleFloatPositive),
                               (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
        def rule_test(start, middle, end) -> tuple:
            return (start, middle, end)
        result = rule_test(start="hello", middle=22, end=-3.4)
        assert result == ("hello", 22, -3.4)
        with self.assertRaises(ValueError):
            rule_test(start=" ", middle=22, end=-3.4)
        with self.assertRaises(TypeError):
            rule_test(start="hello", middle="m", end=-3.4)

    def test_rules_any_all_type_kw(self):
        @TypeCheckerKw(arg_index={"start": 0, "middle": 1, "end": 1},
                       types=[(str,),(int, float)])
        @RuleCheckAllKw(arg_index={"start": 0},
                        rules=[(rules.RuleStrNotNullEmptyWs,)])
        @RuleCheckAnyKw(arg_index={"middle": 0, "end": 1},
                        rules=[(rules.RuleIntPositive, rules.RuleFloatPositive),
                               (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
        def rule_test(start, middle, end) -> tuple:
            return (start, middle, end)
        result = rule_test(start="hello", middle=22, end=-3.4)
        assert result == ("hello", 22, -3.4)

if __name__ == '__main__':
    unittest.main()
