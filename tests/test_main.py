# coding: utf-8
if __name__ == '__main__':
    import path_imports

import unittest
from kwhelp import KwArg, KwargsHelper, CancelEventError, AssignBuilder, HelperArgs, AfterAssignEventArgs, BeforeAssignEventArgs, AfterAssignAutoEventArgs, BeforeAssignAutoEventArgs
import kwhelp.rules as rules
from pathlib import Path


class Runner:
    def __init__(self, **kwargs):
        self._kw = KwargsHelper(self, {**kwargs})

    @property
    def kw(self) -> KwargsHelper:
        return self._kw


class RunnerEx:
    def __init__(self, kw_args: dict = None, **kwargs):
        if kw_args is None:
            kw_args = {}
        self._msg = ''
        self._kw = KwargsHelper(self, {**kwargs}, **kw_args)

    @property
    def kw(self) -> KwargsHelper:
        return self._kw


class EmptyObj(object):
    pass


class TestKwArgsHelper(unittest.TestCase):

    def test_msg_hello_wolrd(self):
        r = Runner(msg='Hello World')
        r.kw.assign(key='msg', types=[str], require=True)
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(r == r.kw.originator)

    def test_msg_hello_wolrd_for_empty_obj(self):
        empty = EmptyObj()
        kw = KwargsHelper(originator=empty, obj_kwargs={
            'msg': 'Hello World'
        })
        kw.assign(key='msg', types=[str], require=True)
        self.assertTrue(hasattr(empty, '_msg'))
        self.assertEqual(empty._msg, 'Hello World')
        self.assertTrue(empty == kw.originator)

    def test_msg_fast(self):
        r = Runner(msg='Hello World')
        r.kw.assign(key='msg', types=[str])
        # default should ignore required
        r.kw.assign(key='fast', field='l__fst', types=[
                    'str'], default=True, require=True)
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, 'l__fst'))
        self.assertTrue(r.l__fst)

    def test_key_bad_type(self):
        r = Runner(msg='Hello World')
        self.assertRaises(TypeError, r.kw.assign, key=self, types=[str])

    def test_require_bad_type(self):
        r = Runner(msg='Hello World')
        self.assertRaises(TypeError, r.kw.assign, key='msg',
                          types=[str], require=1)

    def test_age_required_error(self):
        r = Runner(msg='Hello World')
        r.kw.assign(key='msg', types=[str])
        self.assertRaises(ValueError, r.kw.assign, key='age',
                          types=[int], require=True)

    def test_age_required(self):
        r = Runner(msg='Hello World', age=2)
        r.kw.assign(key='msg', types=[str], require=True)
        r.kw.assign(key='age', types=[int], require=True)
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, 2)

    def test_unused_keys(self):
        r = Runner(msg='Hello World', age=2, width=12, height=24, length=6)
        r.kw.assign(key='msg', types=[str], require=True)
        r.kw.assign(key='age', types=[int], require=True)
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, 2)
        self.assertEqual(len(r.kw.unused_keys), 3)
        self.assertIn('width', r.kw.unused_keys)
        self.assertIn('height', r.kw.unused_keys)
        self.assertIn('length', r.kw.unused_keys)

    def test_bad_type(self):
        r = Runner(msg='Hello World', age="2")
        r.kw.assign(key='msg', types=[str], require=True)
        self.assertRaises(TypeError, r.kw.assign, key='age',
                          types=[int], require=True)

    def test_obj_kwargs_bad_type(self):
        empty = EmptyObj()
        self.assertRaises(TypeError, KwargsHelper,
                          originator=empty, obj_kwargs=[1, 2, 3])

    def test_multi_type(self):
        r = Runner(msg='Hello World', age='2')
        r.kw.assign(key='msg', types=[str], require=True)
        r.kw.assign(key='age', types=[int, str], require=True)
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, '2')

    def test_no_type(self):
        r = Runner(msg='Hello World', age='2')
        r.kw.assign(key='msg', require=True)
        r.kw.assign(key='age', require=True)
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, '2')
        self.assertEqual(r.kw.name, 'Runner')
        self.assertEqual(r.kw.field_prefix, '_')

    def test_no_type_missing_required(self):
        r = Runner(msg='Hello World')
        r.kw.assign(key='msg', require=True)
        self.assertRaises(ValueError, r.kw.assign, key='age', require=True)

    def test_set_name_missing_required(self):
        r = Runner(msg='Hello World')
        r.kw.name = 'TEST'
        r.kw.assign(key='msg', require=True)
        self.assertRaises(ValueError, r.kw.assign, key='age',
                          require=True, types=[int])
        err_msg = ''
        try:
            r.kw.assign(key='age', require=True, types=[int])
        except ValueError as e:
            err_msg = str(e)
        self.assertIn("TEST", err_msg)
        self.assertTrue(r.kw.name == 'TEST')

    def test_set_name_bad_type(self):
        r = Runner(msg='Hello World')
        with self.assertRaises(TypeError):
            r.kw.name = True

    def test_multi_type_error(self):
        # set type_instance_check to false and test.
        # this is done because bool is not type int but bool is instance of int, isinstance(True, int) is True
        r = RunnerEx(kw_args={
                     "type_instance_check": False},
                     msg='Hello World', age=True)
        r.kw.assign(key='msg', types=[str], require=True)
        self.assertRaises(TypeError, r.kw.assign, key='age',
                          types=[int, str], require=True)

        # in this case age is assigned to a type and is not int or str
        r = RunnerEx(msg='Hello World', age=Runner)
        r.kw.assign(key='msg', types=[str], require=True)
        self.assertRaises(TypeError, r.kw.assign, key='age',
                          types=[int, str], require=True)

    def test_field(self):
        r = Runner(msg='Hello World', age=2)
        r.kw.assign(key='msg', types=[str], require=True, field="message")
        r.kw.assign(key='age', types=[int], require=True)
        self.assertTrue(hasattr(r, 'message'))
        self.assertEqual(r.message, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, 2)

    def test_default_no_field(self):
        r = Runner(msg='Hello World', age=2)
        r.kw.assign(key='msg', types=[str], require=True, field="message")
        r.kw.assign(key='age', types=[int], require=True)
        r.kw.assign(key='first_name', types=[str], default='unknown')
        self.assertTrue(hasattr(r, 'message'))
        self.assertEqual(r.message, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, 2)
        self.assertTrue(hasattr(r, '_first_name'))
        self.assertEqual(r._first_name, 'unknown')

    def test_set_field_prefix(self):
        r = Runner(msg='Hello World', age='2')
        r.kw.field_prefix = 'f_'
        r.kw.assign(key='msg', require=True)
        r.kw.assign(key='age', require=True)
        self.assertTrue(hasattr(r, 'f_msg'))
        self.assertEqual(r.f_msg, 'Hello World')
        self.assertTrue(hasattr(r, 'f_age'))
        self.assertEqual(r.f_age, '2')
        self.assertEqual(r.kw.name, 'Runner')
        self.assertEqual(r.kw.field_prefix, 'f_')

    def test_no_field_prefix(self):
        r = Runner(msg='Hello World', age='2')
        r.kw.field_prefix = ''
        r.kw.assign(key='msg', require=True)
        r.kw.assign(key='age', require=True)
        self.assertTrue(hasattr(r, 'msg'))
        self.assertEqual(r.msg, 'Hello World')
        self.assertTrue(hasattr(r, 'age'))
        self.assertEqual(r.age, '2')
        self.assertEqual(r.kw.name, 'Runner')
        self.assertEqual(r.kw.field_prefix, '')

    def test_field_bad_type(self):
        r = Runner(msg='Hello World', age='2')
        with self.assertRaises(TypeError):
            r.kw.field_prefix = True

    def test_rule_test_before_assign_bad_type(self):
        r = Runner(msg='Hello World', age='2')
        with self.assertRaises(TypeError):
            r.kw.rule_test_before_assign = ''

    def test_cancel_error_arg_invalid(self):
        self.assertRaises(TypeError, RunnerEx, kw_args={"cancel_error": 1})
        r = Runner(msg='hello World')
        with self.assertRaises(TypeError):
            r.kw.cancel_error = -1

    def test_assign_true_not_required_invalid(self):
        self.assertRaises(TypeError, RunnerEx, kw_args={
                          "assign_true_not_required": 1})
        r = Runner(msg='hello World')
        with self.assertRaises(TypeError):
            r.kw.assign_true_not_required = -1

    def test_assign_default_none(self):
        r = Runner(msg='Hello World')
        r.kw.assign(key='msg', types=[str], require=True)
        r.kw.assign(key='job', types=[str, None], default=None)
        self.assertEqual(r._msg, 'Hello World')
        self.assertEqual(r._job, None)
        self.assertTrue(r == r.kw.originator)


