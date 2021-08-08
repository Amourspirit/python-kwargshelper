# coding: utf-8
try:
    import path_imports
except:
    pass
import unittest
from src.kwargs_util import AssignBuilder, HelperArgs
import src.kwarg_rules as rules



class TestAssignBuilder(unittest.TestCase):
    def test_build_append(self):
        args = AssignBuilder()
        args.append(key="msg", field='test', types=['str'], require=True)
        args.append(key="age", types=['int'], require=True)
        args.append(key="name", rules=[rules.RuleStr], default="unknown")
        args.append(key="city", types=['str'], rules=[
                    rules.RuleStr], default="North York")
        self.assertEqual(args[0].key, 'msg')
        self.assertSetEqual(args[0].types, set(['str']))
        self.assertTrue(args[0].require)
        self.assertEqual(args[0].field, 'test')
        self.assertListEqual(args[3].rules, [rules.RuleStr])
        self.assertEqual(args[3].default, 'North York')

        self.assertRaises(TypeError, args.append, key=2)
        # empyty or whitespace not ok for key
        self.assertRaises(ValueError, args.append, key=' ')
        self.assertRaises(ValueError, args.append, key='')
        # duplicate, raises error, cannot have the same key twice
        self.assertRaises(ValueError, args.append, key="msg",
                          field='test', types=['str'], require=True)

    def test_build_append_helper(self):
        args = AssignBuilder()
        args.append_helper(HelperArgs(key="msg", field='test',
                           types=['str'], require=True))
        args.append_helper(HelperArgs(key="age", types=['int'], require=True))
        args.append_helper(HelperArgs(key="name", rules=[
                           rules.RuleStr], default="unknown"))
        args.append_helper(HelperArgs(key="city", types=['str'], rules=[
            rules.RuleStr], default="North York"))
        self.assertEqual(args[0].key, 'msg')
        self.assertSetEqual(args[0].types, set(['str']))
        self.assertTrue(args[0].require)
        self.assertEqual(args[0].field, 'test')
        self.assertListEqual(args[3].rules, [rules.RuleStr])
        self.assertEqual(args[3].default, 'North York')

        h = HelperArgs(key="msg", field='_message',
                           types=['str'], require=True)
        args[0] = h
        self.assertEqual(args[0].key, 'msg')
        self.assertEqual(args[0].field, '_message')

        self.assertRaises(ValueError, args.append_helper, h)

        # value error when trying to add existing key
        with self.assertRaises(ValueError):
            args[1] = h

        # type error when trying to assign non HelperArgs
        with self.assertRaises(TypeError):
            args[1] = {"key": 'any'}

        with self.assertRaises(IndexError):
            args[10] = h
        h.key = ''
        self.assertRaises(ValueError, args.append_helper, h)
        self.assertRaises(TypeError, HelperArgs, key="msg",
                          types='str', require=True)
        self.assertRaises(TypeError, args.append_helper, 5)
        self.assertRaises(TypeError, args.append, key=2)
        # empyty or whitespace not ok for key
        self.assertRaises(ValueError, args.append, key=' ')
        self.assertRaises(ValueError, args.append, key='')
        # duplicate, raises error, cannot have the same key twice
        self.assertRaises(ValueError, args.append, key="msg",
                          field='test', types=['str'], require=True)

    def test_builder_append_remove(self):
        args = AssignBuilder()
        args.append(key="msg", types=['str'], require=True)
        args.append(key="age", types=['int'], require=True)
        args.append(key="name", rules=[rules.RuleStr], default="unknown")
        args.append(key="city", types=['str'], rules=[
                    rules.RuleStr], default="North York")
        self.assertTrue(len(args) == 4)
        args.remove(args[2])
        self.assertTrue(len(args) == 3)
        args.remove(args[2])
        self.assertTrue(len(args) == 2)
        args.append(key="city", types=['str'], rules=[
                    rules.RuleStr], default="North York")
        self.assertTrue(len(args) == 3)
        self.assertRaises(TypeError, args.remove, [])
        result = args.remove(None)
        self.assertIsNone(result)

    def test_builder_append_extend(self):
        args = AssignBuilder()
        args.append(key="msg", types=['str'], require=True)
        args.append(key="age", types=['int'], require=True)
        args.append(key="name", rules=[rules.RuleStr], default="unknown")
        args.append(key="city", types=['str'], rules=[
                    rules.RuleStr], default="North York")
        self.assertTrue(len(args) == 4)
        args_ex = AssignBuilder()
        args_ex.append(key="message", types=['str'], require=True)
        args_ex.append(key="limit", types=['int'], require=True)
        self.assertTrue(len(args_ex) == 2)
        args.extend(args_ex)
        self.assertTrue(len(args) == 6)
        self.assertEqual(args[0].key, 'msg')
        self.assertEqual(args[5].key, 'limit')
        # extending with duplicates will ignore all duplicates
        args.extend(args_ex)
        self.assertTrue(len(args) == 6)
        self.assertEqual(args[0].key, 'msg')
        self.assertEqual(args[5].key, 'limit')
        # AssignBuilder can only be extended by other AssignBuilder
        self.assertRaises(NotImplementedError, args.extend, {"key": "test"})


if __name__ == '__main__':
    unittest.main()
