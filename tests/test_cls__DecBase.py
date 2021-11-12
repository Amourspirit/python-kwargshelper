import functools
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import _DecBase, _FnInstInfo


class TestGeneral(unittest.TestCase):

    def test_fn_err(self):
       class Dec(_DecBase):
           pass
       d = Dec()
       with self.assertRaises(ValueError):
           d.fn

    def test_cache(self):
        class Dec(_DecBase):
            def __call__(self, func: callable):
                super()._call_init(func=func)

                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    self._wrapper_init(args=args, kwargs=kwargs)
                    # twice for caching
                    assert isinstance(self.fn_inst_info, _FnInstInfo)
                    assert isinstance(self.fn_inst_info, _FnInstInfo)
                    return func(*args, **kwargs)
                return wrapper
        @Dec()
        def foo(*args):
            return [*args]
        result = foo(1, 2, 3)
        assert result[0] == 1
        

if __name__ == '__main__':
    unittest.main()