class TestKwargsHelperInClass(unittest.TestCase):

    def test_msg_hello_wolrd(self):
        class MyRunner:
            def __init__(self, **kwargs):
                self._msg = ''
                kw = KwargsHelper(self, {**kwargs})
                kw.assign(
                    key='msg', require=True, types=[str]
                )
                kw.assign(
                    key='name', require=False, types=[str], default='unknown'
                )

            @property
            def msg(self) -> str:
                return self._msg

            @property
            def name(self) -> str:
                return self._name

        r = MyRunner(msg='Hello World')
        self.assertEqual(r.msg, 'Hello World')
        self.assertTrue(hasattr(r, '_name'))
        self.assertEqual(r.name, 'unknown')

        # 'test' arg will be ignored
        r = MyRunner(msg='Hello World', test=True, name='Uncle Bob')
        self.assertTrue(hasattr(r, '_test') == False)
        self.assertEqual(r.name, 'Uncle Bob')
        self.assertEqual(r.msg, 'Hello World')
        self.assertRaises(ValueError, MyRunner, not_a_msg='Goodbye')
        self.assertRaises(ValueError, MyRunner)
        self.assertRaises(TypeError, MyRunner, msg=100)

    def test_with_args(self):
        class MyRunner:
            def __init__(self, **kwargs):
                self.m_msg = ''
                self.m_length = -1
                kw = KwargsHelper(self, {**kwargs},
                                  field_prefix='m_', name='MY_TEST')
                kw.assign(
                    key='msg', require=True, types=[str]
                )
                kw.assign(
                    key='name', require=False, types=[str], default='unknown'
                )
                kw.assign(
                    key='length', types=[int], default=self.m_length
                )

            @property
            def msg(self) -> str:
                return self.m_msg

            @property
            def name(self) -> str:
                return self.m_name

        r = MyRunner(msg='Hello World')
        self.assertEqual(r.msg, 'Hello World')
        self.assertTrue(hasattr(r, 'm_name'))
        self.assertEqual(r.name, 'unknown')
        self.assertEqual(r.m_length, -1)

        err_msg = ''
        try:
            r = MyRunner(msg=100)
        except TypeError as e:
            err_msg = str(e)
        self.assertIn('MY_TEST', err_msg)

    def test_with_arg_field_prefx_bad(self):
        class MyRunner:
            def __init__(self, **kwargs):
                self.m_msg = ''
                kw = KwargsHelper(self, {**kwargs},
                                  field_prefix=1)
                kw.assign(
                    key='msg', require=True, types=[str]
                )
                kw.assign(
                    key='name', require=False, types=[str], default='unknown'
                )

            @property
            def msg(self) -> str:
                return self.m_msg

            @property
            def name(self) -> str:
                return self.m_name
        self.assertRaises(TypeError, MyRunner, msg='hi')

    def test_with_arg_name_bad(self):
        class MyRunner:
            def __init__(self, **kwargs):
                self.m_msg = ''
                kw = KwargsHelper(self, {**kwargs},
                                  name=1)
                kw.assign(
                    key='msg', require=True, types=[str]
                )
                kw.assign(
                    key='name', require=False, types=[str], default='unknown'
                )

            @property
            def msg(self) -> str:
                return self.m_msg

            @property
            def name(self) -> str:
                return self.m_name
        self.assertRaises(TypeError, MyRunner, msg='hi')

    def test_init_bad_rule_error_arg_type(self):
        self.assertRaises(TypeError, RunnerEx, kw_args={
                          "rule_error": 1}, msg='')
        r = Runner(msg='Hello World')
        with self.assertRaises(TypeError):
            r.kw.rule_error = ''

    def test_init_bad_rule_test_before_assign_arg_type(self):
        self.assertRaises(TypeError, RunnerEx, kw_args={
                          "rule_test_before_assign": 1}, msg='')

    def test_path_obj(self):
        # path object generates type PosixPath,WindowsPath etc.
        # testing if PosixPath is type of Path is False.
        # isinstance(_posx, Path) is True
        p = Path('app.log')
        r = RunnerEx(msg='Hello World', age=10, path=p)
        self.assertRaises(TypeError, r.kw.assign, kw_args={
            "type_instance_check": False},
            key='path', types=[Path])
        r.kw.assign(key='path', types=[Path])
        self.assertEqual(str(r._path), 'app.log')


