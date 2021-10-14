# coding: utf-8
if __name__ == '__main__':
    import path_imports
import unittest
import kwhelp.rules as rules
from kwhelp import KwArg, ReservedAttributeError, HelperArgs


class TestKwArg(unittest.TestCase):

    def test_assign_hello_world(self):
        #with self.assertWarns(DeprecationWarning):
        kw = KwArg(msg='Hello World')
        kw.kw_assign(key='msg', types=[str], rules=[
                  rules.RuleStrNotNullOrEmpty], require=True)
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 'Hello World')
        self.assertTrue(kw.is_key_existing('msg'))
        self.assertFalse(kw.is_key_existing(' '))
        self.assertFalse(kw.is_key_existing(None))
        self.assertTrue('msg' in kw.kwargs_helper.kw_args)
        
    def test_assign_default_none(self):
        #with self.assertWarns(DeprecationWarning):
        kw = KwArg()
        kw.kw_assign(key='msg', types=[str], default=None)
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertFalse(kw.is_key_existing('msg'))
        self.assertFalse('msg' in kw.kwargs_helper.kw_args)
        self.assertEqual(kw.msg, None)
    
    def test_is_attribute_exist(self):
        kw = KwArg(msg='Hello World')
        kw.kw_assign(key='msg', types=[str], rules=[
                  rules.RuleStrNotNullOrEmpty], require=True)
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 'Hello World')
        self.assertFalse(kw.is_attribute_exist(''))
        self.assertFalse(kw.is_attribute_exist(None))

    def test_assign_not_required(self):
        kw = KwArg()
        kw.kw_assign(key='msg', types=[str], rules=[
                  rules.RuleStrNotNullOrEmpty], require=False)
        self.assertFalse(kw.is_attribute_exist('msg'))
        with self.assertRaises(AttributeError):
            print(kw.msg)

    def test_assign_not_required_default(self):
        kw = KwArg()
        kw.kw_assign(key='msg', types=[str], rules=[
                  rules.RuleStrNotNullOrEmpty], default='Hello World')
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 'Hello World')

    def test_assign_reserved_key_word(self):
        kw = KwArg(kw_assign=True)
        with self.assertRaises(ReservedAttributeError):
            kw.kw_assign(key='kw_assign', types=[bool], require=True)
        kw.kw_assign(key='kw_assign', field='is_assign',
                     types=[bool], require=True)
        self.assertTrue(kw.is_attribute_exist('is_assign'))
        self.assertTrue(kw.is_assign)

    def test_assign_reserved_field_word(self):
        kw = KwArg(needs_help=True)
        with self.assertRaises(ReservedAttributeError):
            kw.kw_assign(key='needs_help', field='kw_assign_helper',
                         types=[bool], require=True)
        kw.kw_assign(key='needs_help', field='requires_helper',
                  types=[bool], require=True)
        self.assertTrue(kw.is_attribute_exist('requires_helper'))
        self.assertTrue(kw.requires_helper)

    def test_assign_rule_pos_int(self):
        kw = KwArg(num=1)
        kw.kw_assign(key='num', types=[int], rules=[
                  rules.RuleIntPositive], require=True)
        self.assertEqual(kw.num, 1)
        
        kw = KwArg(num=-1)
        self.assertRaises(ValueError, kw.kw_assign, key='num', types=[int], rules=[
            rules.RuleIntPositive], require=True)
        
        kw = KwArg(num=-1)
        kw.kwargs_helper.rule_error = False
        result = kw.kw_assign(key='num', types=[int], rules=[
            rules.RuleIntPositive], require=True)
        self.assertFalse(result)
        self.assertFalse(kw.is_attribute_exist('num'))

    def test_assign_int_or_str(self):
        kw = KwArg(msg=2)
        kw.kw_assign(key='msg', types=[str, int], require=True)
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 2)
        
        kw = KwArg()
        kw.kw_assign(key='msg', types=[str, int], default='Hello World')
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 'Hello World')
        
        kw = KwArg(msg=True)
        self.assertRaises(TypeError, kw.kw_assign,  types=[
                          str, int], default='Hello World')
        self.assertFalse(kw.is_attribute_exist('msg'))

    def test_by_method(self):
        def my_method(**kwargs) -> str:
            kw = KwArg(**kwargs)
            kw.kw_assign(key='first', require=True, types=[int])
            kw.kw_assign(key='second', require=True, types=[int])
            kw.kw_assign(key='msg', types=[str], default='Result:', rules=[rules.RuleStrNotNullOrEmpty])
            kw.kw_assign(key='end', types=[str])
            first:int = kw.first
            second:int = kw.second
            msg: str = kw.msg
            _result = first + second
            if kw.is_attribute_exist('end'):
                return_msg = f'{msg} {_result}{kw.end}'
            else:
                return_msg = f'{msg} {_result}'
            return return_msg
        
        result = my_method(first=2, second=3)
        self.assertEqual(result, 'Result: 5')
        result = my_method(first=5, msg='Sum:', second=6)
        self.assertEqual(result, 'Sum: 11')
        result = my_method(first=2, msg='Sum:', second=1, end=', Total.')
        self.assertEqual(result, 'Sum: 3, Total.')
        self.assertRaises(TypeError, my_method, first=5, msg=2, second=6)
        self.assertRaises(TypeError, my_method, first="5", second=6)
        self.assertRaises(ValueError, my_method, msg='Sum:', second=6)

    def test_kw_assign_helper(self):
        kw = KwArg(msg='Hello World')
        kw.kw_assign_helper(HelperArgs(key='msg', types=[str], rules=[
                  rules.RuleStrNotNullOrEmpty], require=True))
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 'Hello World')
        self.assertRaises(TypeError, kw.kw_assign_helper, 'hello')
    
    def test_unused_keys(self):
        kw = KwArg(msg='Hello World', width=12, height=24, length=6)
        kw.kw_assign_helper(HelperArgs(key='msg', types=[str], rules=[
            rules.RuleStrNotNullOrEmpty], require=True))
        self.assertEqual(len(kw.kw_unused_keys), 3)
        self.assertIn('width', kw.kw_unused_keys)
        self.assertIn('height', kw.kw_unused_keys)
        self.assertIn('length', kw.kw_unused_keys)
        
    def test_kw_auto_assign(self):
        kw = KwArg(msg='Hello World', width=12, height=24, length=6)
        kw.kw_auto_assign()
        self.assertEqual(len(kw.kw_unused_keys), 0)
        self.assertEqual(kw.msg, 'Hello World')
        self.assertEqual(kw.length, 6)
        self.assertEqual(kw.width, 12)
        self.assertEqual(kw.height, 24)
        
if __name__ == '__main__':
    unittest.main()
