import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.checks import RuleChecker
from kwhelp.decorator import RuleCheckAny, RuleCheckAll, RuleCheckAllKw, RuleCheckAnyKw, TypeCheckKw
from kwhelp import rules
from kwhelp.exceptions import RuleError


class TestRuleChecker(unittest.TestCase):

    def test_main(self):
        rc = RuleChecker(rules_all=[rules.RuleInt], rules_any=[
                         rules.RuleIntPositive, rules.RuleFloatPositive])
        rc.raise_error = True
        assert rc.raise_error == True
        assert len(rc.rules_all) == 1
        assert len(rc.rules_any) == 2
        assert rc.validate_all(one=2, two=2) == True
        with self.assertRaises(RuleError):
            rc.validate_all(one=2, two="2")

        assert rc.validate_all(1, 3, 4, 5, 7) == True
        assert rc.validate_all(first=1, second=3, third=4,
                               fourth=5, fifth=7) == True
        assert rc.validate_all(0, 1, 8, 9, first=1, second=3, third=4,
                               fourth=5, fifth=7) == True
        assert rc.validate_any(1, 3, 4.6, 5, 5.8) == True
        with self.assertRaises(RuleError):
            rc.validate_all(4.6, 5, 5.8)
        with self.assertRaises(RuleError):
            rc.validate_any(1, 2, "4", 5)
        with self.assertRaises(RuleError):
            rc.validate_any(start=1, end="2")

    def test_rules_all_err(self):
        with self.assertRaises(TypeError):
            rc = RuleChecker(rules_all=rules.RuleInt, rules_any=[
                    rules.RuleIntPositive, rules.RuleFloatPositive])

    def test_rules_any_err(self):
        with self.assertRaises(TypeError):
            rc = RuleChecker(rules_all=[rules.RuleInt], rules_any=rules.RuleFloatPositive)

    def test_no_err(self):
        rc = RuleChecker(rules_all=[rules.RuleInt], rules_any=[
                         rules.RuleIntPositive, rules.RuleFloatPositive], raise_error=False)
        assert rc.validate_any(1, 3, 4.6, 5, 5.8) == True
        assert rc.validate_any(one=1, two=3, three=4.6, four=5, five=5.8) == True
        assert rc.validate_all(4.6, 5, 5.8) == False
        assert rc.validate_all(one=4.6, two=5, three=5.8) == False
        assert rc.validate_any(1, "2") == False
        assert rc.validate_any(start=1, end="2") == False
    
    def test_all_empty(self):
        rc = RuleChecker(rules_all=[])
        assert rc.validate_all(1, "a", self, int, 5.8) == True
    
    def test_any_empty(self):
        rc = RuleChecker(rules_any=[])
        assert rc.validate_any(1, "a", self, int, 5.8) == True

    def test_non_irule_any(self):
        rc = RuleChecker(rules_any=[
                         int, rules.RuleInt])
        with self.assertRaises(TypeError):
            rc.validate_any(1)


    def test_non_irule_all(self):
        rc = RuleChecker(rules_all=[
            int, rules.RuleInt])
        with self.assertRaises(TypeError):
            rc.validate_all(1)

