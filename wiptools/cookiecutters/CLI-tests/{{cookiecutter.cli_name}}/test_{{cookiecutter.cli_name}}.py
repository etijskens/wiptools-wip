#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `{{cookiecutter.package_name}}.{{cookiecutter.cli_name}} ` CLI."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from click.testing import CliRunner

from {{cookiecutter.package_name}}.{{cookiecutter.cli_name}}.__main__ import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, ['-vv'])
    print(result.output)
    assert 'running' in result.output

# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (normally all tests are run with pytest)
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_main

    print(f"__main__ running {the_test_you_want_to_debug}")
    the_test_you_want_to_debug()
    print('-*# finished #*-')
# eof
