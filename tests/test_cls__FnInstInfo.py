# coding: utf-8
import functools
from inspect import signature
from collections import OrderedDict
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import _FnInstInfo, _FuncInfo, DecFuncEnum, DefaultArgs

FN_INFO = None


def gen_args(length: int) -> list:
    return [i for i in range(length)]


def test_dec(func):
    global FN_INFO
    FN_INFO = None
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global FN_INFO
        finfo = _FuncInfo(func=func, ftype=DecFuncEnum.FUNCTION)
        FN_INFO = _FnInstInfo(fninfo=finfo, fn_args=args, fn_kwargs=kwargs)
        wrapper.fn_info = FN_INFO
        return func(*args, **kwargs)
    wrapper.fn_info = None
    return wrapper


def test_dec_cls(func):
    global FN_INFO
    FN_INFO = None
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global FN_INFO
        finfo = _FuncInfo(func=func, ftype=DecFuncEnum.METHOD)
        FN_INFO = _FnInstInfo(fninfo=finfo, fn_args=args, fn_kwargs=kwargs)
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

    def test_names_only(self):
        @test_dec
        def foo(name, value):
            return name, value
        assert foo.fn_info == None
        od_key_word_args = OrderedDict()
        od_key_word_args['name'] = 'Me'
        od_key_word_args['value'] = 'awesome'
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
        self.assertDictEqual(od_key_word_args, info.key_word_args)
        
        # test positional with names
        
        result = foo('Me', "awesome")
        assert result[0] == 'Me'
        assert result[1] == 'awesome'
        info: _FnInstInfo = foo.fn_info
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
        self.assertDictEqual(od_key_word_args, info.key_word_args)

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
        result = foo(1, 2, 3, 4, third='3rd',
                     fourth='4th', five='5th', six='6th')
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
            return [first, second] + [*args] + [third, fourth] + [v for _, v in kwargs.items()]
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
    def test_name_only(self):
        @test_dec
        def foo(name, value):
            return name, value
        assert foo.fn_info == None
        od_key_word_args = OrderedDict()
        od_key_word_args['name'] = 'Me'
        od_key_word_args['value'] = 'awesome'
        result = foo(name='Me', value="awesome")
        assert result[0] == 'Me'
        assert result[1] == 'awesome'
        # run twice for cache test
        for _ in range(2):
            info: _FnInstInfo = foo.fn_info
            self.assertDictEqual(od_key_word_args, info.key_word_args)
            d = info.get_all_args()
            self.assertDictEqual(od_key_word_args, d)
            d = info.get_filter_arg()
            assert len(d) == 0
            d = info.get_filter_noargs()
            assert len(d) == 2
            keys = list(d.keys())
            assert keys[0] == 'name'
            assert keys[1] == 'value'
            assert d['name'] == 'Me'
            assert d['value'] == 'awesome'
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(od_key_word_args, d)
            d = info.get_filtered_kwargs()
            assert len(d) == 0
            # test positional
            result = foo('Me', "awesome")
            assert result[0] == 'Me'
            assert result[1] == 'awesome'
            info: _FnInstInfo = foo.fn_info
            self.assertDictEqual(od_key_word_args, info.key_word_args)
            d = info.get_all_args()
            self.assertDictEqual(od_key_word_args, d)
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(od_key_word_args, d)

    def test_names_optional_args(self):
        @test_dec
        def foo(name, value, one=1, two=2):
            return (name, value, one, two)
        assert foo.fn_info == None
        od_key_word_args = OrderedDict()
        od_key_word_args['name'] = 'Me'
        od_key_word_args['value'] = 'awesome'
        od_key_word_args['one'] = 1
        od_key_word_args['two'] = 2
        result = foo(name='Me', value="awesome")
        assert result[0] == 'Me'
        assert result[1] == 'awesome'
        assert result[2] == 1
        assert result[3] == 2
        # run twice for cache test
        for _ in range(2):
            info: _FnInstInfo = foo.fn_info
            self.assertDictEqual(od_key_word_args, info.key_word_args)
            d = info.get_all_args()
            self.assertDictEqual(od_key_word_args, d)
            d = info.get_filter_arg()
            assert len(d) == 0
            d = info.get_filter_noargs()
            self.assertDictEqual(od_key_word_args, d)
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(od_key_word_args, d)
            d = info.get_filtered_kwargs()
            assert len(d) == 0
            # test positional
            result = foo('Me', "awesome")
            assert result[0] == 'Me'
            assert result[1] == 'awesome'
            info: _FnInstInfo = foo.fn_info
            self.assertDictEqual(od_key_word_args, info.key_word_args)
            d = info.get_all_args()
            self.assertDictEqual(od_key_word_args, d)
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(od_key_word_args, d)

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
        # run twice for cache test
        for _ in range(2):
            info: _FnInstInfo = foo.fn_info
            d = info.get_all_args()
            assert len(d) == args_len
            is_match(foo_args, d)
            d = info.get_filter_arg()
            assert len(d) == args_len
            is_match(foo_args, d)
            d = info.get_filtered_key_word_args()
            assert len(d) == 0
            d = info.get_filtered_kwargs()
            assert len(d) == 0
            d = info.get_filter_noargs()
            assert len(d) == 0


    def test_kwargs_only(self):
        @test_dec
        def foo(**kwargs):
            return {**kwargs}
        od = OrderedDict()
        od['one'] = 1
        od['two'] = 2
        od['three'] = 3
        od['four'] = 3
        result = foo(**od)
        assert result['one'] == 1
        info: _FnInstInfo = foo.fn_info
        # run twice for cache test
        for _ in range(2):
            d = info.get_all_args()
            assert len(d) == 4
            self.assertDictEqual(od, d)
            d = info.get_filter_arg()
            assert len(d) == 0
            d = info.get_filtered_key_word_args()
            assert len(d) == 0
            d = info.get_filtered_kwargs()
            self.assertDictEqual(od, d)
            d = info.get_filter_noargs()
            self.assertDictEqual(od, d)

    def test_args_names(self):
        @test_dec
        def foo(*args, one, two, three, four=4):
            return [*args] + [("one", one), ("two", two), ('three', three), ('four', four)]
        args_lst = [5, 6, 7, 8]
        key_word_args = OrderedDict()
        key_word_args['one'] = 1
        key_word_args['two'] = 2
        key_word_args['three'] = 3
        key_word_args['four'] = 4
        od_all = OrderedDict()
        od_args = OrderedDict()
        for i, arg in enumerate(args_lst):
            key = '*' + str(i)
            od_all[key] = arg
            od_args[key] = arg
        od_all.update(key_word_args)
        od_noargs = OrderedDict(key_word_args)
        result = foo(*args_lst, **key_word_args)
        info: _FnInstInfo = foo.fn_info
        # run twice for cache test
        for _ in range(2):
            d = info.get_all_args()
            self.assertDictEqual(od_all, d)
            d = info.get_filter_arg()
            self.assertDictEqual(od_args, d)
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(key_word_args, d)
            d = info.get_filtered_kwargs()
            assert len(d) == 0
            d = info.get_filter_noargs()
            self.assertDictEqual(od_noargs, d)

    def test_names_kwargs(self):
        @test_dec
        def foo(start, center, end="!!", **kwargs):
            result = {
                "start": start,
                "center": center,
                "end": end
            }
            result.update(**kwargs)
            return result
        kwargs = OrderedDict()
        kwargs['one'] = 1
        kwargs['two'] = 2
        kwargs['three'] = 3
        kwargs['four'] = 4
        key_word_args = OrderedDict()
        key_word_args['start'] = '1st'
        key_word_args['center'] = '_'
        key_word_args['end'] = '!!'
        od_all = OrderedDict(key_word_args)
        od_all.update(kwargs)
        od_noargs = OrderedDict(key_word_args)
        od_noargs.update(kwargs)
        result = foo(start='1st', center="_",
                     one=1, two=2, three=3, four=4)
        info: _FnInstInfo = foo.fn_info
        # run twice for cache test
        for _ in range(2):
            d = info.get_all_args()
            self.assertDictEqual(od_all, d)
            d = info.get_filter_arg()
            assert len(d) == 0
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(key_word_args, d)
            d = info.get_filtered_kwargs()
            self.assertDictEqual(kwargs, d)
            d = info.get_filter_noargs()
            self.assertDictEqual(od_noargs, d)
        
        def bar(start, center, end="!!", **kwargs):
            result = {
                "start": start,
                "center": center,
                "end": end
            }
            result.update(**kwargs)
            return result
        # test positional
        result = bar('1st', "_", one=1, two=2, three=3, four=4)
        assert result['start'] == '1st'
        assert result['center'] == '_'
        assert result['end'] == '!!'
        assert result['one'] == 1
        assert result['two'] == 2
        assert result['three'] == 3
        assert result['four'] == 4
   
        result = foo('1st', "_", one=1, two=2, three=3, four=4)
        info: _FnInstInfo = foo.fn_info
        # run twice for cache test
        for _ in range(2):
            d = info.get_all_args()
            self.assertDictEqual(od_all, d)
            d = info.get_filter_arg()
            assert len(d) == 0
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(key_word_args, d)
            d = info.get_filtered_kwargs()
            self.assertDictEqual(kwargs, d)
            d = info.get_filter_noargs()
            self.assertDictEqual(od_noargs, d)
   

    def test_args_names_kwargs(self):
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
        args_lst = [101, 102, 103]
        kwargs = OrderedDict()
        kwargs['one'] = 1
        kwargs['two'] = 2
        kwargs['three'] = 3
        kwargs['four'] = 4
        key_word_args = OrderedDict()
        key_word_args['start'] = '1st'
        key_word_args['center'] = '_'
        key_word_args['end'] = '!!'
        od_args = OrderedDict()
        od_all = OrderedDict()

        for i, arg in enumerate(args_lst):
            key = '*' + str(i)
            od_all[key] = arg
            od_args[key] = arg
        od_all.update(key_word_args)
        od_all.update(kwargs)
        od_noargs = OrderedDict(key_word_args)
        od_noargs.update(kwargs)

        result = foo(*args_lst, start='1st', center="_",
                     one=1, two=2, three=3, four=4)
        info: _FnInstInfo = foo.fn_info
        # run twice for cache test
        for _ in range(2):
            d = info.get_all_args()
            self.assertDictEqual(od_all, d)
            d = info.get_filter_arg()
            self.assertDictEqual(od_args, d)
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(key_word_args, d)
            d = info.get_filtered_kwargs()
            self.assertDictEqual(kwargs, d)
            d = info.get_filter_noargs()
            self.assertDictEqual(od_noargs, d)

    def test_names_args(self):
        @test_dec
        def foo(first, second, *args):
            return [first, second] + [*args]
    
        args_lst = [3, 4]
        od_pre = OrderedDict()
        od_pre['first'] = 1
        od_pre['second'] = 2
        od_args = OrderedDict()
        od_all = OrderedDict(od_pre)
        pre_ofset = len(od_pre)
        for i, arg in enumerate(args_lst):
            key = '*' + str(i + pre_ofset)
            od_all[key] = arg
            od_args[key] = arg
        od_noargs = OrderedDict(od_pre)
        result = foo(1, 2, *args_lst)
        info: _FnInstInfo = foo.fn_info
        # run twice for cache test
        for _ in range(2):
            d = info.get_all_args()
            self.assertDictEqual(od_all, d)
            d = info.get_filter_arg()
            self.assertDictEqual(od_args, d)
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(od_pre, d)
            d = info.get_filtered_kwargs()
            assert len(d) == 0
            d = info.get_filter_noargs()
            self.assertDictEqual(od_noargs, d)

    def test_names_args_names(self):
        @test_dec
        def foo(first, second, *args, third, fourth='4th'):
            return [first, second] + [*args] + [third, fourth]
        
        args_lst = [3, 4]
        od_pre = OrderedDict()
        od_pre['first'] = 1
        od_pre['second'] = 2
        key_word_args = OrderedDict()
        key_word_args['third'] = '3rd'
        key_word_args['fourth'] = '4th'
        od_args = OrderedDict()
        od_all = OrderedDict(od_pre)
        pre_ofset = len(od_pre)
        for i, arg in enumerate(args_lst):
            key = '*' + str(i + pre_ofset)
            od_all[key] = arg
            od_args[key] = arg
        od_all.update(key_word_args)
        od_noargs = OrderedDict(od_pre)
        od_noargs.update(key_word_args)
        od_all_kw = OrderedDict(od_pre)
        od_all_kw.update(key_word_args)
        result = foo(1, 2, 3, 4, third='3rd')
        assert result[0] == 1
        info: _FnInstInfo = foo.fn_info
        # run twice for cache test
        for _ in range(2):
            d = info.get_all_args()
            self.assertDictEqual(od_all, d)
            d = info.get_filter_arg()
            self.assertDictEqual(od_args, d)
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(od_all_kw, d)
            d = info.get_filtered_kwargs()
            assert len(d) == 0
            d = info.get_filter_noargs()
            self.assertDictEqual(od_noargs, d)

    def test_names_args_kwargs(self):
        @test_dec
        def foo(first, second, *args, **kwargs):
            return [first, second] + [*args] + [v for _, v in kwargs.items()]
        
        args_lst = [3, 4]
        od_pre = OrderedDict()
        od_pre['first'] = 1
        od_pre['second'] = 2
        kwargs = OrderedDict()
        kwargs['third'] = '3rd'
        kwargs['fourth'] = '4th'
        kwargs['five'] = '5th'
        kwargs['six'] = '6th'
        od_args = OrderedDict()
        od_all = OrderedDict(od_pre)
        pre_ofset = len(od_pre)
        for i, arg in enumerate(args_lst):
            key = '*' + str(i + pre_ofset)
            od_all[key] = arg
            od_args[key] = arg
        od_all.update(kwargs)
        od_noargs = OrderedDict(od_pre)
        od_noargs.update(kwargs)
        result = foo(1, 2, 3, 4, third='3rd',
                     fourth='4th', five='5th', six='6th')
        assert result[0] == 1
        info: _FnInstInfo = foo.fn_info
        # run twice for cache test
        for _ in range(2):
            d = info.get_all_args()
            self.assertDictEqual(od_all, d)
            d = info.get_filter_arg()
            self.assertDictEqual(od_args, d)
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(od_pre, d)
            d = info.get_filtered_kwargs()
            self.assertDictEqual(kwargs, d)

    def test_names_args_names_kwargs(self):
        @test_dec
        def foo(first, second, *args, third, fourth='4th', **kwargs):
            return [first, second] + [*args] + [third, fourth] + [v for _, v in kwargs.items()]
        
        args_lst = [3, 4]
        od_pre = OrderedDict()
        od_pre['first'] = 1
        od_pre['second'] = 2
        key_word_args = OrderedDict()
        key_word_args['third'] = '3rd'
        key_word_args['fourth'] = '4th'
        kwargs = OrderedDict()
        kwargs['five'] = '5th'
        kwargs['six'] = '6th'
        od_args = OrderedDict()
        od_all = OrderedDict(od_pre)
        pre_ofset = len(od_pre)
        for i, arg in enumerate(args_lst):
            key = '*' + str(i + pre_ofset)
            od_all[key] = arg
            od_args[key] = arg
        od_all.update(key_word_args)
        od_all.update(kwargs)
        od_noargs = OrderedDict(od_pre)
        od_noargs.update(key_word_args)
        od_noargs.update(kwargs)
        od_all_kw = OrderedDict(od_pre)
        od_all_kw.update(key_word_args)
    
        result = foo(1, 2, 3, 4, third='3rd', five='5th', six='6th')
        assert result[0] == 1
        info: _FnInstInfo = foo.fn_info
        assert info.name == 'foo'
        # run twice for cache test
        for _ in range(2):
            d = info.get_all_args()
            self.assertDictEqual(od_all, d)
            d = info.get_filter_arg()
            self.assertDictEqual(od_args, d)
            d = info.get_filtered_key_word_args()
            self.assertDictEqual(od_all_kw, d)
            d = info.get_filtered_kwargs()
            self.assertDictEqual(kwargs, d)
            d = info.get_filter_noargs()
            self.assertDictEqual(od_noargs, d)


