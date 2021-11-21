import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.decorator import AcceptedTypes, DecFuncEnum, ReturnRuleAll
from kwhelp import rules
from kwhelp.exceptions import RuleError
from tests.ex_logger import test_logger, clear_log, get_logged_errors
from tests.ex_log_adapter import LogIndentAdapter

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

    def test_return_opt_return(self):
        @ReturnRuleAll(rules.RuleInt, opt_return=None)
        def req_test(*arg):
            return sum(arg)
        result = req_test(2, 4)
        assert result == 6
        result = req_test(-2, -10)
        assert result == - 12
        result = False
        result = req_test(2, 2.5)
        assert result == None

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

    def test_return_opt_return(self):
        class T:
            @ReturnRuleAll(rules.RuleInt, ftype=DecFuncEnum.METHOD, opt_return=None)
            def req_test(self, *arg):
                return sum(arg)
        t = T()
        result = t.req_test(2, 4)
        assert result == 6
        result = t.req_test(-2, -10)
        assert result == -12
        result = False
        result = t.req_test(2, 2.5)
        assert result == None

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


class TestReturnRuleAllDecoratorsLogger(unittest.TestCase):
    # region setup/teardown
    @classmethod
    def setUpClass(cls):
        cls.log_adapt = LogIndentAdapter(test_logger, {})
        cls.logger = test_logger

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass
    # endregion setup/teardown

    def test_return_gen(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @ReturnRuleAll(rules.RuleInt, opt_logger=log)
            def req_test(*arg):
                return sum(arg)
            with self.assertRaises(RuleError):
                req_test(2, 2.5)
            errors = get_logged_errors()
            assert len(errors) == 1


    def test_return_none(self):
        for i in range(2):
            clear_log()
            if i == 0:
                log = self.logger
            else:
                log = self.log_adapt
            @ReturnRuleAll(rules.RuleNone, opt_logger=log)
            def req_test(arg):
                return arg
            with self.assertRaises(RuleError):
                req_test(arg=self)
            errors = get_logged_errors()
            assert len(errors) == 1


if __name__ == '__main__':
    unittest.main()
