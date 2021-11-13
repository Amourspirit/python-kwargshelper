import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import DecArgEnum, DecFuncEnum, RuleCheckAny
from kwhelp import rules
from kwhelp.exceptions import RuleError


class TestRuleCheckAny(unittest.TestCase):
    def test_rule_check_any_gen(self):
        @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive)
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        result = foo(first=1, last=100, hours=12.5, years=22)
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["years"] == 22
        with self.assertRaises(RuleError):
            foo(first="1", last=100, hours=12.5, years=22)
        with self.assertRaises(RuleError):
            foo(first=1, last="100", hours=12.5, years=22)
        with self.assertRaises(RuleError):
            foo(first=1, last=100, hours="12.5", years=22)
        with self.assertRaises(RuleError):
            foo(first=1, last=100, hours=12.5, years="22")
        with self.assertRaises(RuleError):
            foo(first=-1, last=100, hours=12.5, years=22)
        with self.assertRaises(RuleError):
            foo(first=1, last=100, hours=-12.5, years=22)

    def test_rule_check_any_opt_args_filter_kwargs(self):
        @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive, opt_args_filter=DecArgEnum.KWARGS)
        def foo(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]
        result = foo("the", "quick", "brown", "fox",
                     first="1st", last=-1, hours=12.5, years=22)
        assert result[0] == "the"
        with self.assertRaises(RuleError):
            foo("the", "quick", "brown", "fox",
                first="1", last=-1, hours=-12.5, years=22)
        with self.assertRaises(RuleError):
            foo("the", "quick", "brown", "fox",
                first="1", last=-1, hours=12.5, years="20th")
    
    def test_rule_check_any_opt_args_filter_args(self):
        @RuleCheckAny(rules.RuleStrNotNullEmptyWs, opt_args_filter=DecArgEnum.ARGS)
        def foo(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]
        result = foo("the", "quick", "brown", "fox",
                     first="1st", last=-1, hours=12.5, years=22)
        assert result[0] == "the"
        with self.assertRaises(RuleError):
            foo("the", "quick", "brown", "",
                first="1st", last=-1, hours=12.5, years=22)
        with self.assertRaises(RuleError):
            foo("the", "quick", " ", "fox",
                first="1st", last=-1, hours=12.5, years=22)


    def test_rule_check_any_opt_args_filter_no_args(self):
        @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive, opt_args_filter=DecArgEnum.NO_ARGS)
        def foo(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]
        result = foo("the", "quick", "brown", "fox",
                     first=1, last=100, hours=12.5, years=22)
        assert result[0] == "the"
        with self.assertRaises(RuleError):
            foo("the", "quick", "brown", "fox",
                first=1, last=100, hours=-12.5, years=22)
        with self.assertRaises(RuleError):
            foo("the", "quick", "brown", "fox",
                first=-1, last=100, hours=12.5, years=22)

    def test_rule_check_any_opt_args_filter_named(self):
        @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive, opt_args_filter=DecArgEnum.NAMED_ARGS)
        def foo(*args, first, last, **kwargs):
            return [*args] + [first, last] + [v for _, v in kwargs.items()]
        result = foo("the", "quick", "brown", "fox",
                     first=44.33, last=100, hours="Many", years="20th")
        assert result[0] == "the"
        with self.assertRaises(RuleError):
            foo("the", "quick", "brown", "fox",
                first=1, last=-100, hours="Many", years="20th")
        with self.assertRaises(RuleError):
            foo("the", "quick", "brown", "fox",
                first=-1, last=100, hours="Many", years="20th")

    def test_rule_check_any_opt_return(self):
        @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive, opt_return=None)
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        result = foo(first=1, last=100, hours=12.5, years=22)
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["years"] == 22
        result = False
        result = foo(first="1", last=100, hours=12.5, years=22)
        assert result == None
        result = False
        result = foo(first=1, last="100", hours=12.5, years=22)
        assert result == None
        result = False
        result = foo(first=1, last=100, hours="12.5", years=22)
        assert result == None
        result = False
        result = foo(first=1, last=100, hours=12.5, years="22")
        assert result == None

    def test_rule_check_any_raise_error_opt_return(self):
        @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive,
                      opt_return=None, raise_error=False)
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        assert foo.is_rules_any_valid == True
        result = foo(first=1, last=100, hours=12.5, years=22)
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["years"] == 22
        assert foo.is_rules_any_valid == True
        result = False
        result = foo(first="1", last=100, hours=12.5, years=22)
        assert result == None
        assert foo.is_rules_any_valid == False
        result = False
        result = foo(first=1, last="100", hours=12.5, years=22)
        assert result == None
        assert foo.is_rules_any_valid == False
        result = False
        result = foo(first=1, last=100, hours="12.5", years=22)
        assert result == None
        assert foo.is_rules_any_valid == False
        result = False
        result = foo(first=1, last=100, hours=12.5, years="22")
        assert result == None
        assert foo.is_rules_any_valid == False

    def test_rule_check_any_args(self):
        @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive)
        def add_positives(*args) -> float:
            result = 0.0
            for arg in args:
                result += float(arg)
            return result
        result = add_positives(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        with self.assertRaises(RuleError):
            add_positives(2, 1.2, -1)

    def test_rule_check_any_args_pos(self):
        @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive)
        def add_positives(first, second, *args, **kwargs) -> float:
            result = float(first + second + kwargs.get("last", 0.0))
            for arg in args:
                result += float(arg)
            return result
        result = add_positives(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        result = add_positives(1, 4, 6.9, 3.9, last=7.3)
        assert result == 23.1
        with self.assertRaises(RuleError):
            add_positives(2, 1.2, -1)
        with self.assertRaises(RuleError):
            add_positives(-1, 4, 6.9, 3.9, 7.3)
        with self.assertRaises(RuleError):
            add_positives(1, 4, 6.9, 3.9, last="7.3")
        with self.assertRaises(RuleError):
            add_positives(1, 4, 6.9, 3.9, last=-7.3)

class TestRuleCheckAnyClass(unittest.TestCase):

    def test_rule_check_any_gen(self):
        class Bar:
            def __init__(self):
                self._test = 0
            @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive,
                          ftype=DecFuncEnum.METHOD)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d
            @property
            def test(self):
                return self._test
            @test.setter
            @RuleCheckAny(rules.RuleIntPositive,
                          ftype=DecFuncEnum.PROPERTY_CLASS)
            def test(self, value):
                self._test = value

        b = Bar()
        result = b.foo(first=1, last=100, hours=12.5, years=22)
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["years"] == 22
        assert b.test == 0
        b.test = 345
        assert b.test == 345
        with self.assertRaises(RuleError):
            b.foo(first="1", last=100, hours=12.5, years=22)
        with self.assertRaises(RuleError):
            b.foo(first=1, last="100", hours=12.5, years=22)
        with self.assertRaises(RuleError):
            b.foo(first=1, last=100, hours="12.5", years=22)
        with self.assertRaises(RuleError):
            b.foo(first=1, last=100, hours=12.5, years="22")
        with self.assertRaises(RuleError):
            b.foo(first=-1, last=100, hours=12.5, years=22)
        with self.assertRaises(RuleError):
            b.foo(first=1, last=100, hours=-12.5, years=22)
        with self.assertRaises(RuleError):
            b.test = -4

    def test_rule_check_any_opt_return(self):
        class Bar:
            def __init__(self):
                self._test = 0
            @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive,
                          ftype=DecFuncEnum.METHOD, opt_return=None)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d
            @property
            def test(self):
                return self._test
            @test.setter
            @RuleCheckAny(rules.RuleIntPositive,
                          ftype=DecFuncEnum.PROPERTY_CLASS)
            def test(self, value):
                self._test = value
        b = Bar()
        result = b.foo(first=1, last=100, hours=12.5, years=22)
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["years"] == 22
        assert b.test == 0
        b.test = 44
        assert b.test == 44
        result = False
        result = b.foo(first="1", last=100, hours=12.5, years=22)
        assert result == None
        result = False
        result = b.foo(first=1, last="100", hours=12.5, years=22)
        assert result == None
        result = False
        result = b.foo(first=1, last=100, hours="12.5", years=22)
        assert result == None
        result = False
        result = b.foo(first=1, last=100, hours=12.5, years="22")
        assert result == None

    def test_rule_check_any_raise_error_opt_return(self):
        class Bar:
            @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive,
                          ftype=DecFuncEnum.METHOD, opt_return=None, raise_error=False)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d
        b = Bar()
        assert b.foo.is_rules_any_valid == True
        result = b.foo(first=1, last=100, hours=12.5, years=22)
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["years"] == 22
        assert b.foo.is_rules_any_valid == True
        result = False
        result = b.foo(first="1", last=100, hours=12.5, years=22)
        assert result == None
        assert b.foo.is_rules_any_valid == False
        result = False
        result = b.foo(first=1, last="100", hours=12.5, years=22)
        assert result == None
        assert b.foo.is_rules_any_valid == False
        result = False
        result = b.foo(first=1, last=100, hours="12.5", years=22)
        assert result == None
        assert b.foo.is_rules_any_valid == False
        result = False
        result = b.foo(first=1, last=100, hours=12.5, years="22")
        assert result == None
        assert b.foo.is_rules_any_valid == False

    def test_rule_check_any_args(self):
        class Bar:
            @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive, ftype=DecFuncEnum.METHOD)
            def add_positives(self, *args) -> float:
                result = 0.0
                for arg in args:
                    result += float(arg)
                return result
        b = Bar()
        result = b.add_positives(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        with self.assertRaises(RuleError):
            b.add_positives(2, 1.2, -1)

    def test_rule_check_any_args_pos(self):
        class Bar:
            @RuleCheckAny(rules.RuleIntPositive, rules.RuleFloatPositive, ftype=DecFuncEnum.METHOD)
            def add_positives(self, first, second, *args, **kwargs) -> float:
                result = float(first + second + kwargs.get("last", 0.0))
                for arg in args:
                    result += float(arg)
                return result
        b = Bar()
        result = b.add_positives(1, 4, 6.9, 3.9, 7.3)
        assert result == 23.1
        result = b.add_positives(1, 4, 6.9, 3.9, last=7.3)
        assert result == 23.1
        with self.assertRaises(RuleError):
            b.add_positives(2, 1.2, -1)
        with self.assertRaises(RuleError):
            b.add_positives(-1, 4, 6.9, 3.9, 7.3)
        with self.assertRaises(RuleError):
            b.add_positives(1, 4, 6.9, 3.9, last="7.3")
        with self.assertRaises(RuleError):
            b.add_positives(1, 4, 6.9, 3.9, last=-7.3)

if __name__ == '__main__':
    unittest.main()
