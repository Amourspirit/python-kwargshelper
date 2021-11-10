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
        base._fn = foo
        base.args = [1, 2, 3]
        assert base._drop_arg_first() == False
        args = base._get_args()
        assert len(args) == 3
        base.args = []
        args_dic = base._get_args_dict(error_check=False)
        assert args_dic["arg1"] == NO_THING
        assert args_dic["arg2"] == NO_THING
        base.args = []
        base.kwargs = {"arg1": 1, "arg2": 2}
        args_dic = base._get_args_dict()
        assert args_dic["arg1"] == 1
        assert args_dic["arg2"] == 2
        sig = base._get_signature()
        assert base._get_signature() == sig
        assert base._get_star_args_pos() == -1
        assert base._is_placeholder_arg("*199") == True
        with self.assertRaises(TypeError):
            base.args = []
            base.kwargs = {}
            base._get_args_dict(error_check=True)

    def test_star_args(self):
        def foo(*args, arg1, arg2, **kwargs): pass

        base = _DecBase()
        base._fn = foo
        base.args = [1, 2, 3]
        assert base._drop_arg_first() == False
        args = base._get_args()
        assert len(args) == 3
        base.args = []
        base.kwargs = {}
        args_dic = base._get_args_dict(error_check=False)
        assert args_dic["arg1"] == NO_THING
        assert args_dic["arg2"] == NO_THING
        base.args = []
        base.kwargs = {"arg1": 1, "arg2": 2}
        args_dic = base._get_args_dict()
        assert args_dic["arg1"] == 1
        assert args_dic["arg2"] == 2
        sig = base._get_signature()
        assert base._get_signature() == sig
        assert base._get_star_args_pos() == 0
        assert base._is_placeholder_arg("199") == False
        with self.assertRaises(TypeError):
            base.args = []
            base.kwargs = {}
            base._get_args_dict()

    def test_star_args_class(self):
        class Bar:
            def foo(self, *args, arg1, arg2, **kwargs): pass
        b = Bar()
        base = _DecBase(ftype=DecFuncEnum.METHOD)
        base._fn = Bar.foo
        base.args = [0, 1, 2, 3]
        assert base._drop_arg_first() == True
        args = base._get_args()
        assert len(args) == 3
        base.args = []
        base.kwargs = {}
        args_dic = base._get_args_dict(error_check=False)
        assert args_dic["arg1"] == NO_THING
        assert args_dic["arg2"] == NO_THING
        base.args = []
        base.kwargs = {"arg1": 1, "arg2": 2}
        args_dic = base._get_args_dict()
        assert args_dic["arg1"] == 1
        assert args_dic["arg2"] == 2
        sig = base._get_signature()
        assert base._get_signature() == sig
        assert base._get_star_args_pos() == 0
        assert base._is_placeholder_arg("199") == False
        with self.assertRaises(TypeError):
            base.args = []
            base.kwargs = {}
            base._get_args_dict()

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

    def test_get_formated_names(self):
        rt = _DecBase()
        result = rt._get_formated_names(names=['first'])
        assert result == "'first'"
        result = rt._get_formated_names(names=['first', 'second'])
        assert result == "'first' and 'second'"
        result = rt._get_formated_names(names=['first', 'second', 'third'])
        assert result == "'first', 'second', and 'third'"


if __name__ == '__main__':
    unittest.main()
