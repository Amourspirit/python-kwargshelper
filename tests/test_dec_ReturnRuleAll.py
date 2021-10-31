import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.decorator import AcceptedTypes, DecFuncEnum, ReturnRuleAll
from kwhelp import rules
from kwhelp.exceptions import RuleError


class TestReturnRuleAllDecorators(unittest.TestCase):
    def test_return_gen(self):

        @ReturnRuleAll(rules.RuleInt)
        def req_test(*arg):
            return sum(arg)
        result = req_test(2, 4)
        assert result == 6
        result = req_test(-2, -10)
        assert result == - 12
        with self.assertRaises(RuleError):
            result = req_test(2, 2.5)

    def test_return_none(self):
        @ReturnRuleAll(rules.RuleNone)
        def req_test(arg):
            return arg
        result = req_test(arg=None)
        assert result is None
        with self.assertRaises(RuleError):
            result = req_test(arg=self)


class TestReturnRuleAllDecoratorsClass(unittest.TestCase):
    def test_return_gen(self):
        class T:
            @ReturnRuleAll(rules.RuleInt, ftype=DecFuncEnum.METHOD)
            def req_test(self, *arg):
                return sum(arg)
        t = T()
        result = t.req_test(2, 4)
        assert result == 6
        result = t.req_test(-2, -10)
        assert result == -12
        with self.assertRaises(RuleError):
            result = t.req_test(2, 2.5)

    def test_return_static(self):
        class T:
            @staticmethod
            @ReturnRuleAll(rules.RuleInt, ftype=DecFuncEnum.METHOD_STATIC)
            def req_test(*arg):
                return sum(arg)
        result = T.req_test(2, 4)
        assert result == 6
        result = T.req_test(-2, -10)
        assert result == -12
        with self.assertRaises(RuleError):
            result = T.req_test(2, 2.5)

    def test_return_classmethod(self):
        class T:
            @classmethod
            @ReturnRuleAll(rules.RuleInt, ftype=DecFuncEnum.METHOD_STATIC)
            def req_test(cls, *arg):
                return sum(arg)
        result = T.req_test(2, 4)
        assert result == 6
        result = T.req_test(-2, -10)
        assert result == -12
        with self.assertRaises(RuleError):
            result = T.req_test(2, 2.5)

    def test_class_property(self):
        class T:
            @AcceptedTypes((int, float), ftype=DecFuncEnum.METHOD)
            def __init__(self, tmp):
               self._tmp = tmp

            @property
            @ReturnRuleAll(rules.RuleIntPositive, ftype=DecFuncEnum.PROPERTY_CLASS)
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
        t.tmp = 2.5
        # t.tmp accepsts int or float when setting but only int as return
        with self.assertRaises(RuleError):
            result = t.tmp

if __name__ == '__main__':
    unittest.main()
