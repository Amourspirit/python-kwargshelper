import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import DecFuncEnum, RuleCheckAll
from kwhelp import rules
from kwhelp.exceptions import RuleError


class TestRuleCheckAll(unittest.TestCase):
    def test_rule_check_all_gen(self):
        @RuleCheckAll(rules.RuleInt, rules.RuleIntPositive)
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        result = foo(first=1, last=100, hours=12, years=22)
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12
        assert result["years"] == 22
        with self.assertRaises(RuleError):
            foo(first="1", last=100, hours=12, years=22)
        with self.assertRaises(RuleError):
            foo(first=1, last="100", hours=12, years=22)
        with self.assertRaises(RuleError):
            foo(first=1, last=100, hours="12", years=22)
        with self.assertRaises(RuleError):
            foo(first=1, last=100, hours=12, years="22")
        with self.assertRaises(RuleError):
            foo(first=-1, last=100, hours=12, years=22)
        with self.assertRaises(RuleError):
            foo(first=1, last=100, hours=-12, years=22)

    def test_rule_check_all_opt_return(self):
        @RuleCheckAll(rules.RuleFloatPositive, opt_return=None)
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        result = foo(first=1.0, last=100.0, hours=12.5, years=22.0)
        assert result["first"] == 1.0
        assert result["last"] == 100.0
        assert result["hours"] == 12.5
        assert result["years"] == 22.0
        result = False
        result = foo(first="1.0", last=100.0, hours=12.5, years=22.0)
        assert result == None
        result = False
        result = foo(first=1.0, last="100.0", hours=12.5, years=22.0)
        assert result == None
        result = False
        result = foo(first=1.0, last=100.0, hours="12.5", years=22.0)
        assert result == None
        result = False
        result = foo(first=1.0, last=100.0, hours=12.5, years="22.0")
        assert result == None

    def test_rule_check_all_raise_error_opt_return(self):
        @RuleCheckAll(rules.RuleIntPositive, opt_return=None, raise_error=False)
        def foo(first, last, **kwargs):
            d = {**kwargs}
            d["first"] = first
            d["last"] = last
            return d
        assert foo.is_rules_all_valid == True
        result = foo(first=1, last=100, hours=12, years=22)
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12
        assert result["years"] == 22
        assert foo.is_rules_all_valid == True
        result = False
        result = foo(first="1", last=100, hours=12, years=22)
        assert result == None
        assert foo.is_rules_all_valid == False
        result = False
        result = foo(first=1, last="100", hours=12, years=22)
        assert result == None
        assert foo.is_rules_all_valid == False
        result = False
        result = foo(first=1, last=100, hours="12", years=22)
        assert result == None
        assert foo.is_rules_all_valid == False
        result = False
        result = foo(first=1, last=100, hours=12, years="22")
        assert result == None
        assert foo.is_rules_all_valid == False

    def test_rule_check_all_args(self):
        @RuleCheckAll(rules.RuleIntPositive)
        def add_positives(*args) -> float:
            result = 0.0
            for arg in args:
                result += float(arg)
            return result
        result = add_positives(1, 4, 7, 4, 7)
        assert result == 23
        with self.assertRaises(RuleError):
            add_positives(2, 1, -1)

    def test_rule_check_all_args_pos(self):
        @RuleCheckAll(rules.RuleIntPositive)
        def add_positives(first, second, *args, **kwargs) -> float:
            result = float(first + second + kwargs.get("last", 0.0))
            for arg in args:
                result += float(arg)
            return result
        result = add_positives(1, 4, 7, 4, 7)
        assert result == 23
        result = add_positives(1, 4, 7, 4, last=7)
        assert result == 23
        with self.assertRaises(RuleError):
            add_positives(2, 1, -1)
        with self.assertRaises(RuleError):
            add_positives(-1, 4, 7, 4, 7)
        with self.assertRaises(RuleError):
            add_positives(1, 4, 7, 4, last="7")
        with self.assertRaises(RuleError):
            add_positives(1, 4, 7, 4, last=-7)


