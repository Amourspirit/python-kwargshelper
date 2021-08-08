# coding: utf-8
from pathlib import Path
import sys
import os


def set_import_paths():
    script_path = Path(os.path.dirname(__file__)).parent
    test_path = script_path / "tests"
    src_path = script_path / "src"
    error_path = src_path / 'error'
    event_args_path = src_path / 'event_args'
    helper_path = src_path / 'helper'
    rules_path = src_path / 'rules'
    _paths = (test_path, script_path, src_path, error_path, event_args_path, helper_path, rules_path)
    i = 0
    for p in _paths:
        if not p in sys.path:
            sys.path.insert(i, str(p))
            i += 1

set_import_paths()
