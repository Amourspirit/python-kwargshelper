# coding: utf-8
import functools
from inspect import signature, Signature
from collections import OrderedDict
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import _FnInstInfo, DecFuncEnum, DefaultArgs

FN_INFO = None

def gen_args(length:int) -> list:
    return [i for i in range(length)]

def test_dec(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global FN_INFO
        sig = signature(func)
        FN_INFO = _FnInstInfo(
            func=func, fn_args=args, fn_kwargs=kwargs, sig=sig, ftype=DecFuncEnum.FUNCTION)
        wrapper.fn_info = FN_INFO
        return func(*args, **kwargs)
    wrapper.fn_info = None
    return wrapper


class Test_FuncInfo(unittest.TestCase):

    def test_gen_args(self):
        args = gen_args(3)
        assert args[0] == 0
        assert args[1] == 1
        assert args[2] == 2

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
        result = foo(1, 2, 3, 4)
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

    def test_args_names_with_DefaultArgs(self):
        global FN_INFO

        @test_dec
        def foo(*args, one, two, three, four=4):
            return [*args] + [("one", one), ("two", two), ('three', three), ('four', four)]

        @DefaultArgs(three=3, four=4)
        @test_dec
        def foo_default(*args, one, two, three, four):
            return [*args] + [("one", one), ("two", two), ('three', three), ('four', four)]
        i = 0
        while i < 2:
            if i == 0:
                result = foo(5, 6, 7, 8, two=2, one=1, three=3)
                info: _FnInstInfo = FN_INFO
                assert info.name == 'foo'
            else:
                result = foo_default(5, 6, 7, 8, two=2, one=1)
                info: _FnInstInfo = FN_INFO
                assert info.name == 'foo_default'
            assert result[0] == 5
            od = OrderedDict()
            od['one'] = 1
            od['two'] = 2
            od['three'] = 3
            od['four'] = 4
            self.assertDictEqual(info.key_word_args, od)
            self.assertListEqual(info.args, [5, 6, 7, 8])
            assert len(info.key_word_args) == 4
            assert len(info.args) == 4
            assert len(info.kwargs) == 0
            assert info.info.len_kw_only == 4
            assert info.info.len_pos_or_kw == 0
            assert info.info.len_positon_only == 0
            assert info.info.is_args == True
            assert info.info.is_args_only == False
            assert info.info.is_kwargs == False
            assert info.info.is_kwargs_only == False
            assert info.info.is_named_args_only == False
            assert len(info.info.all_keys) == 4
            assert info.info.index_args == 0
            assert info.info.index_kwargs == -1
            i += 1

    def test_names_kwargs_with_DefaultArgs(self):
        global FN_INFO

        @test_dec
        def foo(start, center, end="!!", **kwargs):
            result = {
                "start": start,
                "center": center,
                "end": end
            }
            result.update(**kwargs)
            return result

        @DefaultArgs(center="_", end="!!", four=4)
        @test_dec
        def foo_default(start, center, end="!!", **kwargs):
            result = {
                "start": start,
                "center": center,
                "end": end
            }
            result.update(**kwargs)
            return result
        i = 0
        while i < 2:
            if i == 0:
                result = foo(start='1st', center="_",
                             one=1, two=2, three=3, four=4)
                info: _FnInstInfo = FN_INFO
                assert info.name == 'foo'
            else:
                result = foo_default(start='1st', one=1, two=2, three=3)
                info: _FnInstInfo = FN_INFO
                assert info.name == 'foo_default'
            assert result['start'] == '1st'
            kwargs = OrderedDict()
            kwargs['one'] = 1
            kwargs['two'] = 2
            kwargs['three'] = 3
            kwargs['four'] = 4
            key_word_args = OrderedDict()
            key_word_args['start'] = '1st'
            key_word_args['center'] = '_'
            key_word_args['end'] = '!!'

            self.assertDictEqual(info.kwargs, kwargs)
            self.assertDictEqual(info.key_word_args, key_word_args)
            assert len(info.key_word_args) == 3
            assert len(info.args) == 0
            assert len(info.kwargs) == 4
            assert info.info.len_kw_only == 0
            assert info.info.len_pos_or_kw == 3
            assert info.info.len_positon_only == 0
            assert info.info.is_args == False
            assert info.info.is_args_only == False
            assert info.info.is_kwargs == True
            assert info.info.is_kwargs_only == False
            assert info.info.is_named_args_only == False
            assert len(info.info.all_keys) == 3
            assert info.info.index_args == -1
            assert info.info.index_kwargs == 3
            i += 1

    def test_args_names_kwargs_with_DefaultArgs(self):
        global FN_INFO

        @test_dec
        def foo(*args, start, center, end="!!", **kwargs):
            result = {
                "args": args,
                "start": start,
                "center": center,
                "end": end
            }
            result.update(**kwargs)
            return result

        @DefaultArgs(center="_", end="!!", four=4)
        @test_dec
        def foo_default(*args, start, center, end="!!", **kwargs):
            result = {
                "args": args,
                "start": start,
                "center": center,
                "end": end
            }
            result.update(**kwargs)
            return result
        i = 0
        while i < 2:
            if i == 0:
                result = foo(101, 102, 103, start='1st', center="_",
                             one=1, two=2, three=3, four=4)
                info: _FnInstInfo = FN_INFO
                assert info.name == 'foo'
            else:
                result = foo_default(
                    101, 102, 103, start='1st', one=1, two=2, three=3)
                info: _FnInstInfo = FN_INFO
                assert info.name == 'foo_default'
            assert result['start'] == '1st'

            kwargs = OrderedDict()
            kwargs['one'] = 1
            kwargs['two'] = 2
            kwargs['three'] = 3
            kwargs['four'] = 4
            key_word_args = OrderedDict()
            key_word_args['start'] = '1st'
            key_word_args['center'] = '_'
            key_word_args['end'] = '!!'
            self.assertDictEqual(info.kwargs, kwargs)
            self.assertDictEqual(info.key_word_args, key_word_args)
            assert len(info.key_word_args) == 3
            assert len(info.args) == 3
            assert len(info.kwargs) == 4
            assert info.info.len_kw_only == 3
            assert info.info.len_pos_or_kw == 0
            assert info.info.len_positon_only == 0
            assert info.info.is_args == True
            assert info.info.is_args_only == False
            assert info.info.is_kwargs == True
            assert info.info.is_kwargs_only == False
            assert info.info.is_named_args_only == False
            assert len(info.info.all_keys) == 3
            assert info.info.index_args == 0
            assert info.info.index_kwargs == 4
            i += 1

    def test_names_args(self):
        @test_dec
        def foo(first, second, *args):
            return [first, second] + [*args]
        result = foo(1, 2, 3, 4)
        assert result[0] == 1
        info: _FnInstInfo = foo.fn_info
        assert info.name == 'foo'
        key_word_args = OrderedDict()
        key_word_args['first'] = 1
        key_word_args['second'] = 2

        self.assertDictEqual(info.key_word_args, key_word_args)
        self.assertListEqual(info.args, [3, 4])
        assert len(info.key_word_args) == 2
        assert len(info.kwargs) == 0
        assert info.info.len_kw_only == 0
        assert info.info.len_pos_or_kw == 2
        assert info.info.len_positon_only == 0
        assert info.info.is_args == True
        assert info.info.is_args_only == False
        assert info.info.is_kwargs == False
        assert info.info.is_kwargs_only == False
        assert info.info.is_named_args_only == False
        assert len(info.info.all_keys) == 2
        assert info.info.index_args == 2
        assert info.info.index_kwargs == -1

    def test_names_args_names(self):
        @test_dec
        def foo(first, second, *args, third, fourth='4th'):
            return [first, second] + [*args] + [third, fourth]
        result = foo(1, 2, 3, 4, third='3rd')
        assert result[0] == 1
        info: _FnInstInfo = foo.fn_info
        assert info.name == 'foo'
        key_word_args = OrderedDict()
        key_word_args['first'] = 1
        key_word_args['second'] = 2
        key_word_args['third'] = '3rd'
        key_word_args['fourth'] = '4th'

        self.assertDictEqual(info.key_word_args, key_word_args)
        self.assertListEqual(info.args, [3, 4])
        self.assertDictEqual(info.info.defauts, {"fourth": "4th"})
        assert len(info.key_word_args) == 4
        assert len(info.kwargs) == 0
        assert info.info.len_kw_only == 2
        assert info.info.len_pos_or_kw == 2
        assert info.info.len_positon_only == 0
        assert info.info.is_args == True
        assert info.info.is_args_only == False
        assert info.info.is_kwargs == False
        assert info.info.is_kwargs_only == False
        assert info.info.is_named_args_only == False
        assert len(info.info.all_keys) == 4
        assert info.info.index_args == 2
        assert info.info.index_kwargs == -1

    def test_names_args_kwargs(self):
        @test_dec
        def foo(first, second, *args, **kwargs):
            return [first, second] + [*args] + [v for _, v in kwargs.items()]
        result = foo(1, 2, 3, 4, third='3rd', fourth='4th', five='5th', six='6th')
        assert result[0] == 1
        info: _FnInstInfo = foo.fn_info
        assert info.name == 'foo'
        key_word_args = OrderedDict()
        key_word_args['first'] = 1
        key_word_args['second'] = 2
        kwargs = OrderedDict()
        kwargs['third'] = '3rd'
        kwargs['fourth'] = '4th'
        kwargs['five'] = '5th'
        kwargs['six'] = '6th'

        self.assertDictEqual(info.key_word_args, key_word_args)
        self.assertDictEqual(info.kwargs, kwargs)
        self.assertListEqual(info.args, [3, 4])
        assert len(info.key_word_args) == 2
        assert len(info.kwargs) == 4
        assert info.info.len_kw_only == 0
        assert info.info.len_pos_or_kw == 2
        assert info.info.len_positon_only == 0
        assert info.info.is_args == True
        assert info.info.is_args_only == False
        assert info.info.is_kwargs == True
        assert info.info.is_kwargs_only == False
        assert info.info.is_named_args_only == False
        assert len(info.info.all_keys) == 2
        assert info.info.index_args == 2
        assert info.info.index_kwargs == 3

    def test_names_args_names_kwargs(self):
        @test_dec
        def foo(first, second, *args, third, fourth='4th', **kwargs):
            return [first, second] + [*args] + [third, fourth] + [v for _,v in kwargs.items()]
        result = foo(1, 2, 3, 4, third='3rd', five='5th', six='6th')
        assert result[0] == 1
        info: _FnInstInfo = foo.fn_info
        assert info.name == 'foo'
        key_word_args = OrderedDict()
        key_word_args['first'] = 1
        key_word_args['second'] = 2
        key_word_args['third'] = '3rd'
        key_word_args['fourth'] = '4th'
        kwargs = OrderedDict()
        kwargs['five'] = '5th'
        kwargs['six'] = '6th'

        self.assertDictEqual(info.key_word_args, key_word_args)
        self.assertDictEqual(info.kwargs, kwargs)
        self.assertListEqual(info.args, [3, 4])
        self.assertDictEqual(info.info.defauts, {"fourth": "4th"})
        assert len(info.key_word_args) == 4
        assert len(info.kwargs) == 2
        assert info.info.len_kw_only == 2
        assert info.info.len_pos_or_kw == 2
        assert info.info.len_positon_only == 0
        assert info.info.is_args == True
        assert info.info.is_args_only == False
        assert info.info.is_kwargs == True
        assert info.info.is_kwargs_only == False
        assert info.info.is_named_args_only == False
        assert len(info.info.all_keys) == 4
        assert info.info.index_args == 2
        assert info.info.index_kwargs == 5


class Test_FuncInfoGets(unittest.TestCase):
    def test_args_kwargs(self):
        @test_dec
        def foo(name, value):
            return name, value
        assert foo.fn_info == None
        result = foo(name='Me', value="awesome")
        assert result[0] == 'Me'
        assert result[1] == 'awesome'
        info: _FnInstInfo = foo.fn_info
        dict = info.get_all_args()
        assert len(dict) == 2
        keys = list(dict.keys())
        assert keys[0] == 'name'
        assert keys[1] == 'value'
        assert dict['name'] == 'Me'
        assert dict['value'] == 'awesome'
        dict = info.get_filter_arg()
        assert len(dict) == 0
        dict = info.get_filter_noargs()
        assert len(dict) == 2
        keys = list(dict.keys())
        assert keys[0] == 'name'
        assert keys[1] == 'value'
        assert dict['name'] == 'Me'
        assert dict['value'] == 'awesome'
        dict = info.get_filtered_key_word_args()
        assert len(dict) == 2
        keys = list(dict.keys())
        assert keys[0] == 'name'
        assert keys[1] == 'value'
        assert dict['name'] == 'Me'
        assert dict['value'] == 'awesome'
        dict = info.get_filtered_kwargs()
        assert len(dict) == 0

    def test_args_only(self):
        def is_match(lst: list, dict: OrderedDict):
            for i in range(len(lst)):
                key = '*' + str(i)
                assert foo_args[i] == dict[key]
        @test_dec
        def foo(*args):
            return [*args]
        args_len = 20
        foo_args = [*gen_args(args_len)]
        result = foo(*foo_args)
        info: _FnInstInfo = foo.fn_info
        dict = info.get_all_args()
        assert len(dict) == args_len
        is_match(foo_args, dict)
        dict = info.get_filter_arg()
        assert len(dict) == args_len
        is_match(foo_args, dict)
        dict = info.get_filtered_key_word_args()
        assert len(dict) == 0
        dict = info.get_filtered_kwargs()
        assert len(dict) == 0


if __name__ == '__main__':
    unittest.main()
