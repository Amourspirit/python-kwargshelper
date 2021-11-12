import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import DecFuncEnum, DecArgEnum
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

    def test_DecArgEnum(self):
        e = DecArgEnum.NO_ARGS
        result = DecArgEnum.KWARGS in e
        assert result
        result = DecArgEnum.NAMED_ARGS in e
        assert result
        result = DecArgEnum.ARGS in e
        assert result == False
        result = DecArgEnum.NAMED_ARGS & e
        assert result != 0
        assert result == DecArgEnum.NAMED_ARGS
        self.assertNotEqual(DecArgEnum.KWARGS & e, 0)
        self.assertNotEqual(DecArgEnum.NAMED_ARGS & e, 0)
        e = DecArgEnum.All_ARGS
        result = DecArgEnum.ARGS in e
        assert result == True
        result = DecArgEnum.KWARGS in e
        assert result == True
        result = DecArgEnum.NAMED_ARGS in e
        assert result == True
        assert DecArgEnum.All_ARGS == DecArgEnum.ARGS | DecArgEnum.KWARGS | DecArgEnum.NAMED_ARGS
        assert DecArgEnum.NO_ARGS == DecArgEnum.NAMED_ARGS | DecArgEnum.KWARGS
        # self.assertEqual(DecArgEnum.All_ARGS & e, 0)

if __name__ == '__main__':
    unittest.main()