class TestKwArgsHelperCallback(unittest.TestCase):

    def test_msg_hello_wolrd(self):
        def cb_before(helper, args: BeforeAssignEventArgs):
            self.assertIsInstance(helper, KwargsHelper)
            self.assertEqual(args.key, 'msg')
            self.assertIsNone(args.helper_args.field)
            self.assertIsInstance(args.originator, Runner)

        def cb_before2(helper, args: BeforeAssignEventArgs):
            self.assertIsInstance(helper, KwargsHelper)
            self.assertEqual(args.key, 'msg')
            self.assertIsNone(args.helper_args.field)

        def cb_after(helper, args: AfterAssignEventArgs):
            self.assertIsInstance(helper, KwargsHelper)
            self.assertEqual(args.field_name, '_msg')
            self.assertEqual(args.field_value, 'Hello World')
            self.assertIsNone(args.helper_args.field)
            self.assertIsInstance(args.originator, Runner)

        def cb_after2(helper, args: AfterAssignEventArgs):
            self.assertIsInstance(helper, KwargsHelper)
            self.assertEqual(args.field_name, '_msg')
            self.assertEqual(args.field_value, 'Hello World')
            self.assertIsNone(args.helper_args.field)
            self.assertIsInstance(args.originator, Runner)
            self.assertEqual(args.key, 'msg')

        r = Runner(msg='Hello World')
        r.kw.add_handler_before_assign(cb_before)
        r.kw.add_handler_before_assign(cb_before2)
        r.kw.add_handler_after_assign(cb_after)
        r.kw.add_handler_after_assign(cb_after2)
        r.kw.assign(key='msg', types=[str])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')

    def test_msg_change_message(self):
        def cb_before(helper: KwargsHelper, args: BeforeAssignEventArgs):
            self.assertIsInstance(helper, KwargsHelper)
            self.assertEqual(args.key, 'msg')
            self.assertIsNone(args.helper_args.field)
            self.assertIsInstance(args.originator, Runner)

        def cb_after(helper: KwargsHelper, args: AfterAssignEventArgs):
            self.assertIsInstance(helper, KwargsHelper)
            self.assertEqual(args.field_name, '_msg')
            self.assertEqual(args.field_value, 'Hello World')
            self.assertIsNone(args.helper_args.field)
            self.assertIsInstance(args.originator, Runner)
            setattr(args.originator, args.field_name, 'Soooo.... Yesterday')

        r = Runner(msg='Hello World')
        r.kw.add_handler_before_assign(cb_before)
        r.kw.add_handler_after_assign(cb_after)
        r.kw.assign(key='msg', types=[str])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Soooo.... Yesterday')

    def test_callback_cancel(self):
        def cb_before(helper: KwargsHelper, args: BeforeAssignEventArgs):
            self.assertIsInstance(helper, KwargsHelper)
            if args.key == 'num':
                if args.field_value == 22:
                    args.cancel = True

        def cb_after(helper: KwargsHelper, args: AfterAssignEventArgs):
            self.assertIsInstance(helper, KwargsHelper)
            if args.key == 'msg':
                self.assertEqual(args.field_name, '_msg')
                self.assertEqual(args.field_value, 'Hello World')
            elif args.key == 'num':
                self.assertTrue(args.canceled)

        r = Runner(msg='Hello World', num=22)
        r.kw.add_handler_before_assign(cb_before)
        r.kw.add_handler_after_assign(cb_after)
        result = r.kw.assign(key='msg', types=[str])
        self.assertTrue(result)
        self.assertRaises(CancelEventError, r.kw.assign,
                          key='num', types=[int])

        rx = RunnerEx(kw_args={'cancel_error': False},
                      msg='Hello World', num=22)
        rx.kw.add_handler_before_assign(cb_before)
        rx.kw.add_handler_after_assign(cb_after)
        result = rx.kw.assign(key='msg', types=[str])
        self.assertTrue(result)
        result = rx.kw.assign(key='num', require=True, types=[int])
        self.assertFalse(result)

        rx = RunnerEx(msg='Hello World', num=22)
        rx.kw.cancel_error = False
        rx.kw.add_handler_before_assign(cb_before)
        rx.kw.add_handler_after_assign(cb_after)
        result = rx.kw.assign(key='msg', types=[str])
        self.assertTrue(result)
        result = rx.kw.assign(key='num', require=True, types=[int])
        self.assertFalse(result)
        self.assertFalse(rx.kw.cancel_error)

    def test_cb_change_match_all_rules(self):
        def cb_before(helper: KwargsHelper, args: BeforeAssignEventArgs):
            if args.key == 'msg' and args.match_all_rules == False:
                args.match_all_rules = True
        def cb_after(helper: KwargsHelper, args: AfterAssignEventArgs):
            if args.key == 'msg':
                self.assertTrue(args.match_all_rules)

        r = Runner(msg='Hello World')
        r.kw.add_handler_before_assign(cb_before)
        r.kw.add_handler_after_assign(cb_after)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullEmptyWs, rules.RuleAttrNotExist], all_rules=False)
        
        self.assertTrue(hasattr(r, '_msg'))


