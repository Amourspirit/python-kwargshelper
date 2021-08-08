# coding: utf-8
try:
    import path_imports
except:
    pass
import unittest
from src.kwargs_util import AfterAssignEventArgs, AssignBuilder, BeforeAssignEventArgs, CancelEventError, HelperArgs, KwargsHelper
import src.kwarg_rules as rules


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


class TestKwArgsHelper(unittest.TestCase):

    def test_msg_hello_wolrd(self):
        r = Runner(msg='Hello World')
        r.kw.assign(key='msg', types=['str'])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(r == r.kw.originator)

    def test_msg_fast(self):
        r = Runner(msg='Hello World')
        r.kw.assign(key='msg', types=['str'])
        # default should ignore required
        r.kw.assign(key='fast', field='l__fst', types=[
                    'str'], default=True, require=True)
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, 'l__fst'))
        self.assertTrue(r.l__fst)

    def test_key_bad_type(self):
        r = Runner(msg='Hello World')
        self.assertRaises(TypeError, r.kw.assign, key=self, types=['str'])

    def test_require_bad_type(self):
        r = Runner(msg='Hello World')
        self.assertRaises(TypeError, r.kw.assign, key='msg',
                          types=['str'], require=1)

    def test_age_required_error(self):
        r = Runner(msg='Hello World')
        r.kw.assign(key='msg', types=['str'])
        self.assertRaises(ValueError, r.kw.assign, key='age',
                          types=['int'], require=True)

    def test_age_required(self):
        r = Runner(msg='Hello World', age=2)
        r.kw.assign(key='msg', types=['str'], require=True)
        r.kw.assign(key='age', types=['int'], require=True)
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, 2)

    def test_bad_type(self):
        r = Runner(msg='Hello World', age="2")
        r.kw.assign(key='msg', types=['str'], require=True)
        self.assertRaises(TypeError, r.kw.assign, key='age',
                          types=['int'], require=True)

    def test_multi_type(self):
        r = Runner(msg='Hello World', age='2')
        r.kw.assign(key='msg', types=['str'], require=True)
        r.kw.assign(key='age', types=['int', 'str'], require=True)
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
                          require=True, types=['int'])
        err_msg = ''
        try:
            r.kw.assign(key='age', require=True, types=['int'])
        except ValueError as e:
            err_msg = str(e)
        self.assertIn("TEST", err_msg)
        self.assertTrue(r.kw.name == 'TEST')

    def test_set_name_bad_type(self):
        r = Runner(msg='Hello World')
        with self.assertRaises(TypeError):
            r.kw.name = True

    def test_multi_type_error(self):
        r = Runner(msg='Hello World', age=True)
        r.kw.assign(key='msg', types=['str'], require=True)
        self.assertRaises(TypeError, r.kw.assign, key='age',
                          types=['int', 'str'], require=True)

    def test_field(self):
        r = Runner(msg='Hello World', age=2)
        r.kw.assign(key='msg', types=['str'], require=True, field="message")
        r.kw.assign(key='age', types=['int'], require=True)
        self.assertTrue(hasattr(r, 'message'))
        self.assertEqual(r.message, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, 2)

    def test_default_no_field(self):
        r = Runner(msg='Hello World', age=2)
        r.kw.assign(key='msg', types=['str'], require=True, field="message")
        r.kw.assign(key='age', types=['int'], require=True)
        r.kw.assign(key='first_name', types=['str'], default='unknown')
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


