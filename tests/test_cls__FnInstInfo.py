# coding: utf-8
import functools
from inspect import signature, Signature
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import _FnInstInfo, DecFuncEnum

def test_dec(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig = signature(func)
        wrapper.fn_info = _FnInstInfo(func=func, fn_args=args, fn_kwargs=kwargs, sig=sig, ftype=DecFuncEnum.FUNCTION)
        return func(*args, **kwargs)
    wrapper.fn_info = None
    return wrapper

class Test_FuncInfo(unittest.TestCase):
    
    def test_args_kwargs(self):
        @test_dec
        def foo(name, value):
            return name, value
        assert foo.fn_info == None
        result = foo(name='Me', value="awesome")
        assert result[0] == 'Me'
        assert result[1] == 'awesome'
        self.assertIsInstance(foo.fn_info, _FnInstInfo)
        info: _FnInstInfo = foo.fn_info
        assert info.key_word_args['name'] == 'Me'
        assert info.key_word_args['value'] == 'awesome'
        assert info.name == 'foo'
        assert len(info.args) == 0
        assert len(info.kwargs) == 0
        assert info.info.len_kw_only == 0
        assert info.info.len_pos_or_kw == 2
        assert info.info.len_positon_only == 0
        assert info.info.is_args == False
        assert info.info.is_args_only == False
        assert info.info.is_kwargs == False
        assert info.info.is_kwargs_only == False
        assert info.info.is_named_args_only == True
        assert len(info.info.all_keys) == 2
        assert info.info.index_args == -1
        assert info.info.index_kwargs == -1

    def test_args_only(self):
        @test_dec
        def foo(*args):
            return [*args]
        result = foo(1,2,3,4)
        assert result[0] == 1
        info: _FnInstInfo = foo.fn_info
        assert info.name == 'foo'
        self.assertListEqual(info.args, result)
        assert len(info.key_word_args) == 0
        assert len(info.kwargs) == 0
        assert info.info.len_kw_only == 0
        assert info.info.len_pos_or_kw == 0
        assert info.info.len_positon_only == 0
        assert info.info.is_args == True
        assert info.info.is_args_only == True
        assert info.info.is_kwargs == False
        assert info.info.is_kwargs_only == False
        assert info.info.is_named_args_only == False
        assert len(info.info.all_keys) == 0
        assert info.info.index_args == 0
        assert info.info.index_kwargs == -1

    def test_kwargs_only(self):
        @test_dec
        def foo(**kwargs):
            return {**kwargs}
        result = foo(one=1, two=2, three=3, four=4)
        assert result['one'] == 1
        info: _FnInstInfo = foo.fn_info
        assert info.name == 'foo'
        self.assertDictEqual(info.kwargs, result)
        assert len(info.key_word_args) == 0
        assert len(info.args) == 0
        assert len(info.kwargs) == 4
        assert info.info.len_kw_only == 0
        assert info.info.len_pos_or_kw == 0
        assert info.info.len_positon_only == 0
        assert info.info.is_args == False
        assert info.info.is_args_only == False
        assert info.info.is_kwargs == True
        assert info.info.is_kwargs_only == True
        assert info.info.is_named_args_only == False
        assert len(info.info.all_keys) == 0
        assert info.info.index_args == -1
        assert info.info.index_kwargs == 0

    def test_args_names(self):
        @test_dec
        def foo(*args, one, two, three, four=4):
            return [*args] + [("one", one), ("two", two), ('three', three), ('four', four)]
        result = foo(1, 2, 3, 4, two=2, one=1, three=3)
        assert result[0] == 1
        info: _FnInstInfo = foo.fn_info
        assert info.name == 'foo'

if __name__ == '__main__':
    unittest.main()
