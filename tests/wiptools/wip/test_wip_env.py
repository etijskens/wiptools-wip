# -*- coding: utf-8 -*-

"""Tests for `wip env`."""

from pathlib import Path
import sys

path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(path))

import pytest

from helpers import run_wip, test_workspace
import wiptools.utils as utils


def test_env():
    result = run_wip(['env'], assert_exit_code=False)


# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (normally all tests are run with pytest)
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_env

    print(f"__main__ running {the_test_you_want_to_debug}")
    the_test_you_want_to_debug()
    print('-*# finished #*-')
