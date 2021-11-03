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


if __name__ == '__main__':
    unittest.main()