class TestKwargsHelperInClass(unittest.TestCase):

    def test_msg_hello_wolrd(self):
        class MyRunner:
            def __init__(self, **kwargs):
                self._msg = ''
                kw = KwargsHelper(self, {**kwargs})
                kw.assign(
                    key='msg', require=True, types=['str']
                )
                kw.assign(
                    key='name', require=False, types=['str'], default='unknown'
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
                    key='msg', require=True, types=['str']
                )
                kw.assign(
                    key='name', require=False, types=['str'], default='unknown'
                )
                kw.assign(
                    key='length', types=['int'], default=self.m_length
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
                    key='msg', require=True, types=['str']
                )
                kw.assign(
                    key='name', require=False, types=['str'], default='unknown'
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
                    key='msg', require=True, types=['str']
                )
                kw.assign(
                    key='name', require=False, types=['str'], default='unknown'
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
        r.kw.assign(key='msg', types=['str'])
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
        r.kw.assign(key='msg', types=['str'])
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
        result = r.kw.assign(key='msg', types=['str'])
        self.assertTrue(result)
        self.assertRaises(CancelEventError, r.kw.assign,
                          key='num', types=['int'])

        rx = RunnerEx(kw_args={'cancel_error': False},
                      msg='Hello World', num=22)
        rx.kw.add_handler_before_assign(cb_before)
        rx.kw.add_handler_after_assign(cb_after)
        result = rx.kw.assign(key='msg', types=['str'])
        self.assertTrue(result)
        result = rx.kw.assign(key='num', require=True, types=['int'])
        self.assertFalse(result)

        rx = RunnerEx(msg='Hello World', num=22)
        rx.kw.cancel_error = False
        rx.kw.add_handler_before_assign(cb_before)
        rx.kw.add_handler_after_assign(cb_after)
        result = rx.kw.assign(key='msg', types=['str'])
        self.assertTrue(result)
        result = rx.kw.assign(key='num', require=True, types=['int'])
        self.assertFalse(result)
        self.assertFalse(rx.kw.cancel_error)


class TestKwArgsHelperRules(unittest.TestCase):

    def test_msg_hello_wolrd(self):
        def cb(helper: KwargsHelper, args: AfterAssignEventArgs):
            self.assertTrue(args.rules_passed)
        rx = RunnerEx(msg='Hello World')
        rx.kw.add_handler_after_assign(cb)
        rx.kw.assign(key='msg', rules=[
                     rules.RuleStrNotNullOrEmpty, rules.RuleAttrExist])
        self.assertTrue(hasattr(rx, '_msg'))
        self.assertEqual(rx._msg, 'Hello World')

    def test_rule_str(self):
        def cb(helper: KwargsHelper, args: AfterAssignEventArgs):
            if args.key == 'alert':
                self.assertFalse(args.rules_passed)
        r = Runner(msg='')
        result = r.kw.assign('msg', rules=[rules.RuleStr])
        self.assertTrue(result)
        r = Runner(msg=None)
        self.assertRaises(TypeError, r.kw.assign,
                          key='msg', rules=[rules.RuleStr])
        rx = RunnerEx(kw_args={"rule_error": False}, alert=1)
        rx.kw.add_handler_after_assign(cb)
        result = rx.kw.assign("alert", require=True, rules=[rules.RuleStr])
        self.assertFalse(result)

    def test_msg_empty_str_rule(self):
        r = Runner(msg='')
        self.assertRaises(ValueError, r.kw.assign, key='msg',
                          rules=[rules.RuleStrNotNullOrEmpty])
        rx = RunnerEx(msg='Hello World')
        self.assertRaises(AttributeError, rx.kw.assign, key='msg',
                          rules=[rules.RuleStrNotNullOrEmpty, rules.RuleAttrNotExist])
        rx = RunnerEx(kw_args={"rule_error": False}, msg='')
        result = rx.kw.assign(
            key='msg', rules=[rules.RuleStrNotNullOrEmpty, rules.RuleAttrExist])
        rx = RunnerEx(
            {"rule_error": False, 'rule_test_before_assign': False}, msg='')
        result = rx.kw.assign(key='msg', require=True, rules=[
                              rules.RuleStrNotNullOrEmpty])
        self.assertFalse(result)
        self.assertEqual(rx._msg, '')

        r = Runner(msg='')
        r.kw.rule_error = False
        r.kw.rule_test_before_assign = False
        result = r.kw.assign(key='msg', require=True, rules=[
            rules.RuleStrNotNullOrEmpty])
        self.assertFalse(result)
        self.assertEqual(r._msg, '')
        self.assertFalse(r.kw.rule_error)
        self.assertFalse(r.kw.rule_test_before_assign)

    def test_msg_ws_str_rule(self):
        r = Runner(msg='  ')
        self.assertRaises(ValueError, r.kw.assign, key='msg',
                          rules=[rules.RuleStrNotNullOrEmpty])

    def test_msg_non_str_rule(self):
        r = Runner(msg=2)
        self.assertRaises(TypeError, r.kw.assign, key='msg',
                          rules=[rules.RuleNotNone, rules, rules.RuleStr, rules.RuleStrNotNullOrEmpty])

        rx = RunnerEx(kw_args={"rule_error": False}, msg=2)
        result = rx.kw.assign(key='msg', require=True, rules=[
                              rules.RuleStrNotNullOrEmpty])
        self.assertFalse(result)

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, msg=2)
        result = rx.kw.assign(key='msg', require=True, rules=[
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
                              rules=[rules.RuleNotNone])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=None)
        result = rx.kw.assign(key='num', require=True,
                              rules=[rules.RuleNotNone])
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
            'str'], rules=[rules.RuleAttrExist])
        rx = RunnerEx(kw_args={'rule_error': False}, msg='Hello World', num=22)
        rx.kw.add_handler_after_assign(cb)
        result = rx.kw.assign('msg', require=True, types=['str'], rules=[
                              rules.RuleStrNotNullOrEmpty, rules.RuleAttrExist])
        self.assertTrue(result)
        result = rx.kw.assign('num', require=True, types=['int'], rules=[
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
            'str'], rules=[rules.RuleAttrNotExist])
        rx = RunnerEx(kw_args={'rule_error': False}, msg='Hello World', num=22)
        rx.kw.add_handler_after_assign(cb)
        result = rx.kw.assign('msg', require=True, types=['str'], rules=[
                              rules.RuleStrNotNullOrEmpty, rules.RuleAttrNotExist])
        self.assertFalse(result)
        result = rx.kw.assign('num', require=True, types=['int'], rules=[
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
        r.kw.assign(key='num', rules=[rules.RuleInt])
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, 35)
        r = Runner(num=True)
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleInt])

        rx = RunnerEx(kw_args={"rule_error": False}, num=False)
        result = rx.kw.assign(key='num', require=True, rules=[rules.RuleInt])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=True)
        result = rx.kw.assign(key='num', require=True, rules=[rules.RuleInt])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == True)

    def test_str_rule_positive_int_rule(self):
        r = Runner(msg='Hello World', age=35)
        r.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        r.kw.assign(key='age', rules=[rules.RuleInt, rules.RuleIntPositive])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, 35)

        r = Runner(age=None)
        # RuleIntPositive will not raise a TypeError and will return False for non Int.
        # RuleInt will raise a Type error so these two rules are normally together as in the above test
        result = r.kw.assign(key='age', require=True,
                             rules=[rules.RuleIntPositive])
        self.assertFalse(result)

    def test_str_rule_positive_int_rule_invalid(self):
        r = Runner(msg='Hello World', age=-1)
        r.kw.assign(key='msg', require=True, rules=[
                    rules.RuleStrNotNullOrEmpty])
        self.assertRaises(ValueError, r.kw.assign, key='age', require=True,
                          rules=[rules.RuleInt, rules.RuleIntPositive])

        rx = RunnerEx(kw_args={"rule_error": False}, num=-1)
        result = rx.kw.assign(
            key='num', require=True, rules=[rules.RuleInt, rules.RuleIntPositive])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=-1)
        result = rx.kw.assign(
            key='num', require=True, rules=[rules.RuleInt, rules.RuleIntPositive])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == -1)

    def test_str_rule_positive_int_rule_invalid_type(self):
        r = Runner(msg='Hello World', age='10')
        r.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(TypeError, r.kw.assign,
                          key='age', rules=[rules.RuleInt, rules.RuleIntPositive])

    def test_str_rule_negative_int_rule(self):
        r = Runner(msg='Hello World', num=-35)
        r.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        r.kw.assign(key='num', rules=[rules.RuleInt, rules.RuleIntNegative])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, -35)

    def test_str_rule_negative_int_rule_invalid(self):
        r = Runner(msg='Hello World', num=0)
        r.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(ValueError, r.kw.assign,
                          key='num', rules=[rules.RuleInt, rules.RuleIntNegative])
        rx = RunnerEx(kw_args={"rule_error": False}, msg='Hello World', num=0)
        result = rx.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        self.assertTrue(result)
        result = rx.kw.assign(
            key='num', require=True, rules=[rules.RuleInt, rules.RuleIntNegative])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, msg='Hello World', num=0)
        result = rx.kw.assign(key='msg', require=True, rules=[
                              rules.RuleStrNotNullOrEmpty])
        self.assertTrue(result)
        result = rx.kw.assign(
            key='num', require=True, rules=[rules.RuleInt, rules.RuleIntNegative])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == 0)

        r = Runner(age=None)
        # RuleIntNegative will not raise a TypeError and will return False for non Int.
        # RuleInt will raise a Type error so these two rules are normally together as in the above test
        result = r.kw.assign(key='age', require=True,
                             rules=[rules.RuleIntNegative])
        self.assertFalse(result)

    def test_str_rule_negative_int_rule_invalid_type(self):
        r = Runner(msg='Hello World', num='10')
        r.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleInt, rules.RuleIntNegative])

    def test_float_rule(self):
        r = Runner(num=35.9)
        r.kw.assign(key='num', rules=[rules.RuleFloat])
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, 35.9)
        r = Runner(num=True)
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleFloat])

        rx = RunnerEx(kw_args={"rule_error": False}, num=10)
        result = rx.kw.assign(key='num', require=True, rules=[rules.RuleFloat])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=True)
        result = rx.kw.assign(key='num', require=True, rules=[rules.RuleFloat])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == True)

    def test_str_rule_positive_float_rule(self):
        r = Runner(msg='Hello World', age=35.3)
        r.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        r.kw.assign(key='age', rules=[
                    rules.RuleFloat, rules.RuleFloatPositive])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_age'))
        self.assertEqual(r._age, 35.3)

    def test_str_rule_positive_float_rule_invalid(self):
        r = Runner(msg='Hello World', num=-1.0)
        r.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(ValueError, r.kw.assign,
                          key='num', rules=[rules.RuleFloat, rules.RuleFloatPositive])

        rx = RunnerEx(kw_args={"rule_error": False},
                      msg='Hello World', num=-1.0)
        result = rx.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        self.assertTrue(result)
        result = rx.kw.assign(
            key='num', require=True, rules=[rules.RuleFloat, rules.RuleFloatPositive])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, msg='Hello World', num=-1.0)
        result = rx.kw.assign(key='msg', require=True, rules=[
                              rules.RuleStrNotNullOrEmpty])
        self.assertTrue(result)
        result = rx.kw.assign(
            key='num', require=True, rules=[rules.RuleFloat, rules.RuleFloatPositive])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == -1.0)

    def test_str_rule_positive_float_rule_invalid_type(self):
        r = Runner(msg='Hello World', age='10')
        r.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(TypeError, r.kw.assign,
                          key='age', rules=[rules.RuleFloat, rules.RuleFloatPositive])

    def test_str_rule_negative_float_rule(self):
        r = Runner(msg='Hello World', num=-35.2)
        r.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        r.kw.assign(key='num', rules=[
                    rules.RuleFloat, rules.RuleFloatNegative])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, -35.2)

    def test_str_rule_negative_float_rule_invalid(self):
        r = Runner(msg='Hello World', num=0.0)
        r.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(ValueError, r.kw.assign,
                          key='num', require=True, rules=[rules.RuleFloat, rules.RuleFloatNegative])

        rx = RunnerEx(kw_args={"rule_error": False}, num=0.0)
        result = rx.kw.assign(
            key='num', require=True, rules=[rules.RuleFloat, rules.RuleFloatNegative])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=0.0)
        result = rx.kw.assign(
            key='num', require=True, rules=[rules.RuleFloat, rules.RuleFloatNegative])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == 0.0)

    def test_str_rule_negative_float_rule_invalid_type(self):
        r = Runner(msg='Hello World', num='10')
        r.kw.assign(key='msg', rules=[rules.RuleStrNotNullOrEmpty])
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleFloat, rules.RuleFloatNegative])

    def test_num_rule(self):
        r = Runner(num=35.9)
        r.kw.assign(key='num', rules=[rules.RuleNumber])
        self.assertTrue(hasattr(r, '_num'))
        self.assertEqual(r._num, 35.9)
        r = Runner(num=True)
        self.assertRaises(TypeError, r.kw.assign,
                          key='num', rules=[rules.RuleNumber])

        rx = RunnerEx(kw_args={"rule_error": False}, num="10")
        result = rx.kw.assign(key='num', require=True,
                              rules=[rules.RuleNumber])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_num'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, num=True)
        result = rx.kw.assign(key='num', require=True,
                              rules=[rules.RuleNumber])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_num'))
        self.assertTrue(rx._num == True)

    def test_bool_rule(self):
        r = Runner(is_adult=True)
        r.kw.assign(key='is_adult', rules=[rules.RuleBool])
        self.assertTrue(hasattr(r, '_is_adult'))
        self.assertEqual(r._is_adult, True)
        r = Runner(is_adult=20)
        self.assertRaises(TypeError, r.kw.assign,
                          key='is_adult', rules=[rules.RuleBool])

        rx = RunnerEx(kw_args={"rule_error": False}, is_adult="10")
        rx.kw.assign_true_not_required = False
        result = rx.kw.assign(key='num', rules=[rules.RuleBool])
        self.assertFalse(result)
        self.assertFalse(hasattr(rx, '_is_adult'))

        rx = RunnerEx(kw_args={
                      "rule_error": False, 'rule_test_before_assign': False}, is_adult=10)
        rx.kw.assign_true_not_required = False
        result = rx.kw.assign(key='is_adult', rules=[rules.RuleBool])
        self.assertFalse(result)
        self.assertTrue(hasattr(rx, '_is_adult'))
        self.assertTrue(rx._is_adult == 10)


