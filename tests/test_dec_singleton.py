import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from kwhelp.decorator import singleton, RuleCheckAll, DecFuncEnum
import kwhelp.rules as rules
from kwhelp.exceptions import RuleError


class TestRequiredDecorators(unittest.TestCase):

    def test_singleton(self):
        @singleton
        class Logger:
            def log(self, msg):
                print(msg)

        logger1 = Logger()
        logger2 = Logger()
        assert logger1 is logger2
    
    def test_singleton_rules(self):
        @singleton
        class Logger:
            @RuleCheckAll(rules.RuleStrNotNullEmptyWs, ftype=DecFuncEnum.METHOD)
            def log(self, msg):
                return msg

        logger1 = Logger()
        logger2 = Logger()
        assert logger1 is logger2
        result = logger1.log("hello")
        assert result == "hello"
        with self.assertRaises(RuleError):
            result = logger2.log("  ")







if __name__ == '__main__':
    unittest.main()
