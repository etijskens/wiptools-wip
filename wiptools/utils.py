from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import subprocess

# try:
#     import tomllib
# except ModuleNotFoundError:
#     import tomli as tomllib
# import tomli_w as tomli_w
import tomlkit
from typing import List, Union, Tuple, Callable

import click

import wiptools.messages as messages

@contextmanager
def in_directory(path):
    """Context manager for changing the current working directory while the body of the
    context manager executes.
    """
    previous_dir = Path.cwd()
    os.chdir(path) # the str method takes care of when path is a Path object
    try:
        yield Path.cwd()
    finally:
        os.chdir(previous_dir)


def wiptools():
    """Return the path to the wiptools package."""
    return cookiecutters().parent

def cookiecutters():
    """Return the path to the cookiecutter templates"""
    return Path(__file__).parent / 'cookiecutters'

def pat(github_username):
    """Return the personal access token for github.com/{github_username} from the standard location."""
    return Path.home() / '.wiptools' / f'{github_username}.pat'

def verify_project_name(project_name: str) -> bool:
    """Project names must start with a char, and contain only chars, digits, underscores and dashes.

    Args:
        project_name: name of the current project
    """
    p = re.compile(r"\A[a-zA-Z][a-zA-Z0-9_-]*\Z")
    return bool(p.match(project_name))


def pep8_module_name(module_name: str)->str:
    """Convert a module name to a PEP8 compliant module name.

    Conversion implies:

    * -> lowercase
    * dash -> underscore

    If the conversion is not possible, the function exits with a non-zero exit code.

    This function is typically called to convert a project name to a PE8 compliant module name.

    Args:
        module_name to be converted

    Returns:
        PEP8 compliant version of module_name.
    """

    pep8_name = module_name\
        .lower()\
        .replace('-', '_')

    p = re.compile(r"\A[a-z][a-z0-9_]*\Z")
    if not bool(p.match(pep8_name)):
        messages.error_message(f"Module name '{module_name}' could not be made PEP8 compliant.")

    return pep8_name


def get_config(config_path: Path, needed: dict = {}) -> dict:
    """Get cookiecutter parameters from a config file and prompt for missing parameters.

    Args:
        config_path: path to config file. If it does not exist, the user is prompted for all needed parameters
            and the answers are saved to config_path.

        needed: (key, kwargs) pairs. Each key is the name of a needed parameter, and kwargs is a dict passed as
            messages.ask(**kwargs) to prompt the user for parameters missing from the config file in config_path.

    Returns:
         a dictionary with (cookiecutter_parameter_name, value) pairs.
    """

    save = False
    if config_path.is_file():
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = {}
        if config_path:
            save = True

    header = False
    for cookiecutter_parameter, kwargs in needed.items():
        if not cookiecutter_parameter in config:
            if not header:
                click.secho("\nDeveloper info needed:")
                header = True
            config[cookiecutter_parameter] = messages.ask(**kwargs)

    if save:
        config_path.parent.mkdir(parents=True)
        with open(config_path, mode='w') as f:
            json.dump(config, f, indent=2)

    return config

def read_wip_cookiecutter_json() -> dict:
    """Read the `wip-cookiecutter.json` file. Exits if missing.

    This function also serves as a test that the current working directory is a wip project directory.
    """
    try:
        with open(Path.cwd() / 'wip-cookiecutter.json') as fp:
            cookiecutter_params = json.load(fp)
            if Path.cwd().name != cookiecutter_params['project_name']:
                messages.error_message("Path.cwd().name != cookiecutter_params['project_name']: This is unexpected.")
            cookiecutter_params['project_path'] = str(Path.cwd())
            return cookiecutter_params
            # The project path is not needed by cookiecutter, but it is practical to have available.

    except FileNotFoundError:
        messages.error_message(f"Current working directory does not contain a `wip-cookiecutter.json` file.\n"
                               f"Not a wip project?"
                              )

def subprocess_run_cmds(
        cmds: Union[ str                    # a command string
                   , Tuple[str,dict]        # a (command string, kwargs) pair
                   , List[Union[str,Tuple[str,dict]]]  # a list of the above
                   ],
    ):
    """Run a series of commands using subprocess.run, optionally with kwargs, and exit on failure."""

    if isinstance(cmds, (str, tuple)):
        cmds = [cmds]

    for cmd in cmds:
        if isinstance(cmd, str):
            # a command without kwargs
            command = cmd
            with messages.TaskInfo(f"Running `{command}` in directory {Path.cwd()}"):
                completed_process = subprocess.run(command, shell=True)
        else:
            # a command with kwargs
            command = cmd[0]
            kwargs  = cmd[1]
            with messages.TaskInfo(f"Running `{command} {kwargs=}` in directory {Path.cwd()}"):
                completed_process = subprocess.run(command, shell=True, **kwargs, )

        if completed_process.returncode:
            messages.error_message(f'Command `{command}` failed')


def read_pyproject_toml():
    """"""
    with open('pyproject.toml', mode='r') as fp:
        toml = tomlkit.load(fp=fp)
        return toml
def write_pyproject_toml(toml: dict):
    """"""
    with open('pyproject.toml', mode='w') as fp:
        tomlkit.dump(toml, fp=fp)

class PyProjectTOML:
    """Context manager class for  """
    def __init__(self, mode="r"):
        self.mode = mode
    def __enter__(self):
        if 'r' in self.mode:
            self.toml = read_pyproject_toml()
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        if 'w' in self.mode:
            write_pyproject_toml(self.toml)

def docs_format() -> str:
    """Return the documentation format.

    Returns:
        `md` for markdowm (with `mkdocs`), `rst` for restructuredText (with `sphinx`). Empty string otherwise.
    """
    if (Path.cwd() / 'mkdocs.yml').is_file():
        return 'md'
    elif (Path.cwd() / 'docs' / 'conf.py').is_file():
        return 'rst'
    else:
        return ''

def component_type(path_to_component):
    """return the type of a component directory."""
    if list(path_to_component.glob('*.cpp')):
        return 'cpp'
    elif list(path_to_component.glob('*.f90')):
        return 'f90'
    elif list(path_to_component.glob('__init__.py')):
        return 'py'
    elif list(path_to_component.glob('__main__.py')):
        return 'cli'
    else:
        return ''

def component_string(component: Path, type: str = ''):
    type_ = type if type else component_type(component)
    d = {
        'py': 'Python module'
      , 'cli': 'CLI'
      , 'cpp': 'C++ binary extension module'
      , 'f90': 'Modern Fortran binary extension module'
    }
    s = f"{component.name} [{d.get(type_, '???')}]"
    # print(s)
    return s

def iter_components(path: Path, apply: Callable):
    for entry in path.iterdir():
        if entry.is_dir():
            comp_type = component_type(entry)
            if comp_type:
                apply(entry)
                iter_components(entry, apply=apply)

