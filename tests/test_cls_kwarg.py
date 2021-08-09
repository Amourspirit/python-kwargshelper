# coding: utf-8
if __name__ == '__main__':
    import path_imports
import unittest
import kwhelp.rules as rules
from kwhelp import KwArg, ReservedAttributeError, HelperArgs


class TestKwArg(unittest.TestCase):

    def test_assign_hello_world(self):
        kw = KwArg(msg='Hello World')
        kw.assign(key='msg', types=[str], rules=[
                  rules.RuleStrNotNullOrEmpty], require=True)
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 'Hello World')
        self.assertTrue(kw.is_key_existing('msg'))
        self.assertFalse(kw.is_key_existing(' '))
        self.assertFalse(kw.is_key_existing(None))
        self.assertTrue('msg' in kw.kwargs_helper.kw_args)
    
    def test_is_attribute_exist(self):
        kw = KwArg(msg='Hello World')
        kw.assign(key='msg', types=[str], rules=[
                  rules.RuleStrNotNullOrEmpty], require=True)
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 'Hello World')
        self.assertFalse(kw.is_attribute_exist(''))
        self.assertFalse(kw.is_attribute_exist(None))

    def test_assign_not_required(self):
        kw = KwArg()
        kw.assign(key='msg', types=[str], rules=[
                  rules.RuleStrNotNullOrEmpty], require=False)
        self.assertFalse(kw.is_attribute_exist('msg'))
        with self.assertRaises(AttributeError):
            print(kw.msg)

    def test_assign_not_required_default(self):
        kw = KwArg()
        kw.assign(key='msg', types=[str], rules=[
                  rules.RuleStrNotNullOrEmpty], default='Hello World')
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 'Hello World')

    def test_assign_reserved_key_word(self):
        kw = KwArg(assign=True)
        self.assertRaises(ReservedAttributeError, kw.assign,
                          key='assign', types=[bool], require=True)
        kw.assign(key='assign', field='is_assign', types=[bool], require=True)
        self.assertTrue(kw.is_attribute_exist('is_assign'))
        self.assertTrue(kw.is_assign)

    def test_assign_reserved_field_word(self):
        kw = KwArg(needs_help=True)
        self.assertRaises(ReservedAttributeError, kw.assign,
                          key='needs_help', field='assign_helper', types=[bool], require=True)
        kw.assign(key='needs_help', field='requires_helper',
                  types=[bool], require=True)
        self.assertTrue(kw.is_attribute_exist('requires_helper'))
        self.assertTrue(kw.requires_helper)

    def test_assign_rule_pos_int(self):
        kw = KwArg(num=1)
        kw.assign(key='num', types=[int], rules=[
                  rules.RuleIntPositive], require=True)
        self.assertEqual(kw.num, 1)
        
        kw = KwArg(num=-1)
        self.assertRaises(ValueError, kw.assign, key='num', types=[int], rules=[
            rules.RuleIntPositive], require=True)
        
        kw = KwArg(num=-1)
        kw.kwargs_helper.rule_error = False
        result = kw.assign(key='num', types=[int], rules=[
            rules.RuleIntPositive], require=True)
        self.assertFalse(result)
        self.assertFalse(kw.is_attribute_exist('num'))

    def test_assign_int_or_str(self):
        kw = KwArg(msg=2)
        kw.assign(key='msg', types=[str, int], require=True)
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 2)
        
        kw = KwArg()
        kw.assign(key='msg', types=[str, int], default='Hello World')
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 'Hello World')
        
        kw = KwArg(msg=True)
        self.assertRaises(TypeError, kw.assign,  types=[
                          str, int], default='Hello World')
        self.assertFalse(kw.is_attribute_exist('msg'))

    def test_by_method(self):
        def my_method(**kwargs) -> str:
            kw = KwArg(**kwargs)
            kw.assign(key='first', require=True, types=[int])
            kw.assign(key='second', require=True, types=[int])
            kw.assign(key='msg', types=[str], default='Result:', rules=[rules.RuleStrNotNullOrEmpty])
            kw.assign(key='end', types=[str])
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

    def test_assign_helper(self):
        kw = KwArg(msg='Hello World')
        kw.assign_helper(HelperArgs(key='msg', types=[str], rules=[
                  rules.RuleStrNotNullOrEmpty], require=True))
        self.assertTrue(kw.is_attribute_exist('msg'))
        self.assertEqual(kw.msg, 'Hello World')
        self.assertRaises(TypeError, kw.assign_helper, 'hello')
        

if __name__ == '__main__':
    unittest.main()
