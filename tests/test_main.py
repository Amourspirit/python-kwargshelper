# coding: utf-8
try:
    import path_imports
except:
    pass
import unittest
from src.kwargs_helper import KwargsHelper

class Runner:
    def __init__(self, **kwargs):
        self._kw = KwargsHelper(self,{**kwargs})
    
    @property
    def kw(self) -> KwargsHelper:
        return self._kw
            

class TestKwArgsHelper(unittest.TestCase):

    def test_msg_hello_wolrd(self):
        r = Runner(msg='Hello World')
        r.kw.add(key='msg',types=['str'])
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')

    def test_msg_fast(self):
        r = Runner(msg='Hello World')
        r.kw.add(key='msg', types=['str'])
        # default should ignore required
        r.kw.add(key='fast', field='l__fst',types=['str'],default=True,require=True)
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, 'l__fst'))
        self.assertTrue(r.l__fst)
    
    def test_age_required_error(self):
        r = Runner(msg='Hello World')
        r.kw.add(key='msg',types=['str'])
        self.assertRaises(ValueError, r.kw.add, key='age',types=['int'],require=True)
    
    def test_age_required(self):
        r = Runner(msg='Hello World', age=2)
        r.kw.add(key='msg', types=['str'], require=True)
        r.kw.add(key='age', types=['int'], require=True)
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._msg, 'Hello World')
        self.assertTrue(hasattr(r, '_msg'))
        self.assertEqual(r._age, 2)


if __name__ == '__main__':
    unittest.main()
