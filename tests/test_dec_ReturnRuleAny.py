import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.decorator import AcceptedTypes, DecFuncEnum, ReturnRuleAny
from kwhelp import rules
from kwhelp.exceptions import RuleError


class TestReturnRuleAllDecorators(unittest.TestCase):
    def test_return_gen(self):
        @ReturnRuleAny(rules.RuleInt, rules.RuleFloatNegative)
        def req_test(*arg):
            return sum(arg)
    
        result = req_test(2, 4)
        assert result == 6
        result = req_test(-2, -10)
        assert result == - 12
        with self.assertRaises(RuleError):
            # return type not an int or a float negative
            result = req_test(2, 2.4)

    def test_return_opt_return(self):
        @ReturnRuleAny(rules.RuleInt, rules.RuleFloatNegative, opt_return=None)
        def req_test(*arg):
            return sum(arg)

        result = req_test(2, 4)
        assert result == 6
        result = req_test(-2, -10)
        assert result == - 12
        result = False
        result = req_test(2, 2.4)
        assert result == None

    def test_return_none(self):
        @ReturnRuleAny(rules.RuleNone, rules.RuleIntZero)
        def req_test(arg):
            return arg
        result = req_test(arg=None)
        assert result is None
        result = req_test(arg=0)
        assert result == 0
        with self.assertRaises(RuleError):
            result = req_test(arg=self)
        with self.assertRaises(RuleError):
            result = req_test(arg=1)


class TestReturnRuleAllDecoratorsClass(unittest.TestCase):
    def test_return_gen(self):
        class T:
            @ReturnRuleAny(rules.RuleInt, rules.RuleFloatNegative, ftype=DecFuncEnum.METHOD)
            def req_test(self, *arg):
                return sum(arg)
        t = T()
        result = t.req_test(2, 4)
        assert result == 6
        result = t.req_test(-2, -10)
        assert result == -12
        result = t.req_test(-2, -1.2)
        assert result == -3.2
        with self.assertRaises(RuleError):
            # result is not int or negative float
            result = t.req_test(2, 2.5)

    def test_return_opt_return(self):
        class T:
            @ReturnRuleAny(rules.RuleInt, rules.RuleFloatNegative, ftype=DecFuncEnum.METHOD, opt_return=None)
            def req_test(self, *arg):
                return sum(arg)
        t = T()
        result = t.req_test(2, 4)
        assert result == 6
        result = t.req_test(-2, -10)
        assert result == -12
        result = t.req_test(-2, -1.2)
        assert result == -3.2
        result = False
        result = t.req_test(2, 2.5)
        assert result == None

    def test_return_static(self):
        class T:
            @staticmethod
            @ReturnRuleAny(rules.RuleInt, rules.RuleFloatNegative, ftype=DecFuncEnum.METHOD_STATIC)
            def req_test(*arg):
                return sum(arg)
        result = T.req_test(2, 4)
        assert result == 6
        result = T.req_test(-2, -10)
        assert result == -12
        result = T.req_test(-2, -1.2)
        assert result == -3.2
        with self.assertRaises(RuleError):
            # result is not int or negative float
            result = T.req_test(2, 2.5)

    def test_return_classmethod(self):
        class T:
            @classmethod
            @ReturnRuleAny(rules.RuleInt, rules.RuleFloatNegative, ftype=DecFuncEnum.METHOD_CLASS)
            def req_test(cls, *arg):
                return sum(arg)
        result = T.req_test(2, 4)
        assert result == 6
        result = T.req_test(-2, -10)
        assert result == -12
        result = T.req_test(-2, -1.2)
        assert result == -3.2
        with self.assertRaises(RuleError):
            # result is not int or negative float
            result = T.req_test(2, 2.5)

    def test_class_property(self):
        class T:
            @AcceptedTypes((int, float), ftype=DecFuncEnum.METHOD)
            def __init__(self, tmp):
               self._tmp = tmp

            @property
            @ReturnRuleAny(rules.RuleIntPositive, rules.RuleFloatNegative, ftype=DecFuncEnum.PROPERTY_CLASS)
            def tmp(self):
                return self._tmp

            @tmp.setter
            @AcceptedTypes((int, float), ftype=DecFuncEnum.PROPERTY_CLASS)
            def tmp(self, value):
                self._tmp = value

        t = T(2)
        assert t.tmp == 2
        t.tmp = 5
        assert t.tmp == 5
        t.tmp = -2.4
        assert t.tmp == -2.4
        t.tmp = 2.5
        # t.tmp accepsts int or float when setting but only int as return
        with self.assertRaises(RuleError):
            result = t.tmp
        t.tmp = 2.55
        with self.assertRaises(RuleError):
            # positive float is not accepted as return value
            result = t.tmp


if __name__ == '__main__':
    unittest.main()