class Test_FuncInfoGetsClass(unittest.TestCase):
    def test_args_kwargs(self):
        global FN_INFO
        class Runner:
            @test_dec_cls
            def foo(self, name, value):
                return name, value
        r = Runner()
        result = r.foo(name='Me', value="awesome")
        info: _FnInstInfo = FN_INFO
        # run twice for cache test
        for _ in range(2):
            assert result[0] == 'Me'
            assert result[1] == 'awesome'
            d = info.get_all_args()
            assert len(d) == 2
            keys = list(d.keys())
            assert keys[0] == 'name'
            assert keys[1] == 'value'
            assert d['name'] == 'Me'
            assert d['value'] == 'awesome'
            d = info.get_filter_arg()
            assert len(d) == 0
            d = info.get_filter_noargs()
            assert len(d) == 2
            keys = list(d.keys())
            assert keys[0] == 'name'
            assert keys[1] == 'value'
            assert d['name'] == 'Me'
            assert d['value'] == 'awesome'
            d = info.get_filtered_key_word_args()
            assert len(d) == 2
            keys = list(d.keys())
            assert keys[0] == 'name'
            assert keys[1] == 'value'
            assert d['name'] == 'Me'
            assert d['value'] == 'awesome'
            d = info.get_filtered_kwargs()
            assert len(d) == 0

    def test_args_only(self):
        global FN_INFO
        def is_match(lst: list, dict: OrderedDict):
            for i in range(len(lst)):
                key = '*' + str(i)
                assert foo_args[i] == dict[key]
        class Runner:
            @test_dec_cls
            def foo(self, *args):
                return [*args]
        r = Runner()
        args_len = 20
        foo_args = [*gen_args(args_len)]
        result = r.foo(*foo_args)
        info: _FnInstInfo = FN_INFO
        # run twice for cache test
        for _ in range(2):
            d = info.get_all_args()
            assert len(d) == args_len
            is_match(foo_args, d)
            d = info.get_filter_arg()
            assert len(d) == args_len
            is_match(foo_args, d)
            d = info.get_filtered_key_word_args()
            assert len(d) == 0
            d = info.get_filtered_kwargs()
            assert len(d) == 0
            d = info.get_filter_noargs()
            assert len(d) == 0

    def test_kwargs_only(self):
        class Runner:
            @test_dec_cls
            def foo(self, **kwargs):
                return {**kwargs}
        od = OrderedDict()
        od['one'] = 1
        od['two'] = 2
        od['three'] = 3
        od['four'] = 3
        r = Runner()
        result = r.foo(**od)
        assert result['one'] == 1
        info: _FnInstInfo = Runner.foo.fn_info
        d = info.get_all_args()
        assert len(d) == 4
        self.assertDictEqual(od, d)
        d = info.get_filter_arg()
        assert len(d) == 0
        d = info.get_filtered_key_word_args()
        assert len(d) == 0
        d = info.get_filtered_kwargs()
        self.assertDictEqual(od, d)
        d = info.get_filter_noargs()
        self.assertDictEqual(od, d)

    def test_args_names(self):
        class Runner:
            @test_dec_cls
            def foo(self, *args, one, two, three, four=4):
                return [*args] + [("one", one), ("two", two), ('three', three), ('four', four)]
        args_lst = [5, 6, 7, 8]
        key_word_args = OrderedDict()
        key_word_args['one'] = 1
        key_word_args['two'] = 2
        key_word_args['three'] = 3
        key_word_args['four'] = 4
        od_all = OrderedDict()
        od_args = OrderedDict()
        for i, arg in enumerate(args_lst):
            key = '*' + str(i)
            od_all[key] = arg
            od_args[key] = arg
        od_all.update(key_word_args)
        od_noargs = OrderedDict(key_word_args)
        r = Runner()
        result = r.foo(*args_lst, **key_word_args)
        info: _FnInstInfo = Runner.foo.fn_info
        d = info.get_all_args()
        self.assertDictEqual(od_all, d)
        d = info.get_filter_arg()
        self.assertDictEqual(od_args, d)
        d = info.get_filtered_key_word_args()
        self.assertDictEqual(key_word_args, d)
        d = info.get_filtered_kwargs()
        assert len(d) == 0
        d = info.get_filter_noargs()
        self.assertDictEqual(od_noargs, d)

    def test_names_kwargs(self):
        class Runner:
            @test_dec_cls
            def foo(self, start, center, end="!!", **kwargs):
                result = {
                    "start": start,
                    "center": center,
                    "end": end
                }
                result.update(**kwargs)
                return result
        kwargs = OrderedDict()
        kwargs['one'] = 1
        kwargs['two'] = 2
        kwargs['three'] = 3
        kwargs['four'] = 4
        key_word_args = OrderedDict()
        key_word_args['start'] = '1st'
        key_word_args['center'] = '_'
        key_word_args['end'] = '!!'
        od_all = OrderedDict(key_word_args)
        od_all.update(kwargs)
        od_noargs = OrderedDict(key_word_args)
        od_noargs.update(kwargs)
        r = Runner()
        result = r.foo(start='1st', center="_",
                     one=1, two=2, three=3, four=4)
        info: _FnInstInfo = Runner.foo.fn_info
        d = info.get_all_args()
        self.assertDictEqual(od_all, d)
        d = info.get_filter_arg()
        assert len(d) == 0
        d = info.get_filtered_key_word_args()
        self.assertDictEqual(key_word_args, d)
        d = info.get_filtered_kwargs()
        self.assertDictEqual(kwargs, d)
        d = info.get_filter_noargs()
        self.assertDictEqual(od_noargs, d)


        result = r.foo('1st', "_", one=1, two=2, three=3, four=4)
        info: _FnInstInfo = Runner.foo.fn_info
        d = info.get_all_args()
        self.assertDictEqual(od_all, d)
        d = info.get_filter_arg()
        assert len(d) == 0
        d = info.get_filtered_key_word_args()
        self.assertDictEqual(key_word_args, d)
        d = info.get_filtered_kwargs()
        self.assertDictEqual(kwargs, d)
        d = info.get_filter_noargs()
        self.assertDictEqual(od_noargs, d)

    def test_args_names_kwargs(self):
        class Runner:
            @test_dec_cls
            def foo(self, *args, start, center, end="!!", **kwargs):
                result = {
                    "args": args,
                    "start": start,
                    "center": center,
                    "end": end
                }
                result.update(**kwargs)
                return result
        args_lst = [101, 102, 103]
        kwargs = OrderedDict()
        kwargs['one'] = 1
        kwargs['two'] = 2
        kwargs['three'] = 3
        kwargs['four'] = 4
        key_word_args = OrderedDict()
        key_word_args['start'] = '1st'
        key_word_args['center'] = '_'
        key_word_args['end'] = '!!'
        od_args = OrderedDict()
        od_all = OrderedDict()

        for i, arg in enumerate(args_lst):
            key = '*' + str(i)
            od_all[key] = arg
            od_args[key] = arg
        od_all.update(key_word_args)
        od_all.update(kwargs)
        od_noargs = OrderedDict(key_word_args)
        od_noargs.update(kwargs)
        r = Runner()
        result = r.foo(*args_lst, start='1st', center="_",
                     one=1, two=2, three=3, four=4)
        info: _FnInstInfo = Runner.foo.fn_info
        d = info.get_all_args()
        self.assertDictEqual(od_all, d)
        d = info.get_filter_arg()
        self.assertDictEqual(od_args, d)
        d = info.get_filtered_key_word_args()
        self.assertDictEqual(key_word_args, d)
        d = info.get_filtered_kwargs()
        self.assertDictEqual(kwargs, d)
        d = info.get_filter_noargs()
        self.assertDictEqual(od_noargs, d)

    def test_names_args(self):
        class Runner:
            @test_dec_cls
            def foo(sefl, first, second, *args):
                return [first, second] + [*args]

        args_lst = [3, 4]
        od_pre = OrderedDict()
        od_pre['first'] = 1
        od_pre['second'] = 2
        od_args = OrderedDict()
        od_all = OrderedDict(od_pre)
        pre_ofset = len(od_pre)
        for i, arg in enumerate(args_lst):
            key = '*' + str(i + pre_ofset)
            od_all[key] = arg
            od_args[key] = arg
        od_noargs = OrderedDict(od_pre)
        r = Runner()
        result = r.foo(1, 2, *args_lst)
        info: _FnInstInfo = Runner.foo.fn_info
        d = info.get_all_args()
        self.assertDictEqual(od_all, d)
        d = info.get_filter_arg()
        self.assertDictEqual(od_args, d)
        d = info.get_filtered_key_word_args()
        self.assertDictEqual(od_pre, d)
        d = info.get_filtered_kwargs()
        assert len(d) == 0
        d = info.get_filter_noargs()
        self.assertDictEqual(od_noargs, d)

    def test_names_args_names(self):
        class Runner:
            @test_dec_cls
            def foo(self, first, second, *args, third, fourth='4th'):
                return [first, second] + [*args] + [third, fourth]

        args_lst = [3, 4]
        od_pre = OrderedDict()
        od_pre['first'] = 1
        od_pre['second'] = 2
        key_word_args = OrderedDict()
        key_word_args['third'] = '3rd'
        key_word_args['fourth'] = '4th'
        od_args = OrderedDict()
        od_all = OrderedDict(od_pre)
        pre_ofset = len(od_pre)
        for i, arg in enumerate(args_lst):
            key = '*' + str(i + pre_ofset)
            od_all[key] = arg
            od_args[key] = arg
        od_all.update(key_word_args)
        od_noargs = OrderedDict(od_pre)
        od_noargs.update(key_word_args)
        od_all_kw = OrderedDict(od_pre)
        od_all_kw.update(key_word_args)
        r = Runner()
        result = r.foo(1, 2, 3, 4, third='3rd')
        assert result[0] == 1
        info: _FnInstInfo = Runner.foo.fn_info
        d = info.get_all_args()
        self.assertDictEqual(od_all, d)
        d = info.get_filter_arg()
        self.assertDictEqual(od_args, d)
        d = info.get_filtered_key_word_args()
        self.assertDictEqual(od_all_kw, d)
        d = info.get_filtered_kwargs()
        assert len(d) == 0
        d = info.get_filter_noargs()
        self.assertDictEqual(od_noargs, d)

    def test_names_args_kwargs(self):
        class Runner:
            @test_dec_cls
            def foo(self, first, second, *args, **kwargs):
                return [first, second] + [*args] + [v for _, v in kwargs.items()]

        args_lst = [3, 4]
        od_pre = OrderedDict()
        od_pre['first'] = 1
        od_pre['second'] = 2
        kwargs = OrderedDict()
        kwargs['third'] = '3rd'
        kwargs['fourth'] = '4th'
        kwargs['five'] = '5th'
        kwargs['six'] = '6th'
        od_args = OrderedDict()
        od_all = OrderedDict(od_pre)
        pre_ofset = len(od_pre)
        for i, arg in enumerate(args_lst):
            key = '*' + str(i + pre_ofset)
            od_all[key] = arg
            od_args[key] = arg
        od_all.update(kwargs)
        od_noargs = OrderedDict(od_pre)
        od_noargs.update(kwargs)
        r = Runner()
        result = r.foo(1, 2, 3, 4, third='3rd',
                     fourth='4th', five='5th', six='6th')
        assert result[0] == 1
        info: _FnInstInfo = Runner.foo.fn_info
        d = info.get_all_args()
        self.assertDictEqual(od_all, d)
        d = info.get_filter_arg()
        self.assertDictEqual(od_args, d)
        d = info.get_filtered_key_word_args()
        self.assertDictEqual(od_pre, d)
        d = info.get_filtered_kwargs()
        self.assertDictEqual(kwargs, d)

    def test_names_args_names_kwargs(self):
        class Runner:
            @test_dec_cls
            def foo(self, first, second, *args, third, fourth='4th', **kwargs):
                return [first, second] + [*args] + [third, fourth] + [v for _, v in kwargs.items()]

        args_lst = [3, 4]
        od_pre = OrderedDict()
        od_pre['first'] = 1
        od_pre['second'] = 2
        key_word_args = OrderedDict()
        key_word_args['third'] = '3rd'
        key_word_args['fourth'] = '4th'
        kwargs = OrderedDict()
        kwargs['five'] = '5th'
        kwargs['six'] = '6th'
        od_args = OrderedDict()
        od_all = OrderedDict(od_pre)
        pre_ofset = len(od_pre)
        for i, arg in enumerate(args_lst):
            key = '*' + str(i + pre_ofset)
            od_all[key] = arg
            od_args[key] = arg
        od_all.update(key_word_args)
        od_all.update(kwargs)
        od_noargs = OrderedDict(od_pre)
        od_noargs.update(key_word_args)
        od_noargs.update(kwargs)
        od_all_kw = OrderedDict(od_pre)
        od_all_kw.update(key_word_args)
        r = Runner()
        result = r.foo(1, 2, 3, 4, third='3rd', five='5th', six='6th')
        assert result[0] == 1
        info: _FnInstInfo = Runner.foo.fn_info
        assert info.name == 'foo'
        d = info.get_all_args()
        self.assertDictEqual(od_all, d)
        d = info.get_filter_arg()
        self.assertDictEqual(od_args, d)
        d = info.get_filtered_key_word_args()
        self.assertDictEqual(od_all_kw, d)
        d = info.get_filtered_kwargs()
        self.assertDictEqual(kwargs, d)
        d = info.get_filter_noargs()
        self.assertDictEqual(od_noargs, d)

if __name__ == '__main__':
    unittest.main()