class TestAssignBuilder(unittest.TestCase):
    def test_build_append(self):
        args = AssignBuilder()
        args.append(key="msg", field='test', types=['str'], require=True)
        args.append(key="age", types=['int'], require=True)
        args.append(key="name", rules=[rules.RuleStr], default="unknown")
        args.append(key="city", types=['str'], rules=[
                    rules.RuleStr], default="North York")
        self.assertEqual(args[0]['key'], 'msg')
        self.assertListEqual(args[0]['types'], ['str'])
        self.assertTrue(args[0]['require'])
        self.assertEqual(args[0]['field'], 'test')
        self.assertListEqual(args[3]['rules'], [rules.RuleStr])
        self.assertEqual(args[3]['default'], 'North York')

        self.assertRaises(TypeError, args.append, key=2)
        # empyty or whitespace not ok for key
        self.assertRaises(ValueError, args.append, key=' ')
        self.assertRaises(ValueError, args.append, key='')
        # duplicate, raises error, cannot have the same key twice
        self.assertRaises(ValueError, args.append, key="msg",
                          field='test', types=['str'], require=True)

    def test_build_append_helper(self):
        args = AssignBuilder()
        args.append_helper(HelperArgs(key="msg", field='test',
                           types=['str'], require=True))
        args.append_helper(HelperArgs(key="age", types=['int'], require=True))
        args.append_helper(HelperArgs(key="name", rules=[
                           rules.RuleStr], default="unknown"))
        args.append_helper(HelperArgs(key="city", types=['str'], rules=[
            rules.RuleStr], default="North York"))
        self.assertEqual(args[0]['key'], 'msg')
        self.assertListEqual(args[0]['types'], ['str'])
        self.assertTrue(args[0]['require'])
        self.assertEqual(args[0]['field'], 'test')
        self.assertListEqual(args[3]['rules'], [rules.RuleStr])
        self.assertEqual(args[3]['default'], 'North York')

        self.assertRaises(TypeError, args.append, key=2)
        # empyty or whitespace not ok for key
        self.assertRaises(ValueError, args.append, key=' ')
        self.assertRaises(ValueError, args.append, key='')
        # duplicate, raises error, cannot have the same key twice
        self.assertRaises(ValueError, args.append, key="msg",
                          field='test', types=['str'], require=True)

    def test_builder_append_remove(self):
        args = AssignBuilder()
        args.append(key="msg", types=['str'], require=True)
        args.append(key="age", types=['int'], require=True)
        args.append(key="name", rules=[rules.RuleStr], default="unknown")
        args.append(key="city", types=['str'], rules=[
                    rules.RuleStr], default="North York")
        self.assertTrue(len(args) == 4)
        args.remove(args[2])
        self.assertTrue(len(args) == 3)
        args.remove(args[2])
        self.assertTrue(len(args) == 2)
        args.append(key="city", types=['str'], rules=[
                    rules.RuleStr], default="North York")
        self.assertTrue(len(args) == 3)
        self.assertRaises(KeyError, args.remove, {})
        self.assertRaises(TypeError, args.remove, [])
        result = args.remove(None)
        self.assertIsNone(result)

    def test_builder_append_extend(self):
        args = AssignBuilder()
        args.append(key="msg", types=['str'], require=True)
        args.append(key="age", types=['int'], require=True)
        args.append(key="name", rules=[rules.RuleStr], default="unknown")
        args.append(key="city", types=['str'], rules=[
                    rules.RuleStr], default="North York")
        self.assertTrue(len(args) == 4)
        args_ex = AssignBuilder()
        args_ex.append(key="message", types=['str'], require=True)
        args_ex.append(key="limit", types=['int'], require=True)
        self.assertTrue(len(args_ex) == 2)
        args.extend(args_ex)
        self.assertTrue(len(args) == 6)
        self.assertEqual(args[0]['key'], 'msg')
        self.assertEqual(args[5]['key'], 'limit')
        # extending with duplicates will ignore all duplicates
        args.extend(args_ex)
        self.assertTrue(len(args) == 6)
        self.assertEqual(args[0]['key'], 'msg')
        self.assertEqual(args[5]['key'], 'limit')
        # AssignBuilder can only be extended by other AssignBuilder
        self.assertRaises(NotImplementedError, args.extend, {"key": "test"})


