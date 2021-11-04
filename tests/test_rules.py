from typing import Type
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp import rules

# region Test Helpers
class TestObj:
    
    def __init__(self):
        self.default = None

class TestRule(rules.IRule):
    
    def validate(self) -> bool:
        if self.field_value is not None:
            if self.raise_errors:
                raise ValueError("Expected None")
            return False
        return True
# endregion Test Helpers
class TestRules(unittest.TestCase):
    def setUp(self):
        self.obj = TestObj()
    
    def tearDown(self):
        self.obj = None
    
    def create(self, rule: Type[rules.IRule],k: str = "test",n: str = "default", val: object = None, err: bool = False) -> rules.IRule:
        r = rule(key=k, name=n, value=val, raise_errors=err, originator=self.obj)
        return r

    def test_TestRule(self):
        r = self.create(rule=TestRule)
        self.assertTrue(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(ValueError):
            r.validate()


    # region test IRule
    def test_rule_constructor(self):
        r = TestRule(key="test_key", name="default",value=True,raise_errors=True, originator=self.obj)
        self.assertEqual(r.key, "test_key")
        self.assertEqual(r.field_name, "default")
        self.assertTrue(r.field_value)
        self.assertTrue(r.raise_errors)
        self.assertIs(r.originator, self.obj)
        

        with self.assertRaises(TypeError):
            r = TestRule(key=2, name="default", value=True,
                         raise_errors=True, originator=self.obj)
        with self.assertRaises(TypeError):
            r = TestRule(key="test_key", name=2, value=True,
                         raise_errors=True, originator=self.obj)
        with self.assertRaises(TypeError):
            r = TestRule(key="test_key", name="default", value=True,
                         raise_errors="", originator=self.obj)

    def test_rule_properties(self):
        r = TestRule(key="test_key", name="default", value=True,
                     raise_errors=True, originator=self.obj)

        r.key = "new_key"
        r.field_name = "new_field"
        r.field_value = False
        r.raise_errors = False
        self.assertEqual(r.key, "new_key")
        self.assertEqual(r.field_name, "new_field")
        self.assertFalse(r.field_value)
        self.assertFalse(r.raise_errors)

        with self.assertRaises(TypeError):
            r.key = 2
        with self.assertRaises(TypeError):
            r.field_name = 2
        with self.assertRaises(TypeError):
            r.raise_errors = ""

    # endregion test IRule

    # region Attrib rules
    def test_RuleAttrExist(self):
        r = self.create(rule=rules.RuleAttrExist)
        self.assertTrue(r.validate())
        del self.obj.default
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(AttributeError):
            r.validate()

    def test_RuleAttrNotExist(self):
        r = self.create(rule=rules.RuleAttrNotExist,n="unknown")
        self.assertTrue(r.validate())
        self.obj.unknown = True
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(AttributeError):
            r.validate()

    # endregion Attrib rules

    # region None
    def test_RuleNone(self):
        r = self.create(rule=rules.RuleNone)
        self.assertTrue(r.validate())
        r.field_value = True
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(ValueError):
            r.validate()

    def test_RuleNotNone(self):
        r = self.create(rule=rules.RuleNotNone, val=True)
        self.assertTrue(r.validate())
        r.field_value = None
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(ValueError):
            r.validate()
    # endregion None

    # region Number
    def test_RuleRuleNumber(self):
        r = self.create(rule=rules.RuleNumber, val=10)
        self.assertTrue(r.validate())
        r.field_value = 44.55
        self.assertTrue(r.validate())
        r.field_value = -4.55
        self.assertTrue(r.validate())
        r.field_value = 11
        self.assertTrue(r.validate())
        r.field_value = -11
        self.assertTrue(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
    # endregion Number

    # region Integer
    def test_RuleInt(self):
        r = self.create(rule=rules.RuleInt, val=10)
        self.assertTrue(r.validate())
        r.field_value = 11
        self.assertTrue(r.validate())
        r.field_value = -11
        self.assertTrue(r.validate())
        r.field_value = 44.55
        self.assertFalse(r.validate())
        r.field_value = -4.55
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()

    def test_RuleIntZero(self):
        r = self.create(rule=rules.RuleIntZero, val=0)
        self.assertTrue(r.validate())
        r.field_value = 11
        self.assertFalse(r.validate())
        r.field_value = -11
        self.assertFalse(r.validate())
        r.field_value = 44.55
        self.assertFalse(r.validate())
        r.field_value = -4.55
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
        r.field_value = 10
        with self.assertRaises(ValueError):
            r.validate()

    def test_RuleIntPositive(self):
        r = self.create(rule=rules.RuleIntPositive, val=1)
        self.assertTrue(r.validate())
        r.field_value = 11
        self.assertTrue(r.validate())
        r.field_value = -11
        self.assertFalse(r.validate())
        r.field_value = 44.55
        self.assertFalse(r.validate())
        r.field_value = -4.55
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
        r.field_value = -10
        with self.assertRaises(ValueError):
            r.validate()

    def test_RuleIntNegative(self):
        r = self.create(rule=rules.RuleIntNegative, val=-1)
        self.assertTrue(r.validate())
        r.field_value = -11
        self.assertTrue(r.validate())
        r.field_value = 11
        self.assertFalse(r.validate())
        r.field_value = 44.55
        self.assertFalse(r.validate())
        r.field_value = -4.55
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
        r.field_value = 10
        with self.assertRaises(ValueError):
            r.validate()

    def test_RuleIntNegativeOrZero(self):
        r = self.create(rule=rules.RuleIntNegativeOrZero, val=0)
        self.assertTrue(r.validate())
        r.field_value = -11
        self.assertTrue(r.validate())
        r.field_value = 11
        self.assertFalse(r.validate())
        r.field_value = 44.55
        self.assertFalse(r.validate())
        r.field_value = -4.55
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
        r.field_value = 10
        with self.assertRaises(ValueError):
            r.validate()

    # endregion Integer

    # region Float

    def test_RuleFloat(self):
        r = self.create(rule=rules.RuleFloat, val=0.0)
        self.assertTrue(r.validate())
        r.field_value = 11.5
        self.assertTrue(r.validate())
        r.field_value = -11.5
        self.assertTrue(r.validate())
        r.field_value = 44
        self.assertFalse(r.validate())
        r.field_value = -4
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()

    def test_RuleFloatZero(self):
        r = self.create(rule=rules.RuleFloatZero, val=0.0)
        self.assertTrue(r.validate())
        r.field_value = 11
        self.assertFalse(r.validate())
        r.field_value = -11
        self.assertFalse(r.validate())
        r.field_value = 44.55
        self.assertFalse(r.validate())
        r.field_value = -4.55
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
        r.field_value = 10.3
        with self.assertRaises(ValueError):
            r.validate()

    def test_RuleFloatPositive(self):
        r = self.create(rule=rules.RuleFloatPositive, val=1.2)
        self.assertTrue(r.validate())
        r.field_value = 11.2
        self.assertTrue(r.validate())
        r.field_value = -11.3
        self.assertFalse(r.validate())
        r.field_value = 44
        self.assertFalse(r.validate())
        r.field_value = -4
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
        r.field_value = -10.3
        with self.assertRaises(ValueError):
            r.validate()
    
    def test_RuleFloatNegative(self):
        r = self.create(rule=rules.RuleFloatNegative, val=-1.4)
        self.assertTrue(r.validate())
        r.field_value = -11.5
        self.assertTrue(r.validate())
        r.field_value = 11.2
        self.assertFalse(r.validate())
        r.field_value = 44
        self.assertFalse(r.validate())
        r.field_value = -4
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
        r.field_value = 10.9
        with self.assertRaises(ValueError):
            r.validate()
    
    def test_RuleFloatNegativeOrZero(self):
        r = self.create(rule=rules.RuleFloatNegativeOrZero, val=0.0)
        self.assertTrue(r.validate())
        r.field_value = -11.33
        self.assertTrue(r.validate())
        r.field_value = 11.24
        self.assertFalse(r.validate())
        r.field_value = 44
        self.assertFalse(r.validate())
        r.field_value = -4
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
        r.field_value = 10.001
        with self.assertRaises(ValueError):
            r.validate()
    
    # endregion Float

    # region String
    def test_RuleStr(self):
        r = self.create(rule=rules.RuleStr, val="hello")
        self.assertTrue(r.validate())
        r.field_value = ""
        self.assertTrue(r.validate())
        r.field_value = " "
        self.assertTrue(r.validate())
        r.field_value = -11
        self.assertFalse(r.validate())
        r.field_value = 44.55
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()

    def test_RuleStrEmpty(self):
        r = self.create(rule=rules.RuleStrEmpty, val="")
        self.assertTrue(r.validate())
        r.field_value = "hello"
        self.assertFalse(r.validate())
        r.field_value = " "
        self.assertFalse(r.validate())
        r.field_value = 2
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
        r.field_value = " "
        with self.assertRaises(ValueError):
            r.validate()

    def test_RuleStrNotNullOrEmpty(self):
        r = self.create(rule=rules.RuleStrNotNullOrEmpty, val="hello")
        self.assertTrue(r.validate())
        r.field_value = " "
        self.assertTrue(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = 2
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
        r.field_value = ""
        with self.assertRaises(ValueError):
            r.validate()

    def test_RuleStrNotNullEmptyWs(self):
        r = self.create(rule=rules.RuleStrNotNullEmptyWs, val="hello")
        self.assertTrue(r.validate())
        r.field_value = "  hello "
        self.assertTrue(r.validate())
        r.field_value = " "
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = 2
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
        r.field_value = ""
        with self.assertRaises(ValueError):
            r.validate()
        r.field_value = " "
        with self.assertRaises(ValueError):
            r.validate()
    # endregion String

    # region bool
    def test_RuleBool(self):
        r = self.create(rule=rules.RuleBool, val=True)
        self.assertTrue(r.validate())
        r.field_value = False
        self.assertTrue(r.validate())
        r.field_value = 1
        self.assertFalse(r.validate())
        r.field_value = 44.55
        self.assertFalse(r.validate())
        r.field_value = -4.55
        self.assertFalse(r.validate())
        r.field_value = ""
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()

    # endregion bool

    #region Byte
    def test_RuleByteUnsigned(self):
        class Foo:
            pass
        f = Foo()
        rule = rules.RuleByteUnsigned(
            key="tesst",
            name="irule",
            value=22,
            raise_errors=True,
            originator=f
        )
        rule.validate()
        rule.field_value = -1
        with self.assertRaises(ValueError):
            rule.validate()
        rule.field_value = 1.3
        with self.assertRaises(TypeError):
            rule.validate()
        rule.field_value = 256
        rule.raise_errors = False
        assert rule.validate() == False
        rule.field_value = 1.3
        assert rule.validate() == False

    def test_RuleByteSigned(self):
        class Foo:
            pass
        f = Foo()
        rule = rules.RuleByteSigned(
            key="tesst",
            name="irule",
            value=22,
            raise_errors=True,
            originator=f
        )
        rule.validate()
        rule.field_value = -129
        with self.assertRaises(ValueError):
            rule.validate()
        rule.field_value = 1.3
        with self.assertRaises(TypeError):
            rule.validate()
        rule.field_value = 128
        rule.raise_errors = False
        assert rule.validate() == False
        rule.field_value = 1.3
        assert rule.validate() == False
    # endregion byte

    # region Iterable
    def test_RuleIterable(self):
        r = self.create(rule=rules.RuleIterable, val=[0, 1])
        self.assertTrue(r.validate())
        r.field_value = (1, 2)
        self.assertTrue(r.validate())
        r.field_value = set([1, 2])
        self.assertTrue(r.validate())
        r.field_value = 44
        self.assertFalse(r.validate())
        r.field_value = ""
        self.assertFalse(r.validate())
        r.field_value = False
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()

    def test_RuleNotIterable(self):
        r = self.create(rule=rules.RuleNotIterable, val=1)
        self.assertTrue(r.validate())
        r.field_value = (1, 2)
        self.assertFalse(r.validate())
        r.field_value = 44
        self.assertTrue(r.validate())
        r.field_value = ""
        self.assertTrue(r.validate())
        r.field_value = False
        self.assertTrue(r.validate())
        r.field_value = set([1, 2])
        self.assertFalse(r.validate())
        r.raise_errors = True
        with self.assertRaises(TypeError):
            r.validate()
    # endregion Iterable



if __name__ == '__main__':
    unittest.main()
