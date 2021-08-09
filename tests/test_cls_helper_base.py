# coding: utf-8
if __name__ == '__main__':
    import path_imports

import unittest
from kwhelp.helper.base import HelperBase

class MyHelper(HelperBase):
    def __init__(self) -> None:
        super().__init__()


class TestKwArgsHelper(unittest.TestCase):

    def test_get_type_error_method_msg(self):
        mh = MyHelper()
        myvalue = 10
        result = mh._get_type_error_method_msg(
            method_name='test_get_type_error_method_msg', arg=myvalue, arg_name="myvalue", expected_type='str')
        s = f"MyHelper.test_get_type_error_method_msg() arg 'myvalue' is expecting type of 'str'. Got type of '{type(myvalue).__name__}'"
        self.assertEqual(result, s)

    def test_get_value_error_msg(self):
        mh = MyHelper()
        myvalue = 10
        result = mh._get_value_error_msg(
            method_name='test_get_value_error_msg', arg=myvalue, arg_name='myvalue', msg='test')
        s = "MyHelper.test_get_value_error_msg() arg 'myvalue' test"
        self.assertEqual(result, s)

    def test_get_type_error_prop_msg(self):
        prop_name: str = 'mypropety'
        value: object = 10
        expected_type: str = 'str'
        mh = MyHelper()
        result = mh._get_type_error_prop_msg(
            prop_name=prop_name, value=value, expected_type=expected_type)
        s = result = f"MyHelper.{prop_name} is expecting type of '{expected_type}'. Got type of '{type(value).__name__}'"
        self.assertEqual(s, result)

    def test_isinstance_prop(self):
        value: object = 'myvalue'
        prop_name: str = 'myprop'
        prop_type: object = str
        raise_error = False
        mh = MyHelper()
        result = mh._isinstance_prop(
            value=value, prop_name=prop_name, prop_type=prop_type, raise_error=raise_error)
        self.assertTrue(result)
        prop_type = int
        result = mh._isinstance_prop(
            value=value, prop_name=prop_name, prop_type=prop_type, raise_error=raise_error)
        self.assertFalse(result)
        raise_error = True
        self.assertRaises(TypeError, mh._isinstance_prop, value=value,
                          prop_name=prop_name, prop_type=prop_type, raise_error=raise_error)

    def test_prop_error(self):
        prop_name: str = 'myprop'
        value: object = 10
        expected_type: str = 'str'
        mh = MyHelper()
        self.assertRaises(TypeError, mh._prop_error, prop_name=prop_name,
                          value=value, expected_type=expected_type)

    def test_is_prop_str(self):
        value: object = 'myvalue'
        prop_name: str = 'myprop'
        raise_error = False
        mh = MyHelper()
        result = mh._is_prop_str(
            value=value, prop_name=prop_name, raise_error=raise_error)
        self.assertTrue(result)
        value = 10
        result = mh._is_prop_str(
            value=value, prop_name=prop_name, raise_error=raise_error)
        self.assertFalse(result)
        raise_error = True
        self.assertRaises(TypeError, mh._is_prop_str, value=value,
                          prop_name=prop_name, raise_error=raise_error)

    def test_is_prop_bool(self):
        value: object = True
        prop_name: str = 'myprop'
        raise_error = False
        mh = MyHelper()
        result = mh._is_prop_bool(
            value=value, prop_name=prop_name, raise_error=raise_error)
        self.assertTrue(result)
        value = 10
        result = mh._is_prop_bool(
            value=value, prop_name=prop_name, raise_error=raise_error)
        self.assertFalse(result)
        raise_error = True
        self.assertRaises(TypeError, mh._is_prop_bool, value=value,
                          prop_name=prop_name, raise_error=raise_error)

    def test_is_prop_int(self):
        value: object = 10
        prop_name: str = 'myprop'
        raise_error = False
        mh = MyHelper()
        result = mh._is_prop_int(
            value=value, prop_name=prop_name, raise_error=raise_error)
        self.assertTrue(result)
        value = 'test'
        result = mh._is_prop_int(
            value=value, prop_name=prop_name, raise_error=raise_error)
        self.assertFalse(result)
        raise_error = True
        self.assertRaises(TypeError, mh._is_prop_int, value=value,
                          prop_name=prop_name, raise_error=raise_error)

    def test_isinstance_method(self):
        method_name: str = 'test_isinstance_method'
        arg: object = 10
        arg_name: str = 'myarg'
        arg_type: object = int
        raise_error = False
        mh = MyHelper()
        result = mh._isinstance_method(
            method_name=method_name, arg=arg, arg_name=arg_name, arg_type=arg_type, raise_error=raise_error)
        self.assertTrue(result)
        arg = 'hello'
        result = mh._isinstance_method(
            method_name=method_name, arg=arg, arg_name=arg_name, arg_type=arg_type, raise_error=raise_error)
        self.assertFalse(result)
        raise_error = True
        self.assertRaises(TypeError, mh._isinstance_method, method_name=method_name,
                          arg=arg, arg_name=arg_name, arg_type=arg_type, raise_error=raise_error)

    def test_is_arg_str(self):
        method_name: str = 'mymethod'
        arg: object = 'hello'
        arg_name: str = 'arg'
        raise_error = False
        mh = MyHelper()
        result = mh._is_arg_str(
            method_name=method_name, arg=arg, arg_name=arg_name, raise_error=raise_error)
        self.assertTrue(result)
        arg = 10
        result = mh._is_arg_str(
            method_name=method_name, arg=arg, arg_name=arg_name, raise_error=raise_error)
        self.assertFalse(result)
        raise_error = True
        self.assertRaises(TypeError, mh._is_arg_str, method_name=method_name,
                          arg=arg, arg_name=arg_name, raise_error=raise_error)

    def test_is_arg_bool(self):
        method_name: str = 'mymethod'
        arg: object = True
        arg_name: str = 'arg'
        raise_error = False
        mh = MyHelper()
        result = mh._is_arg_bool(
            method_name=method_name, arg=arg, arg_name=arg_name, raise_error=raise_error)
        self.assertTrue(result)
        arg = 10
        result = mh._is_arg_bool(
            method_name=method_name, arg=arg, arg_name=arg_name, raise_error=raise_error)
        self.assertFalse(result)
        raise_error = True
        self.assertRaises(TypeError, mh._is_arg_bool, method_name=method_name,
                          arg=arg, arg_name=arg_name, raise_error=raise_error)

    def test_arg_type_error(self):
        method_name: str = 'mymethod'
        arg: object = 10
        arg_name: str ='arg'
        expected_type: str = 'int'
        mh = MyHelper()
        self.assertRaises(TypeError, mh._arg_type_error,
                          method_name=method_name, arg=arg, arg_name=arg_name, expected_type=expected_type)
        
    def test_get_name_type_obj(self):
        mh = MyHelper()
        obj = 10
        result = mh._get_name_type_obj(obj)
        self.assertEqual(result, 'int')
        obj = int
        self.assertEqual(result, 'int')
        
        obj = ''
        result = mh._get_name_type_obj(obj)
        self.assertEqual(result, 'str')
        obj = str
        self.assertEqual(result, 'str')
        
        obj = mh
        result = mh._get_name_type_obj(obj)
        self.assertEqual(result, 'MyHelper')
        obj = MyHelper
        self.assertEqual(result, 'MyHelper')
        
if __name__ == '__main__':
    unittest.main()
