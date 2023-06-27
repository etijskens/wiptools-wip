# -*- coding: utf-8 -*-
import json
from pathlib import Path
from typing import Callable

import click

import wiptools.messages as messages
import wiptools.utils as utils


def wip_info(ctx: click.Context):
    """get info about the project's structure."""

    cookiecutter_params = utils.read_wip_cookiecutter_json()

    project_path = Path.cwd()
    package_name = cookiecutter_params['package_name']

    # project version
    toml = utils.read_pyproject_toml()
    version    = toml['tool']['poetry']['version']
    repository = toml['tool']['poetry']['repository']
    homepage   = toml['tool']['poetry']['homepage']
    print(f"Project    : {project_path.name}")
    print(f"Version    : {version}")
    print(f"Package    : {package_name}")
    print(f"GitHub repo: {'--' if not repository else repository}")
    print(f"Home page  : {'--' if not homepage else homepage}")
    print(f"Location   : {project_path}")

    # Package structure
    click.secho(f"\nStructure of Python package {package_name}", fg='bright_blue')
    paths = DisplayablePath.make_tree(
        project_path / package_name
      , criteria=criteria
    )
    for path in paths:
        click.echo('  ' + path.displayable())

def criteria(path: Path):
    if path.is_dir():
        return path.name != '__pycache__'
    else:
        return path.suffix in ['.py', '.cpp', '.f90', '.md', 'rst']


class DisplayablePath:
    """Class for printing the tree structure of a python package.

    Adapted from https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python.
    """
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path: Path, parent_path: Path, is_last: bool):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            component_string = utils.component_string(self.path)
            return click.style(component_string, fg='blue')
        return click.style(self.path.name, fg='cyan')

    @classmethod
    def make_tree( cls,
        root: Path,
        parent: Path=None,
        is_last: bool=False,
        criteria: Callable=None
    ):
        """Create a generator that produces a tree structure of a python package."""
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(
            list(path for path in root.iterdir() if criteria(path)),
            key=lambda s: str(s).lower()
        )
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path: Path):
        return True

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))
