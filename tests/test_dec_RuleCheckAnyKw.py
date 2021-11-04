import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.exceptions import RuleError
from kwhelp import rules
from kwhelp.decorator import DecFuncEnum, RuleCheckAnyKw


class TestRuleCheckAnyKw(unittest.TestCase):
    def test_rule_check_anykw_gen(self):
        @RuleCheckAnyKw(arg_info={"first": 0, "last": 0, "hours": 1, "name": 2},
                        rules=[rules.RuleIntPositive,
                        (rules.RuleIntPositive, rules.RuleFloatPositive),
                        rules.RuleStrNotNullEmptyWs])
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        result = foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        result = foo(first=1, last=100, hours=12, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12
        assert result["name"] == "test"
        with self.assertRaises(RuleError):
            foo(first="1", last=100, hours=12.5, name="test")
        with self.assertRaises(RuleError):
            foo(first=1, last="100", hours=12.5, name="test")
        with self.assertRaises(RuleError):
            foo(first=1, last=100, hours="12.5", name="test")
        with self.assertRaises(RuleError):
            foo(first=1, last=100, hours=12.5, name=" ")
        with self.assertRaises(RuleError):
            foo(first=-1, last=100, hours=12.5, name="test")
        with self.assertRaises(RuleError):
            foo(first=1, last=100, hours=-12.5, name="test")

    def test_rule_check_anykw_opt_return(self):
        @RuleCheckAnyKw(arg_info={"first": 0, "last": 0, "hours": 1, "name": 2},
                        rules=[rules.RuleIntPositive,
                        (rules.RuleIntPositive, rules.RuleFloatPositive),
                        rules.RuleStrNotNullEmptyWs], opt_return=None)
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        result = foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        result = False
        result = foo(first="1", last=100, hours=12.5, name="test")
        assert result == None
        result = False
        result = foo(first=1, last="100", hours=12.5, name="test")
        assert result == None
        result = False
        result = foo(first=1, last=100, hours="12.5", name="test")
        assert result == None
        result = False
        result = foo(first=1, last=100, hours=12.5, name="")
        assert result == None

    def test_rule_check_anykw_raise_error_opt_return(self):
        @RuleCheckAnyKw(arg_info={"first": 0, "last": 0, "hours": 1, "name": 2},
                        rules=[rules.RuleIntPositive,
                        (rules.RuleIntPositive, rules.RuleFloatPositive),
                        rules.RuleStrNotNullEmptyWs], opt_return=None, raise_error=False)
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        assert foo.is_rules_any_valid == True
        result = foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        assert foo.is_rules_any_valid == True
        result = False
        result = foo(first="1", last=100, hours=12.5, name="test")
        assert result == None
        assert foo.is_rules_any_valid == False
        result = False
        result = foo(first=1, last="100", hours=12.5, name="test")
        assert result == None
        assert foo.is_rules_any_valid == False
        result = False
        result = foo(first=1, last=100, hours="12.5", name="test")
        assert result == None
        assert foo.is_rules_any_valid == False
        result = False
        result = foo(first=1, last=100, hours=12.5, name=" ")
        assert result == None
        assert foo.is_rules_any_valid == False


class TestRuleCheckAnyKwClass(unittest.TestCase):
    def test_rule_check_anykw_gen(self):
        class Bar:
            @RuleCheckAnyKw(arg_info={"first": 0, "last": 0, "hours": 1, "name": 2},
                            rules=[rules.RuleIntPositive,
                            (rules.RuleIntPositive, rules.RuleFloatPositive),
                            rules.RuleStrNotNullEmptyWs], ftype=DecFuncEnum.METHOD)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d
        b = Bar()
        result = b.foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        with self.assertRaises(RuleError):
            b.foo(first="1", last=100, hours=12.5, name="test")
        with self.assertRaises(RuleError):
            b.foo(first=1, last="100", hours=12.5, name="test")
        with self.assertRaises(RuleError):
            b.foo(first=1, last=100, hours="12.5", name="test")
        with self.assertRaises(RuleError):
            b.foo(first=1, last=100, hours=12.5, name=" ")
        with self.assertRaises(RuleError):
            b.foo(first=-1, last=100, hours=12.5, name="test")
        with self.assertRaises(RuleError):
            b.foo(first=1, last=100, hours=-12.5, name="test")

    def test_rule_check_anykw_opt_return(self):
        class Bar:
            @RuleCheckAnyKw(arg_info={"first": 0, "last": 0, "hours": 1, "name": 2},
                            rules=[rules.RuleIntPositive,
                            (rules.RuleIntPositive, rules.RuleFloatPositive),
                            rules.RuleStrNotNullEmptyWs],
                            opt_return=None, ftype=DecFuncEnum.METHOD)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d
        b = Bar()
        result = b.foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        result = False
        result = b.foo(first="1", last=100, hours=12.5, name="test")
        assert result == None
        result = False
        result = b.foo(first=1, last="100", hours=12.5, name="test")
        assert result == None
        result = False
        result = b.foo(first=1, last=100, hours="12.5", name="test")
        assert result == None
        result = False
        result = b.foo(first=1, last=100, hours=12.5, name="")
        assert result == None

    def test_rule_check_anykw_raise_error_opt_return(self):
        class Bar:
            @RuleCheckAnyKw(arg_info={"first": 0, "last": 0, "hours": 1, "name": 2},
                            rules=[rules.RuleIntPositive,
                            (rules.RuleIntPositive, rules.RuleFloatPositive),
                            rules.RuleStrNotNullEmptyWs],
                            opt_return=None, raise_error=False,
                            ftype=DecFuncEnum.METHOD)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d
        b = Bar()
        assert b.foo.is_rules_any_valid == True
        result = b.foo(first=1, last=100, hours=12.5, name="test")
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12.5
        assert result["name"] == "test"
        assert b.foo.is_rules_any_valid == True
        result = False
        result = b.foo(first="1", last=100, hours=12.5, name="test")
        assert result == None
        assert b.foo.is_rules_any_valid == False
        result = False
        result = b.foo(first=1, last="100", hours=12.5, name="test")
        assert result == None
        assert b.foo.is_rules_any_valid == False
        result = False
        result = b.foo(first=1, last=100, hours="12.5", name="test")
        assert result == None
        assert b.foo.is_rules_any_valid == False
        result = False
        result = b.foo(first=1, last=100, hours=12.5, name=" ")
        assert result == None
        assert b.foo.is_rules_any_valid == False


if __name__ == '__main__':
    unittest.main()
