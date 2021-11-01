import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import DecFuncEnum, ReturnRuleAll
from kwhelp import rules

class TestGeneral(unittest.TestCase):

    def test_DecFuncEnum(self):
       assert DecFuncEnum.FUNCTION < DecFuncEnum.METHOD_STATIC
       assert DecFuncEnum.METHOD_STATIC < DecFuncEnum.METHOD
       assert DecFuncEnum.METHOD < DecFuncEnum.METHOD_CLASS
       assert DecFuncEnum.METHOD_CLASS < DecFuncEnum.PROPERTY_CLASS


    def test_str(self):
        self.assertEqual(str(DecFuncEnum.FUNCTION), "FUNCTION")
        self.assertEqual(str(DecFuncEnum.METHOD_STATIC), "METHOD_STATIC")
        self.assertEqual(str(DecFuncEnum.METHOD), "METHOD")
        self.assertEqual(str(DecFuncEnum.METHOD_CLASS), "METHOD_CLASS")
        self.assertEqual(str(DecFuncEnum.PROPERTY_CLASS), "PROPERTY_CLASS")


class Test_DecBase(unittest.TestCase):
    def test_general(self):
        #bad ftype
        with self.assertRaises(TypeError):
            @ReturnRuleAll(rules.RuleInt, ftype=self)
            def fn():
                return 1

    def test_ordianl(self):
        rt = ReturnRuleAll(rules.RuleInt)
        result = rt._get_ordinal(1)
        self.assertEqual(result, "1st")
        result = rt._get_ordinal(2)
        self.assertEqual(result, "2nd")
        result = rt._get_ordinal(4)
        self.assertEqual(result, "4th")
        result = rt._get_ordinal(10)
        self.assertEqual(result, "10th")
        result = rt._get_ordinal(11)
        self.assertEqual(result, "11th")
        result = rt._get_ordinal(22)
        self.assertEqual(result, "22nd")
        result = rt._get_ordinal(33)
        self.assertEqual(result, "33rd")

    def test_get_arg_names(self):
        def foo(one, two, three, **kwargs): pass
        rt = ReturnRuleAll(rules.RuleInt)
        argnames = rt._get_arg_names(foo)
        assert len(argnames) == 3
        assert argnames[0] == "one"
        assert argnames[1] == "two"
        assert argnames[2] == "three"


if __name__ == '__main__':
    unittest.main()