class TestKwArgsHelperRules(unittest.TestCase):

    def test_msg_hello_wolrd(self):
        def cb(helper: KwargsHelper, args: AfterAssignEventArgs):
            self.assertTrue(args.rules_passed)
        rx = RunnerEx(msg='Hello World')
        rx.kw.add_handler_after_assign(cb)
        rx.kw.assign(key='msg', rules_all=[
                     rules.RuleStrNotNullOrEmpty, rules.RuleAttrExist])
        self.assertTrue(hasattr(rx, '_msg'))
        self.assertEqual(rx._msg, 'Hello World')

    def test_rule_str(self):
        def cb(helper: KwargsHelper, args: AfterAssignEventArgs):
            if args.key == 'alert':
                self.assertFalse(args.rules_passed)
        r = Runner(msg='')
        result = r.kw.assign('msg', rules_all=[rules.RuleStr])
        self.assertTrue(result)
        r = Runner(msg=None)
        with self.assertRaises(TypeError):
            r.kw.assign(key='msg', rules_all=[rules.RuleStr])

        rx = RunnerEx(kw_args={"rule_error": False}, alert=1)
        rx.kw.add_handler_after_assign(cb)
        result = rx.kw.assign("alert", require=True, rules_all=[rules.RuleStr])
        self.assertFalse(result)

    def test_msg_empty_str_rule(self):
        r = Runner(msg='')
        with self.assertRaises(ValueError):
            r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
  
        rx = RunnerEx(msg='Hello World')
        with self.assertRaises(AttributeError):
            rx.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty, rules.RuleAttrNotExist],
                         all_rules=True)
  
        rx = RunnerEx(kw_args={"rule_error": False}, msg='')
        result = rx.kw.assign(
            key='msg', rules_all=[rules.RuleStrNotNullOrEmpty, rules.RuleAttrExist], all_rules=True)
        rx = RunnerEx(
            {"rule_error": False, 'rule_test_before_assign': False}, msg='')
        result = rx.kw.assign(key='msg', require=True, rules_all=[
                              rules.RuleStrNotNullOrEmpty])
        self.assertFalse(result)
        self.assertEqual(rx._msg, '')

        r = Runner(msg='')
        r.kw.rule_error = False
        r.kw.rule_test_before_assign = False
        result = r.kw.assign(key='msg', require=True, rules_all=[
            rules.RuleStrNotNullOrEmpty])
        self.assertFalse(result)
        self.assertEqual(r._msg, '')
        self.assertFalse(r.kw.rule_error)
        self.assertFalse(r.kw.rule_test_before_assign)

    def test_msg_ws_str_rule(self):
        rx = RunnerEx(kw_args={"rule_error": False}, msg="hello")
        result = rx.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullEmptyWs])
        self.assertTrue(result)

        # not required so result will be True
        rx = RunnerEx(kw_args={"rule_error": False}, msg="")
        result = rx.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullEmptyWs])
        self.assertTrue(result)

        rx = RunnerEx(kw_args={"rule_error": False}, msg="")
        result = rx.kw.assign(
            key='msg', rules_all=[rules.RuleStrNotNullEmptyWs], require=True)
        self.assertFalse(result)

        rx = RunnerEx(kw_args={"rule_error": False}, msg="  ")
        result = rx.kw.assign(
            key='msg', rules_all=[rules.RuleStrNotNullEmptyWs], require=True)
        self.assertFalse(result)

    def test_msg_ws_str_rule_error(self):
        r = Runner(msg='')
        with self.assertRaises(ValueError):
            r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullEmptyWs])
        r = Runner(msg='  ')
        with self.assertRaises(ValueError):
            r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullEmptyWs])
        r = Runner(msg=22)
        with self.assertRaises(TypeError):
            r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullEmptyWs])

    def test_msg_non_str_rule(self):
        r = Runner(msg=2)
        with self.assertRaises(TypeError):
            r.kw.assign(key='msg', all_rules=True,
                        rules_all=[rules.RuleNotNone, rules.RuleStr, rules.RuleStrNotNullOrEmpty])
        rx = RunnerEx(kw_args={"rule_error": False}, msg=2)
        result = rx.kw.assign(key='msg', require=True, rules_all=[
                              rules.RuleStrNotNullOrEmpty])
        self.assertFalse(result)

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, msg=2)
        result = rx.kw.assign(key='msg', require=True, rules_all=[
                              rules.RuleStrNotNullOrEmpty])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_msg'))
        self.assertTrue(rx._msg == 2)

    def test_msg_none_rule(self):
        r = Runner(num=None)
        self.assertRaises(ValueError, r.kw.assign, key='num',
                          rules=[rules.RuleNotNone])

        rx = RunnerEx(kw_args={"rule_error": False}, num=None)
        result = rx.kw.assign(key='num', require=True,
                              rules_all=[rules.RuleNotNone])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=None)
        result = rx.kw.assign(key='num', require=True,
                              rules_all=[rules.RuleNotNone])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == None)

    def test_attrib_must_exist(self):
        def cb(helper: KwargsHelper, args: AfterAssignEventArgs):
            if args.key == 'msg':
                self.assertTrue(args.rules_passed)
            elif args.key == 'num':
                self.assertFalse(args.rules_passed)
        r = Runner(msg='Hello World')
        self.assertRaises(AttributeError, r.kw.assign, key='msg', types=[
            str], rules=[rules.RuleAttrExist])
        rx = RunnerEx(kw_args={'rule_error': False}, msg='Hello World', num=22)
        rx.kw.add_handler_after_assign(cb)
        result = rx.kw.assign('msg', require=True, types=[str], rules_all=[
                              rules.RuleStrNotNullOrEmpty, rules.RuleAttrExist])
        self.assertTrue(result)
        result = rx.kw.assign('num', require=True, types=[int], rules_all=[
                              rules.RuleAttrExist])
        self.assertFalse(result)

    def test_attrib_must_not_exist(self):
        def cb(helper: KwargsHelper, args: AfterAssignEventArgs):
            if args.key == 'msg':
                self.assertFalse(args.rules_passed)
            elif args.key == 'num':
                self.assertTrue(args.rules_passed)
        rx = RunnerEx(msg='Hello World')
        self.assertRaises(AttributeError, rx.kw.assign, key='msg', types=[
            str], rules=[rules.RuleAttrNotExist])
        rx = RunnerEx(kw_args={'rule_error': False}, msg='Hello World', num=22)
        rx.kw.add_handler_after_assign(cb)
        result = rx.kw.assign('msg', require=True, types=[str], rules_all=[
                              rules.RuleStrNotNullOrEmpty, rules.RuleAttrNotExist],
                              all_rules=True)
        self.assertFalse(result)
        result = rx.kw.assign('num', require=True, types=[int], rules_all=[
                              rules.RuleAttrNotExist])
        self.assertTrue(result)

    def test_msg_bad_rule(self):
        class MyRule(Runner):
            '''Just a dummy class that does not implement IRule'''
        r = Runner(msg=None)
        # test with invalid rule raises error
        self.assertRaises(TypeError, r.kw.assign, key='msg',
                          rules=[MyRule])

    def test_int_rule(self):
        r = Runner(num=35)
        r.kw.assign(key='num', rules_all=[rules.RuleInt])
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, 35)
        r = Runner(num=True)
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleInt])

        rx = RunnerEx(kw_args={"rule_error": False}, num=False)
        result = rx.kw.assign(key='num', require=True, rules_all=[rules.RuleInt])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=True)
        result = rx.kw.assign(key='num', require=True, rules_all=[rules.RuleInt])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == True)

    def test_str_rule_positive_int_rule(self):
        r = Runner(msg='Hello World', age=35)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        r.kw.assign(key='age', rules_all=[rules.RuleInt, rules.RuleIntPositive])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, 35)

        r = Runner(age=None)
        self.assertRaises(TypeError, r.kw.assign, key='age', require=True,
                          rules=[rules.RuleIntPositive])

    def test_str_rule_positive_int_rule_invalid(self):
        r = Runner(msg='Hello World', age=-1)
        r.kw.assign(key='msg', require=True, rules_all=[
                    rules.RuleStrNotNullOrEmpty])
        with self.assertRaises(ValueError):
            r.kw.assign(key='age', require=True,
                        rules_all=[rules.RuleIntPositive])

        rx = RunnerEx(kw_args={"rule_error": False}, num=-1)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleIntPositive])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=-1)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleIntPositive])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == -1)

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num='notInt')
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleIntPositive])
        self.assertFalse(result)

    def test_str_rule_positive_int_rule_invalid_type(self):
        r = Runner(msg='Hello World', age='10')
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(TypeError, r.kw.assign,
                          key='age', rules=[rules.RuleIntPositive])

    def test_str_rule_negative_int_rule(self):
        r = Runner(msg='Hello World', num=-35)
        result = r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertTrue(result)
        result = r.kw.assign(key='num', rules_all=[rules.RuleIntNegative])
        self.assertTrue(result)
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, -35)

    def test_str_rule_negative_int_rule_invalid(self):
        r = Runner(msg='Hello World', num=0)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])

        self.assertRaises(ValueError, r.kw.assign,
                          key='num', rules=[rules.RuleIntNegative])
        rx = RunnerEx(kw_args={"rule_error": False}, msg='Hello World', num=0)
        result = rx.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertTrue(result)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleIntNegative])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, msg='Hello World', num=0)
        result = rx.kw.assign(key='msg', require=True, rules_all=[
                              rules.RuleStrNotNullOrEmpty])
        self.assertTrue(result)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleIntNegative])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == 0)

        r = Runner(age=None)
        self.assertRaises(TypeError, r.kw.assign, key='age', require=True,
                          rules=[rules.RuleIntNegative])

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num='notInt')
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleIntNegative])
        self.assertFalse(result)

    def test_str_rule_negative_int_rule_invalid_type(self):
        r = Runner(msg='Hello World', num='10')
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleIntNegative])

    def test_str_rule_negative_zero_int_rule(self):
        r = Runner(msg='Hello World', num=-35)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        r.kw.assign(key='num', rules_all=[rules.RuleIntNegativeOrZero])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, -35)

        r = Runner(msg='Hello World', num=0)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        r.kw.assign(key='num', rules_all=[rules.RuleIntNegativeOrZero])
        self.assertEqual(r._num, 0)

    def test_str_rule_negative_zero_int_rule_invalid(self):
        r = Runner(msg='Hello World', num=1)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])

        self.assertRaises(ValueError, r.kw.assign,
                          key='num', rules=[rules.RuleIntNegativeOrZero])
        rx = RunnerEx(kw_args={"rule_error": False}, msg='Hello World', num=1)
        result = rx.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertTrue(result)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleIntNegativeOrZero])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, msg='Hello World', num=1)
        result = rx.kw.assign(key='msg', require=True, rules_all=[
                              rules.RuleStrNotNullOrEmpty])
        self.assertTrue(result)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleIntNegativeOrZero])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == 1)

        r = Runner(age=None)
        self.assertRaises(TypeError, r.kw.assign, key='age', require=True,
                          rules=[rules.RuleIntNegativeOrZero])

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num='notInt')
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleIntNegativeOrZero])
        self.assertFalse(result)

    def test_str_rule_negative_zero_int_rule_invalid_type(self):
        r = Runner(msg='Hello World', num='10')
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleIntNegativeOrZero])

    def test_float_rule(self):
        r = Runner(num=35.9)
        r.kw.assign(key='num', rules_all=[rules.RuleFloat])
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, 35.9)
        r = Runner(num=True)
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleFloat])

        rx = RunnerEx(kw_args={"rule_error": False}, num=10)
        result = rx.kw.assign(key='num', require=True, rules_all=[rules.RuleFloat])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=True)
        result = rx.kw.assign(key='num', require=True, rules_all=[rules.RuleFloat])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == True)

    def test_str_rule_positive_float_rule(self):
        r = Runner(msg='Hello World', age=35.3)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        r.kw.assign(key='age', rules_all=[rules.RuleFloatPositive])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, 35.3)

    def test_str_rule_positive_float_rule_invalid(self):
        r = Runner(msg='Hello World', num=-1.0)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(ValueError, r.kw.assign,
                          key='num', rules=[rules.RuleFloatPositive])

        rx = RunnerEx(kw_args={"rule_error": False},
                      msg='Hello World', num=-1.0)
        result = rx.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertTrue(result)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleFloatPositive])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, msg='Hello World', num=-1.0)
        result = rx.kw.assign(key='msg', require=True, rules_all=[
                              rules.RuleStrNotNullOrEmpty])
        self.assertTrue(result)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleFloatPositive])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == -1.0)

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num='notInt')
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleFloatPositive])
        self.assertFalse(result)

    def test_str_rule_positive_float_rule_invalid_type(self):
        r = Runner(msg='Hello World', age='10')
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(TypeError, r.kw.assign,
                          key='age', rules=[rules.RuleFloatPositive])

    def test_str_rule_negative_float_rule(self):
        r = Runner(msg='Hello World', num=-35.2)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        r.kw.assign(key='num', rules_all=[rules.RuleFloatNegative])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, -35.2)

    def test_str_rule_negative_float_rule_invalid(self):
        r = Runner(msg='Hello World', num=0.0)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        with self.assertRaises(ValueError):
            r.kw.assign(key='num', require=True, rules_all=[
                        rules.RuleFloatNegative])

        rx = RunnerEx(kw_args={"rule_error": False}, num=0.0)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleFloatNegative])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=0.0)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleFloatNegative])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == 0.0)

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num='notInt')
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleFloatNegative])
        self.assertFalse(result)

    def test_str_rule_negative_float_rule_invalid_type(self):
        r = Runner(msg='Hello World', num='10')
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleFloatNegative])

    def test_str_rule_negative_zero_float_rule(self):
        r = Runner(msg='Hello World', num=-35.2)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        r.kw.assign(key='num', rules_all=[rules.RuleFloatNegativeOrZero])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, -35.2)

        r = Runner(msg='Hello World', num=-0.0)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        r.kw.assign(key='num', rules_all=[rules.RuleFloatNegativeOrZero])
        self.assertEqual(r._num, 0.0)

    def test_str_rule_negative_zero_float_rule_invalid(self):
        r = Runner(msg='Hello World', num=1.1)
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(ValueError, r.kw.assign,
                          key='num', require=True, rules=[rules.RuleFloatNegativeOrZero])

        rx = RunnerEx(kw_args={"rule_error": False}, num=1.1)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleFloatNegativeOrZero])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=1.1)
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleFloatNegativeOrZero])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == 1.1)

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num='notInt')
        result = rx.kw.assign(
            key='num', require=True, rules_all=[rules.RuleFloatNegativeOrZero])
        self.assertFalse(result)

    def test_str_rule_negative_zero_float_rule_invalid_type(self):
        r = Runner(msg='Hello World', num='10')
        r.kw.assign(key='msg', rules_all=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleFloatNegativeOrZero])

    def test_num_rule(self):
        r = Runner(num=35.9)
        r.kw.assign(key='num', rules_all=[rules.RuleNumber])
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, 35.9)
        r = Runner(num=True)
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleNumber])

        rx = RunnerEx(kw_args={"rule_error": False}, num="10")
        result = rx.kw.assign(key='num', require=True,
                              rules_all=[rules.RuleNumber])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=True)
        result = rx.kw.assign(key='num', require=True,
                              rules_all=[rules.RuleNumber])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == True)

    def test_bool_rule(self):
        r = Runner(is_adult=True)
        r.kw.assign(key='is_adult', rules_all=[rules.RuleBool])
        self.assertTrue(hasattr(r, '_is_adult'))
        self.assertEqual(r._is_adult, True)
        r = Runner(is_adult=20)
        self.assertRaises(TypeError, r.kw.assign,
                          key='is_adult', rules=[rules.RuleBool])

        rx = RunnerEx(kw_args={"rule_error": False}, is_adult="10")
        rx.kw.assign_true_not_required = False
        result = rx.kw.assign(key='num', rules_all=[rules.RuleBool])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_is_adult'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, is_adult=10)
        rx.kw.assign_true_not_required = False
        result = rx.kw.assign(key='is_adult', rules_all=[rules.RuleBool])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_is_adult'))
        self.assertTrue(rx._is_adult == 10)


