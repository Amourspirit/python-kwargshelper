# coding: utf-8
import unittest
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))

from kwhelp.checks import TypeChecker
from pathlib import Path


class TestTypeChecker(unittest.TestCase):

    def test_main(self):
        tc = TypeChecker(int, float)
        assert len(tc.types) == 2
        assert tc.validate(one=2, two=2.0) == True
        with self.assertRaises(TypeError):
            tc.validate(one=2, two="2")

        assert tc.validate(1, 3, 4.6, 5, 5.8) == True
        with self.assertRaises(TypeError):
            tc.validate(4.6, 5, 5.8, '')

    def test_types_none(self):
        tc = TypeChecker()
        # no checking takes place with types is None
        assert tc.validate(one=2, two=2.0) == True
        assert tc.validate(1, 3, 4.6, 5, 5.8) == True
        assert tc.validate(1, "a", int, self) == True

    def test_no_err(self):
        tc = TypeChecker(int, float, raise_error=False)
        assert tc.validate(one=2, two=2.0) == True
        assert tc.validate(one=2, two="2") == False
        assert tc.validate(4.6, 5, 5.8, '') == False
        tc.raise_error = True
        assert tc.raise_error == True
        with self.assertRaises(TypeError):
            tc.validate(4.6, 5, 5.8, '')

    def test_path(self):
        tc = TypeChecker(str, Path, type_instance_check=True)
        assert tc.type_instance_check == True
        str_path = "/home/user"
        assert tc.validate(str_path=str_path, p=Path(str_path)) == True
        tc.type_instance_check = False
        with self.assertRaises(TypeError):
            tc.validate(str_path=str_path, p=Path(str_path))
        tc.type_instance_check = True
        assert tc.validate(str_path=str_path, p=Path(str_path)) == True
        assert tc.validate(str_path, Path(str_path),
                           str_path=str_path, p=Path(str_path)) == True
        tc.type_instance_check = False
        with self.assertRaises(TypeError):
            tc.validate(str_path, Path(str_path))


if __name__ == '__main__':
    unittest.main()
