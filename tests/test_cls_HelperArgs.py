import unittest
from kwhelp import HelperArgs
from kwhelp.helper import NO_THING
import kwhelp.rules as rules


class TestHelperArgs(unittest.TestCase):
    def test_defaults(self):
        args = HelperArgs(key="test")
        self.assertEqual(args.key, "test")
        self.assertFalse(args.match_all_rules)
        self.assertIsNone(args.field)
        self.assertIsInstance(args.types, set)
        self.assertEqual(len(args.types), 0)
        self.assertIs(args.default, NO_THING)
        self.assertIsInstance(args.rules, list)
        self.assertEqual(len(args.rules), 0)
        dic = {'all_rules': False, 'key': 'test', 'require': False}
        self.assertDictEqual(args.to_dict(), dic)

    def test_assign_fields(self):
        rules_list = [rules.RuleInt, rules.RuleStr]
        types_list = [int, float, str]
        
        args = HelperArgs(key="test",
                          field="myfield",
                          require=True,
                          types=types_list,
                          default=11,
                          rules=rules_list,
                          all_rules=True)
        self.assertEqual(args.key, "test")
        self.assertEqual(args.field, "myfield")
        self.assertTrue(args.require)
        self.assertEqual(len(args.types), 3)
        self.assertEqual(args.default, 11)
        self.assertEqual(len(args.rules), 2)
        self.assertTrue(args.match_all_rules)
        args_dic = args.to_dict()
        _rules = args_dic["rules"]
        _types = args_dic["types"]
        self.assertTrue(args_dic['all_rules'])
        self.assertEqual(args_dic['key'], "test")
        self.assertEqual(args_dic['field'], "myfield")
        self.assertTrue(args_dic['require'])
        self.assertEqual(args_dic['default'], 11)
        self.assertEqual(len(_rules), 2)
        self.assertEqual(len(_types), 3)
        for r in rules_list:
            self.assertIn(r, _rules)
        for t in types_list:
            self.assertIn(t, _types)

    def test_constructor_err(self):
        with self.assertRaises(TypeError):
            args = HelperArgs(key=22)
        with self.assertRaises(TypeError):
            args = HelperArgs(key="test", all_rules="True")
        with self.assertRaises(TypeError):
            args = HelperArgs(key="test", field=13)
        with self.assertRaises(TypeError):
            args = HelperArgs(key="test", types=str)
        with self.assertRaises(TypeError):
            args = HelperArgs(key="test", rules=rules.RuleStr)
        with self.assertRaises(TypeError):
            args = HelperArgs(key="test", require="Yes")

    def test_properties(self):
        args = HelperArgs(key="test")
        args.all_rules = False
        self.assertFalse(args.all_rules)
        self.assertFalse(args.match_all_rules)
        with self.assertRaises(TypeError):
            args.match_all_rules = 10
        args.match_all_rules = True
        self.assertTrue(args.all_rules)
        self.assertTrue(args.match_all_rules)
        args.default = 123
        self.assertEqual(args.default, 123)
        args.field = "_field"
        self.assertEqual(args.field, "_field")
        with self.assertRaises(TypeError):
            args.field = 12
        args.field = None
        self.assertIsNone(args.field)
        args.require = True
        self.assertTrue(args.require)
        with self.assertRaises(TypeError):
            args.require = 12
        args.rules = [rules.RuleBool, rules.RuleInt]
        self.assertEqual(len(args.rules), 2)
        with self.assertRaises(TypeError):
            args.rules = rules.RuleBool
        args.types = [str, int, float]
        self.assertEqual(len(args.types), 3)
        with self.assertRaises(TypeError):
            args.types = str
        