class TestKwArgsHelperAsList(unittest.TestCase):

    def test_list_args(self):
        args = []
        args.append({"key": "msg", "types": [str], "require": True})
        args.append({"key": "age", "types": [int], "require": True})
        args.append({"key": "name", "types": [str], "default": "unknown"})
        args.append({"key": "city", "types": [str], "default": "North York"})
        r = Runner(msg='Hello World', age=2, city='Toronto')
        result = True
        for arg in args:
            result = r.kw.assign(**arg)
            if result == False:
                break
        self.assertTrue(result)
        self.assertEqual(r._msg, 'Hello World')
        self.assertEqual(r._age, 2)
        self.assertEqual(r._name, 'unknown')
        self.assertEqual(r._city, 'Toronto')

    def test_assign_builder_args(self):
        args = AssignBuilder()
        args.append(key="msg", types=[str], require=True)
        args.append(key="age", types=[int], require=True)
        args.append(key="name", types=[str], default="unknown")
        args.append(key="city", types=[str], default="North York")
        r = Runner(msg='Hello World', age=2, city='Toronto')
        result = True
        for arg in args:
            result = r.kw.assign_helper(arg)
            if result == False:
                break
        self.assertTrue(result)
        self.assertEqual(r._msg, 'Hello World')
        self.assertEqual(r._age, 2)
        self.assertEqual(r._name, 'unknown')
        self.assertEqual(r._city, 'Toronto')

    def test_builder_with_rules(self):
        args = AssignBuilder()
        args.append(key="msg", types=[str], require=True)
        args.append(key="age", types=[int], require=True)
        args.append(key="name", rules_all=[rules.RuleStr], default="unknown")
        args.append(key="city", types=[str], rules_all=[
                    rules.RuleStr], default="North York")
        r = Runner(msg='Hello World', age=2, city='Toronto')
        result = True
        for arg in args:
            result = r.kw.assign_helper(arg)
            if result == False:
                break
        self.assertTrue(result)
        self.assertEqual(r._msg, 'Hello World')
        self.assertEqual(r._age, 2)
        self.assertEqual(r._name, 'unknown')
        self.assertEqual(r._city, 'Toronto')

    def test_builder_with_rules_helper(self):
        args = AssignBuilder()
        args.append_helper(HelperArgs(key="msg", types=[str], require=True))
        args.append_helper(HelperArgs(key="age", types=[int], require=True))
        args.append_helper(HelperArgs(key="name", rules=[
                           rules.RuleStr], default="unknown"))
        args.append_helper(HelperArgs(key="city", types=[str], rules=[
            rules.RuleStr], default="North York",  field='_city'))
        r = Runner(msg='Hello World', age=2, city='Toronto')
        result = True
        for arg in args:
            result = r.kw.assign_helper(arg)
            if result == False:
                break
        self.assertTrue(result)
        self.assertEqual(r._msg, 'Hello World')
        self.assertEqual(r._age, 2)
        self.assertEqual(r._name, 'unknown')
        self.assertEqual(r._city, 'Toronto')

    def test_non_require(self):
        self._loop_count = -1
        r = Runner(file_name='data.html', name='Best Doc', loop_count=1)
        ab = AssignBuilder()
        ab.append(key='exporter', rules_all=[rules.RuleStr])
        ab.append(key='name', rules_all=[rules.RuleStr], default='unknown')
        ab.append(key='file_name', rules_all=[
                  rules.RuleStr, rules.RuleStrNotNullOrEmpty])
        ab.append(key='loop_count', rules_all=[
                  rules.RuleInt, rules.RuleIntPositive], default=self._loop_count)
        result = True
        # by default assign will raise errors if conditions are not met.
        for arg in ab:
            result = r.kw.assign_helper(arg)
            if result == False:
                break
        if result == False:
            raise ValueError("Error parsing kwargs")
        self.assertTrue(result)

        def _arg_after_cb(helper: KwargsHelper, args: AfterAssignEventArgs) -> None:
            if args.success == False:
                if args.helper_args.require == False:
                    args.success = True

        r = Runner(file_name='data.html', name='Best Doc', loop_count=1)
        r.kw.assign_true_not_required = False
        ab = AssignBuilder()
        r.kw.add_handler_after_assign(_arg_after_cb)
        ab.append(key='exporter', rules_all=[rules.RuleStr])
        ab.append(key='name', rules_all=[rules.RuleStr],
                  default='unknown', field='_name')
        ab.append(key='file_name', rules_all=[
                  rules.RuleStr, rules.RuleStrNotNullOrEmpty])
        ab.append(key='loop_count', rules_all=[
                  rules.RuleInt, rules.RuleIntPositive], default=self._loop_count)
        result = True
        # by default assign will raise errors if conditions are not met.
        for arg in ab:
            result = r.kw.assign(**arg.to_dict())
            if result == False:
                break
        if result == False:
            raise ValueError("Error parsing kwargs")
        self.assertTrue(result)
        self.assertFalse(r.kw.assign_true_not_required)


