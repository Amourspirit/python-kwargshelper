import unittest
import kwhelp.rules as rules

class RuleTester(rules.IRule):

    def validate(self) -> bool:
        return True


class TestIRule(unittest.TestCase):
    
    def test_read_write_params(self):
        rt = RuleTester(key="test",
                        name="tests",
                        value=111,
                        raise_errors=False,
                        originator=self)
        self.assertEqual(rt.raise_errors, False)
        self.assertEqual(rt.key, "test")
        self.assertEqual(rt.field_name, "tests")
        self.assertEqual(rt.field_value, 111)
        self.assertFalse(rt.raise_errors)
        self.assertTrue(isinstance(rt.originator, TestIRule))
        
        rt.key = 'mykey'
        rt.field_name = 'fname'
        rt.field_value = 'fvalue'
        rt.raise_errors = True
        self.assertEqual(rt.raise_errors, True)
        self.assertEqual(rt.key, "mykey")
        self.assertEqual(rt.field_name, "fname")
        self.assertEqual(rt.field_value, "fvalue")
        self.assertTrue(rt.raise_errors)


    def test_bad_parm_name(self):
        self.assertRaises(TypeError, RuleTester,
                          key="test",
                          name=2,
                          value=111,
                          raise_errors=False,
                          originator=self
                          )

    def test_bad_parm_key(self):
        self.assertRaises(TypeError, RuleTester,
                          key=10,
                          name="tests",
                          value=111,
                          raise_errors=False,
                          originator=self
                          )

    def test_bad_parm_raise_errors(self):
        self.assertRaises(TypeError, RuleTester,
                          key="test",
                          name="tests",
                          value=111,
                          raise_errors="Yes",
                          originator=self
                          )

    def test_bad_prop_field_name(self):
        rt = RuleTester(key="test",
                        name="tests",
                        value=111,
                        raise_errors=False,
                        originator=self)
        self.assertEqual(rt.field_name, "tests")
        with self.assertRaises(TypeError):
            rt.field_name = 22

    def test_bad_prop_key(self):
        rt = RuleTester(key="test",
                        name="tests",
                        value=111,
                        raise_errors=False,
                        originator=self)
        self.assertEqual(rt.key, "test")
        with self.assertRaises(TypeError):
            rt.key = 22

    def test_bad_prop_raise_errors(self):
        rt = RuleTester(key="test",
                        name="tests",
                        value=111,
                        raise_errors=False,
                        originator=self)
        self.assertEqual(rt.raise_errors, False)
        with self.assertRaises(TypeError):
            rt.raise_errors = 22
