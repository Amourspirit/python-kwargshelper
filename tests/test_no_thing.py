# coding: utf-8
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.helper import NoThing, NO_THING

class TestKwArg(unittest.TestCase):

    def test_assign_hello_world(self):
        nutton = NoThing()
        no_thing = NoThing()
        self.assertEqual(nutton, no_thing)
        self.assertEqual(NO_THING, nutton)
        self.assertEqual(NO_THING, no_thing)
        self.assertIs(nutton, NO_THING)

if __name__ == '__main__':
    unittest.main()
