# -*- coding: utf-8 -*-

"""Tests for `helpers.py`."""

import os
from pathlib import Path
import shutil
import sys

path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(path))

import pytest

from helpers import run_wip, test_workspace
import wiptools.utils as utils

def test_test_workspace():
    path_to_test_workspace = test_workspace(clear=True)
    assert path_to_test_workspace.is_dir() == True  # .test-workspace must exist and be a directory
    assert not os.listdir(path_to_test_workspace)   # .test-workspace must be empty
    path_to_foo = path_to_test_workspace / 'foo'
    with open(path_to_foo, 'w') as f:
        f.write("blablabla")
        assert path_to_foo.is_file()
        path_to_foo = path_to_foo.resolve()

    assert path_to_foo.is_file()

    path_to_test_workspace = None
    path_to_test_workspace = test_workspace()
    assert path_to_test_workspace.is_dir() == True  # .test-workspace must exist and be a directory
    contents = os.listdir(path_to_test_workspace)
    print(contents)
    assert len(contents)                            # .test-workspace must NOT be empty

    # cleanup
    shutil.rmtree(path_to_test_workspace)
    assert path_to_test_workspace.exists() == False


def test_run_wip():
    run_wip(['--version'])
    print('-*##*-')

    run_wip(['--help'])
    print('-*##*-')


# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (normally all tests are run with pytest)
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_run_wip

    print(f"__main__ running {the_test_you_want_to_debug}")
    the_test_you_want_to_debug()
    print('-*# finished #*-')
# eof
