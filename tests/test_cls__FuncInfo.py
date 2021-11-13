# coding: utf-8
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
import unittest
from kwhelp.decorator import _FuncInfo, DecFuncEnum


class Test_FuncInfo(unittest.TestCase):
    def test_args_kwargs(self):
        def foo(*args, **kwargs): pass
        info = _FuncInfo(func=foo, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == 0
        assert info.index_kwargs == 1
        assert len(info.lst_kw_only) == 0
        assert len(info.lst_pos_only) == 0
        assert len(info.lst_pos_or_kw) == 0
        assert info.is_noargs == True

    def test_args_only(self):
        def foo(*args): pass
        info = _FuncInfo(func=foo, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == 0
        assert info.index_kwargs == -1
        assert len(info.lst_kw_only) == 0
        assert len(info.lst_pos_only) == 0
        assert len(info.lst_pos_or_kw) == 0
        assert info.is_noargs == False
    
    def test_kwargs_only(self):
        def foo(**kwargs): pass
        info = _FuncInfo(func=foo, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == -1
        assert info.index_kwargs == 0
        assert len(info.lst_kw_only) == 0
        assert len(info.lst_pos_only) == 0
        assert len(info.lst_pos_or_kw) == 0
        assert info.is_noargs == True
    
    def test_names_only(self):
        def foo(one, two, three, four): pass
        info = _FuncInfo(func=foo, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == -1
        assert info.index_kwargs == -1
        assert len(info.lst_kw_only) == 0
        assert len(info.lst_pos_only) == 0
        self.assertListEqual(info.lst_pos_or_kw, ['one', 'two', 'three', 'four'])
        assert info.is_noargs == True
    
    def test_names_kwargs(self):
        def foo(one, two, three, four, **kwargs): pass
        info = _FuncInfo(func=foo, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == -1
        assert info.index_kwargs == 4
        assert len(info.lst_kw_only) == 0
        assert len(info.lst_pos_only) == 0
        self.assertListEqual(info.lst_pos_or_kw, [
                             'one', 'two', 'three', 'four'])
        assert info.is_default("one") == False
        assert info.is_noargs == True
    
    def test_names_kwargs_defults(self):
        def foo(one, two, three=3, four=4, **kwargs): pass
        info = _FuncInfo(func=foo, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == -1
        assert info.index_kwargs == 4
        assert len(info.lst_kw_only) == 0
        assert len(info.lst_pos_only) == 0
        self.assertListEqual(info.lst_pos_or_kw, [
                             'one', 'two', 'three', 'four'])
        assert info.is_default("one") == False
        assert info.is_default("two") == False
        assert info.is_default("three") == True
        assert info.is_default("four") == True
        defaults = info._defaults
        assert defaults['three'] == 3
        assert defaults['four'] == 4
        assert info.is_noargs == True

    def test_args_names_kwargs(self):
        def foo(*args, one, two, three, four, **kwargs): pass
        info = _FuncInfo(func=foo, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == 0
        assert info.index_kwargs == 5
        self.assertListEqual(info.lst_kw_only, [
                             'one', 'two', 'three', 'four'])
        assert len(info.lst_pos_only) == 0
        assert len(info.lst_pos_or_kw) == 0
        assert info.is_noargs == True

    def test_names_args_names_kwargs(self):
        def foo(neg_two, neg_one, *args, one, two, three, four, **kwargs): pass
        info = _FuncInfo(func=foo, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == 2
        assert info.index_kwargs == 7
        self.assertListEqual(info.lst_kw_only, [
                             'one', 'two', 'three', 'four'])
        assert len(info.lst_pos_only) == 0
        self.assertListEqual(info.lst_pos_or_kw, [
                             'neg_two', 'neg_one'])
        assert info.is_noargs == True

if __name__ == '__main__':
    unittest.main()
