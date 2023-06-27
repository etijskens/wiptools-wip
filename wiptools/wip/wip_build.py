# -*- coding: utf-8 -*-
import json
from pathlib import Path
import subprocess

import click

import wiptools.messages as messages
import wiptools.utils as utils


def wip_build(ctx: click.Context):
    """build binary extensions"""

    cookiecutter_params = utils.read_wip_cookiecutter_json()
    component = ctx.params['component']
    cpp_flag =  ctx.params['cpp']
    f90_flag =  ctx.params['f90']

    build = BinaryExtensionBuilder(cookiecutter_params)

    if component:
        # ignore language flags if set.
        if f90_flag:
            messages.warning_message("ignoring '--f90' flag")
        if f90_flag:
            messages.warning_message("ignoring '--cpp' flag")

        build(component)
        
    else:
        if not cpp_flag and not f90_flag:
            # No language flags set, and no component selected, hence build all binary components
            build.cpp_flag = build.f90_flag = True
        else:
            build.cpp_flag = cpp_flag
            build.f90_flag = f90_flag

        # iterate over all components and build if requested
        utils.iter_components(
            Path(cookiecutter_params['project_path']) / cookiecutter_params['package_name'],
            apply=build
        )


class BinaryExtensionBuilder:
    """A functor for building binary extension modules."""
    def __init__(self, cookiecutter_params):
        self.cookiecutter_params = cookiecutter_params
        self.f90_flag = False
        self.cpp_flag = False

    def __call__(self, path_to_component: Path):
        """Build this component's binary extension module."""
        component_type = utils.component_type(path_to_component)
        language = 'C++'            if (component_type == 'cpp' and self.cpp_flag) else \
                   'Modern Fortran' if (component_type == 'f90' and self.f90_flag) else \
                   None
        if language:
            with messages.TaskInfo(
                f"Building {language} binary extension `{path_to_component.relative_to(self.cookiecutter_params['project_path'])}`"
            ):
                self.build_ext(path_to_component)

    def build_ext(self, path_to_component):
        """Build binary extension module."""
        cmds = [
            "cmake -S . -B _cmake_build",
            "cmake --build _cmake_build",
            "cmake --install _cmake_build"
        ]
        with utils.in_directory(path_to_component):
            utils.subprocess_run_cmds(cmds)