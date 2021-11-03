import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.decorator import DecFuncEnum, _DecBase
from kwhelp.helper import NO_THING

class TestDecBase(unittest.TestCase):
    def test_bad_constructro(self):
        with self.assertRaises(TypeError):
            base = _DecBase(ftype="")

    def test_gen(self):
        def foo(arg1, arg2, **kwargs): pass
        
        base = _DecBase()
        assert base._drop_arg_first() == False
        args = base._get_args([1, 2, 3])
        assert len(args) == 3
        args_dic = base._get_args_dict(foo, [], {})
        assert args_dic["arg1"] == NO_THING
        assert args_dic["arg2"] == NO_THING
        args_dic = base._get_args_dict(foo, [], {"arg1": 1, "arg2": 2})
        assert args_dic["arg1"] == 1
        assert args_dic["arg2"] == 2
        sig = base._get_signature(foo)
        assert base._get_signature(foo) == sig
        assert base._get_star_args_pos(foo) == -1
        assert base._is_placeholder_arg("*199") == True

    def test_star_args(self):
        def foo(*args, arg1, arg2, **kwargs): pass

        base = _DecBase()
        assert base._drop_arg_first() == False
        args = base._get_args([1, 2, 3])
        assert len(args) == 3
        args_dic = base._get_args_dict(foo, [], {})
        assert args_dic["arg1"] == NO_THING
        assert args_dic["arg2"] == NO_THING
        args_dic = base._get_args_dict(foo, [], {"arg1": 1, "arg2": 2})
        assert args_dic["arg1"] == 1
        assert args_dic["arg2"] == 2
        sig = base._get_signature(foo)
        assert base._get_signature(foo) == sig
        assert base._get_star_args_pos(foo) == 0
        assert base._is_placeholder_arg("199") == False

    def test_star_args_class(self):
        class Bar:
            def foo(self, *args, arg1, arg2, **kwargs): pass
        b = Bar()
        base = _DecBase(ftype=DecFuncEnum.METHOD)
        assert base._drop_arg_first() == True
        args = base._get_args([0, 1, 2, 3])
        assert len(args) == 3
        args_dic = base._get_args_dict(Bar.foo, [], {})
        assert args_dic["arg1"] == NO_THING
        assert args_dic["arg2"] == NO_THING
        args_dic = base._get_args_dict(Bar.foo, [], {"arg1": 1, "arg2": 2})
        assert args_dic["arg1"] == 1
        assert args_dic["arg2"] == 2
        sig = base._get_signature(Bar.foo)
        assert base._get_signature(Bar.foo) == sig
        assert base._get_star_args_pos(Bar.foo) == 0
        assert base._is_placeholder_arg("199") == False


    def test_ordianl(self):
        rt = _DecBase()
        result = rt._get_ordinal(1)
        self.assertEqual(result, "1st")
        result = rt._get_ordinal(2)
        self.assertEqual(result, "2nd")
        result = rt._get_ordinal(4)
        self.assertEqual(result, "4th")
        result = rt._get_ordinal(10)
        self.assertEqual(result, "10th")
        result = rt._get_ordinal(11)
        self.assertEqual(result, "11th")
        result = rt._get_ordinal(22)
        self.assertEqual(result, "22nd")
        result = rt._get_ordinal(33)
        self.assertEqual(result, "33rd")

if __name__ == '__main__':
    unittest.main()