class TestKwargsHelperAssignAuto(unittest.TestCase):

    def test_assign_auto_simple(self):
        rx = RunnerEx(kw_args=None, msg='Hello World', age=12)
        result = rx.kw.auto_assign()
        self.assertTrue(result)
        self.assertEqual(rx._msg, 'Hello World')
        self.assertEqual(rx._age, 12)

    def test_assign_auto_no_prefix(self):
        obj = EmptyObj()
        d = {
            "age": 12,
            "height": "5.2'"
        }
        kw = KwargsHelper(originator=obj, obj_kwargs=d, field_prefix='')
        result = kw.auto_assign()
        self.assertTrue(result)
        self.assertEqual(obj.age, 12)
        self.assertEqual(obj.height, "5.2'")

    def test_assign_auto_cb(self):
        obj = EmptyObj()

        def before_assign(_, arg: BeforeAssignAutoEventArgs):
            self.assertEqual(arg.originator, obj)
            if arg.key == 'msg':
                arg.field_name = 'msg'
                arg.field_value = 'Good Day'

        def after_assign(_, arg: AfterAssignAutoEventArgs):
            self.assertTrue(arg.success)
            self.assertEqual(arg.originator, obj)
        d = {
            "age": 12,
            "height": "5.2'",
            "msg": "Hello World"
        }
        kw = KwargsHelper(originator=obj, obj_kwargs=d)
        kw.add_handler_before_assign_auto(before_assign)
        kw.add_handler_after_assign_auto(after_assign)
        result = kw.auto_assign()
        self.assertTrue(result)
        self.assertEqual(obj._age, 12)
        self.assertEqual(obj._height, "5.2'")
        self.assertEqual(obj.msg, "Good Day")

    def test_assign_auto_cb_before(self):
        obj = EmptyObj()

        def before_assign(_, arg: BeforeAssignAutoEventArgs):
            self.assertEqual(arg.originator, obj)
            if arg.key == 'msg':
                arg.field_name = 'msg'
                arg.field_value = 'Good Day'

        d = {
            "age": 12,
            "height": "5.2'",
            "msg": "Hello World"
        }
        kw = KwargsHelper(originator=obj, obj_kwargs=d)
        kw.add_handler_before_assign_auto(before_assign)
        result = kw.auto_assign()
        self.assertTrue(result)
        self.assertEqual(obj._age, 12)
        self.assertEqual(obj._height, "5.2'")
        self.assertEqual(obj.msg, "Good Day")

    def test_assign_auto_cb_after(self):
        obj = EmptyObj()
        d = {
            "age": 12,
            "height": "5.2'",
            "msg": "Hello World"
        }
        kw = KwargsHelper(originator=obj, obj_kwargs=d)

        def after_assign(_, arg: AfterAssignAutoEventArgs):

            self.assertTrue(arg.success)
            self.assertEqual(arg.originator, obj)
            self.assertIn(arg.field_name[1:], d)
            self.assertEqual(arg.field_value, d[arg.field_name[1:]])

        kw.add_handler_after_assign_auto(after_assign)
        result = kw.auto_assign()
        self.assertTrue(result)
        self.assertEqual(obj._age, 12)
        self.assertEqual(obj._height, "5.2'")
        self.assertEqual(obj._msg, "Hello World")

    def test_assign_auto_cb_cancel(self):
        obj = EmptyObj()

        def before_assign(_, arg: BeforeAssignAutoEventArgs):
            self.assertEqual(arg.originator, obj)
            if arg.key == 'msg':
                arg.cancel = True

        def after_assign(_, arg: AfterAssignAutoEventArgs):
            self.assertTrue(arg.success)
            self.assertEqual(arg.originator, obj)
        d = {
            "age": 12,
            "height": "5.2'",
            "msg": "Hello World"
        }
        kw = KwargsHelper(originator=obj, obj_kwargs=d)
        kw.add_handler_before_assign_auto(before_assign)
        kw.add_handler_after_assign_auto(after_assign)
        with self.assertRaises(CancelEventError):
            kw.auto_assign()

    def test_assign_auto_cb_cancel_no_error(self):
        obj = EmptyObj()

        def before_assign(_, arg: BeforeAssignAutoEventArgs):
            self.assertEqual(arg.originator, obj)
            if arg.key == 'msg':
                arg.cancel = True

        def after_assign(_, arg: AfterAssignAutoEventArgs):

            self.assertEqual(arg.originator, obj)
            if arg.key == 'msg':
                self.assertTrue(arg.canceled)
                self.assertFalse(arg.success)
            else:
                self.assertTrue(arg.success)
                self.assertFalse(arg.canceled)
        d = {
            "age": 12,
            "height": "5.2'",
            "msg": "Hello World"
        }
        kw = KwargsHelper(originator=obj, obj_kwargs=d)
        kw.cancel_error = False
        kw.add_handler_before_assign_auto(before_assign)
        kw.add_handler_after_assign_auto(after_assign)
        result = kw.auto_assign()
        self.assertFalse(result)
        self.assertEqual(obj._age, 12)
        self.assertEqual(obj._height, "5.2'")
        self.assertFalse(hasattr(obj, '_msg'))

    def test_assign_auto_no_auto_callback(self):
        def cb_assign_after(_, arg: AfterAssignEventArgs):
            self.assertTrue(arg.success)
            self.assertFalse(arg.canceled)
        obj = EmptyObj()
        d = {
            "age": 12,
            "height": "5.2'",
            "msg": "Hello World"
        }
        kw = KwargsHelper(originator=obj, obj_kwargs=d)
        kw.add_handler_after_assign(cb_assign_after)
        result = kw.auto_assign()
        kw.assign(key='month', types=[str], default='August')
        self.assertTrue(result)
        self.assertEqual(obj._age, 12)
        self.assertEqual(obj._height, "5.2'")
        self.assertEqual(obj._msg, "Hello World")
        self.assertEqual(obj._month, "August")

    def test_assign_auto_and_assign_normal(self):
        obj = EmptyObj()
        d = {
            "age": 12,
            "height": "5.2'",
            "msg": "Hello World"
        }
        kw = KwargsHelper(originator=obj, obj_kwargs=d)
        result = kw.auto_assign()
        kw.assign(key='age', types=[int], require=True)
        kw.assign(key='month', types=[str], default='August')
        self.assertTrue(result)
        self.assertEqual(obj._age, 12)
        self.assertEqual(obj._height, "5.2'")
        self.assertEqual(obj._msg, "Hello World")
        self.assertEqual(obj._month, "August")

