# coding: utf-8
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
import unittest
from inspect import _ParameterKind, signature, isclass, Parameter, Signature
from kwhelp.decorator import _FuncInfo, DecFuncEnum


class Test_FuncInfo(unittest.TestCase):
    def test_args_kwargs(self):
        def foo(*args, **kwargs): pass
        sig = signature(foo)
        info = _FuncInfo(sig=sig, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == 0
        assert info.index_kwargs == 1
        assert len(info.lst_kw_only) == 0
        assert len(info.lst_pos_only) == 0
        assert len(info.lst_pos_or_kw) == 0

    def test_args_only(self):
        def foo(*args): pass
        sig = signature(foo)
        info = _FuncInfo(sig=sig, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == 0
        assert info.index_kwargs == -1
        assert len(info.lst_kw_only) == 0
        assert len(info.lst_pos_only) == 0
        assert len(info.lst_pos_or_kw) == 0
    
    def test_kwargs_only(self):
        def foo(**kwargs): pass
        sig = signature(foo)
        info = _FuncInfo(sig=sig, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == -1
        assert info.index_kwargs == 0
        assert len(info.lst_kw_only) == 0
        assert len(info.lst_pos_only) == 0
        assert len(info.lst_pos_or_kw) == 0
    
    def test_names_only(self):
        def foo(one, two, three, four): pass
        sig = signature(foo)
        info = _FuncInfo(sig=sig, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == -1
        assert info.index_kwargs == -1
        assert len(info.lst_kw_only) == 0
        assert len(info.lst_pos_only) == 0
        self.assertListEqual(info.lst_pos_or_kw, ['one', 'two', 'three', 'four'])
    
    def test_names_kwargs(self):
        def foo(one, two, three, four, **kwargs): pass
        sig = signature(foo)
        info = _FuncInfo(sig=sig, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == -1
        assert info.index_kwargs == 4
        assert len(info.lst_kw_only) == 0
        assert len(info.lst_pos_only) == 0
        self.assertListEqual(info.lst_pos_or_kw, [
                             'one', 'two', 'three', 'four'])

    def test_args_names_kwargs(self):
        def foo(*args, one, two, three, four, **kwargs): pass
        sig = signature(foo)
        info = _FuncInfo(sig=sig, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == 0
        assert info.index_kwargs == 5
        self.assertListEqual(info.lst_kw_only, [
                             'one', 'two', 'three', 'four'])
        assert len(info.lst_pos_only) == 0
        assert len(info.lst_pos_or_kw) == 0

    def test_names_args_names_kwargs(self):
        def foo(neg_two, neg_one, *args, one, two, three, four, **kwargs): pass
        sig = signature(foo)
        info = _FuncInfo(sig=sig, ftype=DecFuncEnum.FUNCTION)
        assert info.index_args == 2
        assert info.index_kwargs == 7
        self.assertListEqual(info.lst_kw_only, [
                             'one', 'two', 'three', 'four'])
        assert len(info.lst_pos_only) == 0
        self.assertListEqual(info.lst_pos_or_kw, [
                             'neg_two', 'neg_one'])

if __name__ == '__main__':
    unittest.main()
