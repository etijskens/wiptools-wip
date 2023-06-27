# -*- coding: utf-8 -*-

import contextlib
import os
from pathlib import Path
import shutil
import traceback
import uuid

from click.testing import CliRunner

import wiptools
from wiptools.cli.wip import main as wip_main


def test_workspace(clear: bool = False):
    """Return the path to the test workspace 'wiptools/.test-workspace` in the project directory.

    Args:
        clear: make sure that the test workspace is empty

    Returns:
        the path to the test workspace.
    """
    test_workspace_path = (Path(wiptools.__file__).parent.parent / '.test-workspace').resolve()

    if clear and test_workspace_path.exists():
        shutil.rmtree(test_workspace_path)

    test_workspace_path.mkdir(exist_ok=True)

    return test_workspace_path


# @contextlib.contextmanager
# def in_empty_tmp_dir(cleanup=True):
#     """A context manager that creates a temporary folder and changes
#     the current working directory to it for isolated filesystem tests.
#
#     :param bool cleanup: if True the temporary folder is removed on exit,
#         otherwise a message is printed.
#     """
#     cwd = Path.cwd()
#     uu = uuid.uuid4()
#     tmp = cwd / f'__{uu}'
#     if tmp.exists():
#         shutil.rmtree(tmp)
#     tmp.mkdir(parents=True, exist_ok=True)
#     os.chdir(tmp)
#     print("Switching cwd to", tmp)
#     try:
#         yield tmp
#     finally:
#         print("Switching cwd back to", cwd)
#         os.chdir(cwd)
#         if cleanup:
#             try:
#                 shutil.rmtree(tmp)
#             except (OSError, IOError):
#                 pass
#         else:
#             print(f"Leftover: {tmp}")
        

# def get_version(path_to_file,verbose=False):
#     version = '?'
#     p = str(path_to_file)
#     if p.endswith('.toml'):
#         tomlfile = TomlFile(path_to_file)
#         content = tomlfile.read()
#         version = content['tool']['poetry']['version']
#     else:
#         if p.endswith('.py'):
#             with open(str(p)) as f:
#                 lines = f.readlines()
#                 ptrn = re.compile(r"__version__\s*=\s*['\"](.*)['\"]\s*")
#                 for line in lines:
#                     mtch = ptrn.match(line)
#                     if mtch:
#                         version = mtch[1]
#     if verbose:
#         print(f"%% {path_to_file} : version : ({version})")
#     return version


def run_wip(arguments, stdin=None, assert_exit_code=True):
    """
    helper function to run cli_micc.py with arguments
    """
    print(f"wiptools.cli.helpers.run_wip: running `{' '.join(arguments)}`")

    runner = CliRunner()
    result = runner.invoke(wip_main, arguments, input=stdin)

    print(result.output)

    if result.exception:
        if result.stderr_bytes:
            print(result.stderr)
        print('exit_code =', result.exit_code)
        print(result.exception)
        traceback.print_tb(result.exc_info[2])
        print(result.exc_info[2])

    if assert_exit_code:
        if result.exit_code:
            raise AssertionError(f"result.exit_code == {result.exit_code}")

    return result


# ==============================================================================
if __name__ == "__main__":
    pass

# eof #