class TestAssignAllRules(unittest.TestCase):

    def test_assign_all_rules_runner(self):
        r = Runner(msg='Hello World')
        result = r.kw.assign(key='msg', require=True, all_rules=True,
                    rules_all=[rules.RuleAttrNotExist, rules.RuleStrNotNullEmptyWs])
        self.assertTrue(result)
        self.assertEqual(r._msg, "Hello World")

    def test_assign_all_rules_runner_err(self):
        r = Runner(msg='  ')
        with self.assertRaises(ValueError):
            r.kw.assign(key='msg', require=True, all_rules=True,
                        rules_all=[rules.RuleAttrNotExist, rules.RuleStrNotNullEmptyWs])
        r = Runner(msg='Hello World')
        with self.assertRaises(TypeError):
            r.kw.assign(key='msg', require=True, all_rules=True,
                        rules_all=[rules.RuleAttrNotExist, rules.RuleStrNotNullEmptyWs, rules.RuleInt])
        rx = RunnerEx(kw_args={"rule_error": False}, msg='Hello World')
        result = rx.kw.assign(key='msg', require=True, all_rules=True,
                        rules_all=[rules.RuleAttrExist, rules.RuleStrNotNullEmptyWs])
        self.assertTrue(result)
        rx = RunnerEx(kw_args={"rule_error": False}, msg='  ')
        result = rx.kw.assign(key='msg', require=True, all_rules=True,
                             rules_all=[rules.RuleAttrExist, rules.RuleStrNotNullEmptyWs])
        self.assertFalse(result)

    def test_assign_all_rules_kw_args(self):
        obj = KwArg(msg='Hello World')
        result = obj.kw_assign(key='msg', require=True, all_rules=True,
                      rules_all=[rules.RuleAttrNotExist, rules.RuleStrNotNullEmptyWs])
        self.assertTrue(result)
        self.assertEqual(obj.msg, "Hello World")

    def test_assign_all_rules_kw_args_err(self):
        obj = KwArg(msg=' ')
        with self.assertRaises(ValueError):
            obj.kw_assign(key='msg', require=True, all_rules=True,
                        rules_all=[rules.RuleAttrNotExist, rules.RuleStrNotNullEmptyWs])
        obj = KwArg(msg='Hello World')
        with self.assertRaises(AttributeError):
            obj.kw_assign(key='msg', require=True, all_rules=True,
                          rules_all=[rules.RuleAttrExist, rules.RuleStrNotNullEmptyWs])

    def test_assign_any_rule_runner(self):
        r = Runner(msg='Hello World')
        result = r.kw.assign(key='msg', require=True, all_rules=False,
                             rules_all=[rules.RuleStrNotNullEmptyWs, rules.RuleIntPositive])
        self.assertTrue(result)
        self.assertEqual(r._msg, "Hello World")
        r = Runner(msg=25)
        result = r.kw.assign(key='msg', require=True, all_rules=False,
                             rules_all=[rules.RuleStrNotNullEmptyWs, rules.RuleIntPositive])
        self.assertTrue(result)
        self.assertEqual(r._msg, 25)

    def test_assign_any_rule_runner_err(self):
        r = Runner(msg=' ')
        with self.assertRaises(ValueError):
            r.kw.assign(key='msg', require=True, all_rules=False,
                        rules_all=[rules.RuleStrNotNullEmptyWs, rules.RuleIntPositive])
        r = Runner(msg=-2)
        with self.assertRaises(TypeError):
            # TypeError because first error found will be the error raised with assign.
            # if rules were reversed this would result in a ValueError
            r.kw.assign(key='msg', require=True, all_rules=False,
                        rules_all=[rules.RuleStrNotNullEmptyWs, rules.RuleIntPositive])
        r = Runner(msg=-2)
        with self.assertRaises(ValueError):
            # ValueError because first error found will be the error raised with assign.
            # if rules were reversed this would result in a TypeError
            r.kw.assign(key='msg', require=True, all_rules=False,
                        rules_all=[rules.RuleIntPositive, rules.RuleStrNotNullEmptyWs])


if __name__ == '__main__':
    unittest.main()