class TestKwArgsHelperAsList(unittest.TestCase):

    def test_list_args(self):
        args = []
        args.append({"key": "msg", "types": ['str'], "require": True})
        args.append({"key": "age", "types": ['int'], "require": True})
        args.append({"key": "name", "types": ['str'], "default": "unknown"})
        args.append({"key": "city", "types": ['str'], "default": "North York"})
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
        args.append(key="msg", types=['str'], require=True)
        args.append(key="age", types=['int'], require=True)
        args.append(key="name", types=['str'], default="unknown")
        args.append(key="city", types=['str'], default="North York")
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

    def test_builder_with_rules(self):
        args = AssignBuilder()
        args.append(key="msg", types=['str'], require=True)
        args.append(key="age", types=['int'], require=True)
        args.append(key="name", rules=[rules.RuleStr], default="unknown")
        args.append(key="city", types=['str'], rules=[
                    rules.RuleStr], default="North York")
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

    def test_non_require(self):
        self._loop_count = -1
        r = Runner(file_name='data.html', name='Best Doc', loop_count=1)
        ab = AssignBuilder()
        ab.append(key='exporter', rules=[rules.RuleStr])
        ab.append(key='name', rules=[rules.RuleStr], default='unknown')
        ab.append(key='file_name', rules=[
                  rules.RuleStr, rules.RuleStrNotNullOrEmpty])
        ab.append(key='loop_count', rules=[
                  rules.RuleInt, rules.RuleIntPositive], default=self._loop_count)
        result = True
        # by default assign will raise errors if conditions are not met.
        for arg in ab:
            result = r.kw.assign(**arg)
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
        ab.append(key='exporter', rules=[rules.RuleStr])
        ab.append(key='name', rules=[rules.RuleStr], default='unknown')
        ab.append(key='file_name', rules=[
                  rules.RuleStr, rules.RuleStrNotNullOrEmpty])
        ab.append(key='loop_count', rules=[
                  rules.RuleInt, rules.RuleIntPositive], default=self._loop_count)
        result = True
        # by default assign will raise errors if conditions are not met.
        for arg in ab:
            result = r.kw.assign(**arg)
            if result == False:
                break
        if result == False:
            raise ValueError("Error parsing kwargs")
        self.assertTrue(result)
        self.assertFalse(r.kw.assign_true_not_required)


if __name__ == '__main__':
    unittest.main()