class TestRuleDecorators(unittest.TestCase):

    def test_rule_check_any_dec(self):

        @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive)
        def rule_test(one, two) -> float:
            return float(one) + float(two)

        result = rule_test(10, 12.3)
        assert result == 22.3

        with self.assertRaises(RuleError):
            result = rule_test(3, "")
        with self.assertRaises(RuleError):
            result = rule_test(3, -2.3)

    def test_rule_check_any_dec_kwargs_err(self):
        @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive, raise_error=True)
        def rule_test(one, two) -> float:
            return float(one) + float(two)

        result = rule_test(10, 12.3)
        assert result == 22.3
        
    def test_rule_check_any_dec_kwargs(self):
        @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive, raise_error=False)
        def rule_test(one, two) -> float:
            return float(one) + float(two)

        result = rule_test(10, 12.3)
        assert result == 22.3
        assert rule_test.is_rules_any_valid == True
        
        result = rule_test(10, -12.3)
        assert rule_test.is_rules_any_valid == False

    def test_rule_str(self):
        @RuleCheckAll(rules.RuleStrNotNullEmptyWs)
        def rule_test(start, middle, end) -> str:
            return f"{start} {middle} {end}"

        result = rule_test("1", "2", ".")
        assert result == "1 2 ."
        result = rule_test(start="1", middle="2", end=".")
        assert result == "1 2 ."
        with self.assertRaises(RuleError):
            rule_test("1", "2", 1)
        with self.assertRaises(RuleError):
            rule_test(start="1", middle=2, end=".")

    def test_rule_str_no_err(self):
        @RuleCheckAll(rules.RuleStrNotNullEmptyWs, raise_error=False)
        def rule_test(start, middle, end) -> str:
            return f"{start} {middle} {end}"

        result = rule_test("1", "2", ".")
        assert result == "1 2 ."
        assert rule_test.is_rules_all_valid == True
        result = rule_test(start="1", middle="2", end=".")
        assert result == "1 2 ."
        assert rule_test.is_rules_all_valid == True

        result = rule_test("1", "2", 1)
        assert rule_test.is_rules_all_valid == False


    def test_rules_all_kw(self):
        @RuleCheckAllKw(arg_info={"start": 0, "middle": 0, "end": 1},
                        rules=[(rules.RuleStrNotNullEmptyWs,), (rules.RuleIntZero,)])
        def rule_test(start, middle, end) -> str:
            return f"{start} {middle} {end}"
        result = rule_test("1", "2", 0)
        assert result == "1 2 0"

        with self.assertRaises(RuleError):
            rule_test("1", "2", 1)
        with self.assertRaises(RuleError):
            rule_test("1", "2", "0")
        with self.assertRaises(RuleError):
            rule_test(None, "2", 0)
        with self.assertRaises(RuleError):
            rule_test(22, "2", 0)
        with self.assertRaises(RuleError):
            rule_test("1", 2, 1)

    def test_rules_any_kw_empty_sub_rule(self):
        @RuleCheckAllKw(arg_info={"start": 0, "middle": 0, "end": 1},
                        rules=[(rules.RuleStrNotNullEmptyWs,), []])
        def rule_test(start, middle, end) -> str:
            return f"{start} {middle} {end}"
        result = rule_test("1", "2", 0)
        assert result == "1 2 0"

    def test_rules_all_kw_no_rules(self):
        @RuleCheckAllKw(arg_info={"start": rules.RuleStrNotNullEmptyWs,
                                  "middle": (rules.RuleStrNotNullEmptyWs,),
                                  "end": (rules.RuleIntZero,)}, raise_error=False)
        def rule_test(start, middle, end) -> str:
            return f"{start} {middle} {end}"
        result = rule_test("1", "2", 0)
        assert result == "1 2 0"
        assert rule_test.is_rules_kw_all_valid == True
        
        result = rule_test("1", "2", 1)
        assert rule_test.is_rules_kw_all_valid == False

    def test_rules_any_kw(self):
        @RuleCheckAnyKw(arg_info={"start": 0, "middle": 1, "end": 2},
                        rules=[(rules.RuleInt,), (rules.RuleIntPositive, rules.RuleFloatPositive),
                               (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
        def rule_test(start, middle, end) -> tuple:
            return (start, middle, end)
        result = rule_test(-1, 2, 0)
        assert result == (-1, 2, 0)
        
        result = rule_test(99, 2.6, 0)
        assert result == (99, 2.6, 0)
        with self.assertRaises(RuleError):
            rule_test(-1, -2, 0)
        with self.assertRaises(RuleError):
            rule_test("-1", -2, 0)
    
    def test_rules_all_kw_rule_single(self):
        @RuleCheckAnyKw(arg_info={"start": 0, "middle": 1, "end": 2},
                        rules=[rules.RuleInt, (rules.RuleIntPositive, rules.RuleFloatPositive),
                               (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
        def rule_test(start, middle, end) -> tuple:
            return (start, middle, end)
        result = rule_test(-1, 2, 0)
        assert result == (-1, 2, 0)
        
        result = rule_test(99, 2.6, 0)
        assert result == (99, 2.6, 0)
        with self.assertRaises(RuleError):
            rule_test(-1, -2, 0)
        with self.assertRaises(RuleError):
            rule_test("-1", -2, 0)
    
    def test_rules_all_kw_start_rule(self):
        @RuleCheckAnyKw(arg_info={"start": rules.RuleInt, "middle": 0, "end": 1},
                        rules=[(rules.RuleIntPositive, rules.RuleFloatPositive),
                               (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
        def rule_test(start, middle, end) -> tuple:
            return (start, middle, end)
        result = rule_test(-1, 2, 0)
        assert result == (-1, 2, 0)

        result = rule_test(99, 2.6, 0)
        assert result == (99, 2.6, 0)
        with self.assertRaises(RuleError):
            rule_test(-1, -2, 0)
        with self.assertRaises(RuleError):
            rule_test("-1", -2, 0)

    def test_rules_aany_kw_empty_sub_rule(self):
        @RuleCheckAnyKw(arg_info={"start": 0, "middle": 0, "end": 1},
                        rules=[(rules.RuleStrNotNullEmptyWs,), []])
        def rule_test(start, middle, end) -> str:
            return f"{start} {middle} {end}"
        result = rule_test("1", "2", 0)
        assert result == "1 2 0"

    def test_rules_any_all_kw(self):
        @RuleCheckAllKw(arg_info={"start": 0},
                        rules=[(rules.RuleStrNotNullEmptyWs,)])
        @RuleCheckAnyKw(arg_info={"middle": 0, "end": 1},
                        rules=[(rules.RuleIntPositive, rules.RuleFloatPositive),
                               (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
        def rule_test(start, middle, end) -> tuple:
            return (start, middle, end)
        result = rule_test(start="hello", middle=22, end=-3.4)
        assert result == ("hello", 22, -3.4)
        with self.assertRaises(RuleError):
            rule_test(start=" ", middle=22, end=-3.4)
        with self.assertRaises(RuleError):
            rule_test(start="hello", middle="m", end=-3.4)

    def test_rules_any_all_type_kw(self):
        @TypeCheckKw(arg_info={"start": str, "middle": 0, "end": 0},
                       types=[(int, float)])
        @RuleCheckAllKw(arg_info={"start": 0},
                        rules=[(rules.RuleStrNotNullEmptyWs,)])
        @RuleCheckAnyKw(arg_info={"middle": 0, "end": 1},
                        rules=[(rules.RuleIntPositive, rules.RuleFloatPositive),
                               (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
        def rule_test(start, middle, end) -> tuple:
            return (start, middle, end)
        result = rule_test(start="hello", middle=22, end=-3.4)
        assert result == ("hello", 22, -3.4)

    def test_rules_any_kw_no_rules(self):
        @RuleCheckAnyKw(arg_info={"start": rules.RuleStrNotNullEmptyWs,
                                  "middle": (rules.RuleStrNotNullEmptyWs,),
                                  "end": (rules.RuleIntZero,)}, raise_error=False)
        def rule_test(start, middle, end) -> str:
            return f"{start} {middle} {end}"
        result = rule_test("1", "2", 0)
        assert result == "1 2 0"
        assert rule_test.is_rules_any_valid == True

        result = rule_test("1", "2", 1)
        assert rule_test.is_rules_any_valid == False


class TestRuleDecoratorsClass(unittest.TestCase):
    def test_rule_check_any_dec(self):
        class Internal:
            @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive)
            def rule_test(self, one, two) -> float:
                return float(one) + float(two)
        instance = Internal()
        result = instance.rule_test(10, 12.3)
        assert result == 22.3

        with self.assertRaises(RuleError):
            result = instance.rule_test(3, "")
        with self.assertRaises(RuleError):
            result = instance.rule_test(3, -2.3)
    
    def test_rule_check_any_dec_init(self):
        class Internal:
            @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive)
            def __init__(self, one, two):
                self.one = one
                self.two = two
            
            def rule_test(self) -> float:
                return float(self.one) + float(self.two)
        instance = Internal(10, 12.3)
        result = instance.rule_test()
        assert result == 22.3

        with self.assertRaises(RuleError):
            result = Internal(3, "")
        with self.assertRaises(RuleError):
            result = Internal(3, -2.3)


    def test_rule_check_any_dec_kwargs_err(self):
        class Internal:
            @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive, raise_error=True)
            def rule_test(self, one, two) -> float:
                return float(one) + float(two)
        instance = Internal()
        result = instance.rule_test(10, 12.3)
        assert result == 22.3
    
    def test_rule_check_any_dec_kwargs(self):
        class Internal:
            @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive, raise_error=False)
            def rule_test(self, one, two) -> float:
                return float(one) + float(two)
        instance = Internal()
        result = instance.rule_test(10, 12.3)
        assert result == 22.3
        assert instance.rule_test.is_rules_any_valid == True
        
        result = instance.rule_test(10, -12.3)
        assert instance.rule_test.is_rules_any_valid == False
    
    def test_rule_str(self):
        class Internal:
            @RuleCheckAll(rules.RuleStrNotNullEmptyWs)
            def rule_test(self, start, middle, end) -> str:
                return f"{start} {middle} {end}"
        instance = Internal()
        result = instance.rule_test("1", "2", ".")
        assert result == "1 2 ."
        result = instance.rule_test(start="1", middle="2", end=".")
        assert result == "1 2 ."
        with self.assertRaises(RuleError):
            instance.rule_test("1", "2", 1)
        with self.assertRaises(RuleError):
            instance.rule_test(start="1", middle=2, end=".")

    def test_rules_all_kw(self):
        class Internal:
            @RuleCheckAllKw(arg_info={"start": 0, "middle": 0, "end": 1},
                            rules=[(rules.RuleStrNotNullEmptyWs,), (rules.RuleIntZero,)])
            def rule_test(self, start, middle, end) -> str:
                return f"{start} {middle} {end}"

        instance = Internal()
        result = instance.rule_test("1", "2", 0)
        assert result == "1 2 0"

        with self.assertRaises(RuleError):
            instance.rule_test("1", "2", 1)
        with self.assertRaises(RuleError):
            instance.rule_test("1", "2", "0")
        with self.assertRaises(RuleError):
            instance.rule_test(None, "2", 0)
        with self.assertRaises(RuleError):
            instance.rule_test(22, "2", 0)
        with self.assertRaises(RuleError):
            instance.rule_test("1", 2, 1)

    def test_rules_any_kw_empty_sub_rule(self):
        class Internal:
            @RuleCheckAllKw(arg_info={"start": 0, "middle": 0, "end": 1},
                            rules=[(rules.RuleStrNotNullEmptyWs,), []])
            def rule_test(self, start, middle, end) -> str:
                return f"{start} {middle} {end}"
        instance = Internal()
        result = instance.rule_test("1", "2", 0)
        assert result == "1 2 0"

    def test_rules_all_kw_no_rules(self):
        class Internal:
            @RuleCheckAllKw(arg_info={"start": rules.RuleStrNotNullEmptyWs,
                                    "middle": (rules.RuleStrNotNullEmptyWs,),
                                    "end": (rules.RuleIntZero,)}, raise_error=False)
            def rule_test(self, start, middle, end) -> str:
                return f"{start} {middle} {end}"

        instance = Internal()
        result = instance.rule_test("1", "2", 0)
        assert result == "1 2 0"
        assert instance.rule_test.is_rules_kw_all_valid == True

        result = instance.rule_test("1", "2", 1)
        assert instance.rule_test.is_rules_kw_all_valid == False

    def test_rules_any_kw(self):
        class Internal:
            @RuleCheckAnyKw(arg_info={"start": 0, "middle": 1, "end": 2},
                            rules=[(rules.RuleInt,), (rules.RuleIntPositive, rules.RuleFloatPositive),
                                (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
            def rule_test(self, start, middle, end) -> tuple:
                return (start, middle, end)

        instance = Internal()
        result = instance.rule_test(-1, 2, 0)
        assert result == (-1, 2, 0)

        result = instance.rule_test(99, 2.6, 0)
        assert result == (99, 2.6, 0)
        with self.assertRaises(RuleError):
            instance.rule_test(-1, -2, 0)
        with self.assertRaises(RuleError):
            instance.rule_test("-1", -2, 0)

    def test_rules_all_kw_rule_single(self):
        class Internal:
            @RuleCheckAnyKw(arg_info={"start": 0, "middle": 1, "end": 2},
                            rules=[rules.RuleInt, (rules.RuleIntPositive, rules.RuleFloatPositive),
                                (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
            def rule_test(self, start, middle, end) -> tuple:
                return (start, middle, end)
            
        instance = Internal()
        result = instance.rule_test(-1, 2, 0)
        assert result == (-1, 2, 0)

        result = instance.rule_test(99, 2.6, 0)
        assert result == (99, 2.6, 0)
        with self.assertRaises(RuleError):
            instance.rule_test(-1, -2, 0)
        with self.assertRaises(RuleError):
            instance.rule_test("-1", -2, 0)

    def test_rules_all_kw_start_rule(self):
        class Internal:
            @RuleCheckAnyKw(arg_info={"start": rules.RuleInt, "middle": 0, "end": 1},
                            rules=[(rules.RuleIntPositive, rules.RuleFloatPositive),
                                (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
            def rule_test(self, start, middle, end) -> tuple:
                return (start, middle, end)

        instance = Internal()
        result = instance.rule_test(-1, 2, 0)
        assert result == (-1, 2, 0)

        result = instance.rule_test(99, 2.6, 0)
        assert result == (99, 2.6, 0)
        with self.assertRaises(RuleError):
            instance.rule_test(-1, -2, 0)
        with self.assertRaises(RuleError):
            instance.rule_test("-1", -2, 0)

    def test_rules_aany_kw_empty_sub_rule(self):
        class Internal:
            @RuleCheckAnyKw(arg_info={"start": 0, "middle": 0, "end": 1},
                            rules=[(rules.RuleStrNotNullEmptyWs,), []])
            def rule_test(self, start, middle, end) -> str:
                return f"{start} {middle} {end}"

        instance = Internal()
        result = instance.rule_test("1", "2", 0)
        assert result == "1 2 0"

    def test_rules_any_all_kw(self):
        class Internal:
            @RuleCheckAllKw(arg_info={"start": 0},
                            rules=[(rules.RuleStrNotNullEmptyWs,)])
            @RuleCheckAnyKw(arg_info={"middle": 0, "end": 1},
                            rules=[(rules.RuleIntPositive, rules.RuleFloatPositive),
                                (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
            def rule_test(self, start, middle, end) -> tuple:
                return (start, middle, end)

        instance = Internal()
        result = instance.rule_test(start="hello", middle=22, end=-3.4)
        assert result == ("hello", 22, -3.4)
        with self.assertRaises(RuleError):
            instance.rule_test(start=" ", middle=22, end=-3.4)
        with self.assertRaises(RuleError):
            instance.rule_test(start="hello", middle="m", end=-3.4)

    def test_rules_any_all_type_kw(self):
        class Internal:
            @TypeCheckKw(arg_info={"start": str, "middle": 0, "end": 0},
                        types=[(int, float)])
            @RuleCheckAllKw(arg_info={"start": 0},
                            rules=[(rules.RuleStrNotNullEmptyWs,)])
            @RuleCheckAnyKw(arg_info={"middle": 0, "end": 1},
                            rules=[(rules.RuleIntPositive, rules.RuleFloatPositive),
                                (rules.RuleIntNegativeOrZero, rules.RuleFloatNegativeOrZero)])
            def rule_test(self, start, middle, end) -> tuple:
                return (start, middle, end)

        instance = Internal()
        result = instance.rule_test(start="hello", middle=22, end=-3.4)
        assert result == ("hello", 22, -3.4)

    def test_rules_any_kw_no_rules(self):
        class Internal:
            @RuleCheckAnyKw(arg_info={"start": rules.RuleStrNotNullEmptyWs,
                                    "middle": (rules.RuleStrNotNullEmptyWs,),
                                    "end": (rules.RuleIntZero,)}, raise_error=False)
            def rule_test(self, start, middle, end) -> str:
                return f"{start} {middle} {end}"
        
        instance = Internal()
        result = instance.rule_test("1", "2", 0)
        assert result == "1 2 0"
        assert instance.rule_test.is_rules_any_valid == True

        result = instance.rule_test("1", "2", 1)
        assert instance.rule_test.is_rules_any_valid == False

if __name__ == '__main__':
    unittest.main()
