import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp import HelperArgs
from kwhelp.helper import NO_THING
import kwhelp.rules as rules


class TestHelperArgs(unittest.TestCase):
    def test_defaults(self):
        args = HelperArgs(key="test")
        self.assertEqual(args.key, "test")
        self.assertIsNone(args.field)
        self.assertIsInstance(args.types, set)
        self.assertEqual(len(args.types), 0)
        self.assertIs(args.default, NO_THING)
        self.assertIsInstance(args.rules_all, list)
        self.assertIsInstance(args.rules_any, list)
        self.assertEqual(len(args.rules_all), 0)
        self.assertEqual(len(args.rules_any), 0)
        dic = {'key': 'test', 'require': False}
        self.assertDictEqual(args.to_dict(), dic)

    def test_assign_fields(self):
        rules_all_list = [rules.RuleInt, rules.RuleStr]
        rules_any_list = [rules.RuleFloatPositive, rules.RuleIntPositive]
        types_list = [int, float, str]
        
        args = HelperArgs(key="test",
                          field="myfield",
                          require=True,
                          types=types_list,
                          default=11,
                          rules_all=rules_all_list,
                          rules_any=rules_any_list)
        self.assertEqual(args.key, "test")
        self.assertEqual(args.field, "myfield")
        self.assertTrue(args.require)
        self.assertEqual(len(args.types), 3)
        self.assertEqual(args.default, 11)
        self.assertEqual(len(args.rules_all), 2)
        args_dic = args.to_dict()
        _rules_all = args_dic["rules_all"]
        _rules_any = args_dic["rules_any"]
        _types = args_dic["types"]
        self.assertEqual(args_dic['key'], "test")
        self.assertEqual(args_dic['field'], "myfield")
        self.assertTrue(args_dic['require'])
        self.assertEqual(args_dic['default'], 11)
        self.assertEqual(len(_rules_all), 2)
        self.assertEqual(len(_types), 3)
        for r_all in rules_all_list:
            self.assertIn(r_all, _rules_all)
        for r_any in rules_any_list:
            self.assertIn(r_any, _rules_any)
        for t in types_list:
            self.assertIn(t, _types)

    def test_constructor_err(self):
        with self.assertRaises(TypeError):
            args = HelperArgs(key=22)
        with self.assertRaises(TypeError):
            args = HelperArgs(key="test", field=13)
        with self.assertRaises(TypeError):
            args = HelperArgs(key="test", types=str)
        with self.assertRaises(TypeError):
            args = HelperArgs(key="test", rules_any=rules.RuleStr)
        with self.assertRaises(TypeError):
            args = HelperArgs(key="test", rules_all=rules.RuleStr)
        with self.assertRaises(TypeError):
            args = HelperArgs(key="test", require="Yes")

    def test_properties(self):
        args = HelperArgs(key="test")
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

        args.rules_all = [rules.RuleBool, rules.RuleInt]
        self.assertEqual(len(args.rules_all), 2)
        with self.assertRaises(TypeError):
            args.rules_all = rules.RuleBool

        args.rules_any = [rules.RuleBool, rules.RuleInt]
        self.assertEqual(len(args.rules_any), 2)
        with self.assertRaises(TypeError):
            args.rules_any = rules.RuleBool

        args.types = [str, int, float]
        self.assertEqual(len(args.types), 3)
        with self.assertRaises(TypeError):
            args.types = str


if __name__ == '__main__':
    unittest.main()