class TestRuleCheckAllClass(unittest.TestCase):

    def test_rule_check_all_gen(self):
        class Bar:
            def __init__(self):
                self._test = 0

            @RuleCheckAll(rules.RuleIntPositive, ftype=DecFuncEnum.METHOD)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d

            @property
            def test(self):
                return self._test

            @test.setter
            @RuleCheckAll(rules.RuleIntPositive,
                          ftype=DecFuncEnum.PROPERTY_CLASS)
            def test(self, value):
                self._test = value

        b = Bar()
        result = b.foo(first=1, last=100, hours=12, years=22)
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12
        assert result["years"] == 22
        assert b.test == 0
        b.test = 345
        assert b.test == 345
        with self.assertRaises(RuleError):
            b.foo(first="1", last=100, hours=12, years=22)
        with self.assertRaises(RuleError):
            b.foo(first=1, last="100", hours=12, years=22)
        with self.assertRaises(RuleError):
            b.foo(first=1, last=100, hours="12", years=22)
        with self.assertRaises(RuleError):
            b.foo(first=1, last=100, hours=12, years="22")
        with self.assertRaises(RuleError):
            b.foo(first=-1, last=100, hours=12, years=22)
        with self.assertRaises(RuleError):
            b.foo(first=1, last=100, hours=-12, years=22)
        with self.assertRaises(RuleError):
            b.test = -4

    def test_rule_check_all_opt_return(self):
        class Bar:
            def __init__(self):
                self._test = 0

            @RuleCheckAll(rules.RuleIntPositive, ftype=DecFuncEnum.METHOD, opt_return=None)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d

            @property
            def test(self):
                return self._test

            @test.setter
            @RuleCheckAll(rules.RuleIntPositive,
                          ftype=DecFuncEnum.PROPERTY_CLASS)
            def test(self, value):
                self._test = value
        b = Bar()
        result = b.foo(first=1, last=100, hours=12, years=22)
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12
        assert result["years"] == 22
        assert b.test == 0
        b.test = 44
        assert b.test == 44
        result = False
        result = b.foo(first="1", last=100, hours=12, years=22)
        assert result == None
        result = False
        result = b.foo(first=1, last="100", hours=12, years=22)
        assert result == None
        result = False
        result = b.foo(first=1, last=100, hours="12", years=22)
        assert result == None
        result = False
        result = b.foo(first=1, last=100, hours=12, years="22")
        assert result == None

    def test_rule_check_all_raise_error_opt_return(self):
        class Bar:
            @RuleCheckAll(rules.RuleIntPositive, ftype=DecFuncEnum.METHOD, opt_return=None, raise_error=False)
            def foo(self, first, last, **kwargs):
                d = {**kwargs}
                d["first"] = first
                d["last"] = last
                return d
        b = Bar()
        assert b.foo.is_rules_all_valid == True
        result = b.foo(first=1, last=100, hours=12, years=22)
        assert result["first"] == 1
        assert result["last"] == 100
        assert result["hours"] == 12
        assert result["years"] == 22
        assert b.foo.is_rules_all_valid == True
        result = False
        result = b.foo(first="1", last=100, hours=12, years=22)
        assert result == None
        assert b.foo.is_rules_all_valid == False
        result = False
        result = b.foo(first=1, last="100", hours=12, years=22)
        assert result == None
        assert b.foo.is_rules_all_valid == False
        result = False
        result = b.foo(first=1, last=100, hours="12", years=22)
        assert result == None
        assert b.foo.is_rules_all_valid == False
        result = False
        result = b.foo(first=1, last=100, hours=12, years="22")
        assert result == None
        assert b.foo.is_rules_all_valid == False

    def test_rule_check_all_args(self):
        class Bar:
            @RuleCheckAll(rules.RuleIntPositive, ftype=DecFuncEnum.METHOD)
            def add_positives(self, *args) -> float:
                result = 0.0
                for arg in args:
                    result += float(arg)
                return result
        b = Bar()
        result = b.add_positives(1, 4, 7, 4, 7)
        assert result == 23.
        with self.assertRaises(RuleError):
            b.add_positives(2, 1, -1)

    def test_rule_check_all_args_pos(self):
        class Bar:
            @RuleCheckAll(rules.RuleIntPositive, ftype=DecFuncEnum.METHOD)
            def add_positives(self, first, second, *args, **kwargs) -> float:
                result = float(first + second + kwargs.get("last", 0.0))
                for arg in args:
                    result += float(arg)
                return result
        b = Bar()
        result = b.add_positives(1, 4, 7, 4, 7)
        assert result == 23
        result = b.add_positives(1, 4, 7, 4, last=7)
        assert result == 23
        with self.assertRaises(RuleError):
            b.add_positives(2, 1, -1)
        with self.assertRaises(RuleError):
            b.add_positives(-1, 4, 7, 4, 7)
        with self.assertRaises(RuleError):
            b.add_positives(1, 4, 7, 4, last="7")
        with self.assertRaises(RuleError):
            b.add_positives(1, 4, 6, 3, last=-7)


if __name__ == '__main__':
    unittest.main()
