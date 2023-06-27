# -*- coding: utf-8 -*-
import os
from pathlib import Path
import shutil
import subprocess

import click
from cookiecutter.main import cookiecutter

import wiptools.messages as messages
import wiptools.utils as utils


def wip_add(ctx: click.Context):
    """Add submodules and CLIs."""


    flag_py     = ctx.params['py']
    flag_cpp    = ctx.params['cpp']
    flag_f90    = ctx.params['f90']
    flag_cli    = ctx.params['cli']
    flag_clisub = ctx.params['clisub']
    nflags_set = flag_py + flag_cpp + flag_f90 + flag_cli + flag_clisub
    if nflags_set > 1:
        messages.error_message(
            "It is illegal to specify more than one component flags\n"
            "(--py|--cpp|--f90|--cli|--clisub"
        )

    cookiecutter_params = utils.read_wip_cookiecutter_json()
    project_path = Path.cwd()
    package_name = cookiecutter_params['package_name']
    component = ctx.params['component'] # path to module relative to package directory

    if flag_py or flag_cpp or flag_f90:

        module_path = project_path / package_name / component
        module_name = module_path.name
        parent_module_path = module_path.parent
        parent_module_path_relative = parent_module_path.relative_to(project_path)
        parent_pypath = str(parent_module_path.relative_to(project_path)).replace(os.sep,'.') + '.'

        if not module_path.parent.is_dir():
            messages.error_message(f"The parent directory `{module_path.parent}` does not exist.")

        cookiecutter_params.update(
          { 'module_name' : module_name
          , 'parent_pypath'  : parent_pypath
          }
        )

        template = str(utils.cookiecutters() / 'module-py' ) if flag_py  else \
                   str(utils.cookiecutters() / 'module-cpp') if flag_cpp else \
                   str(utils.cookiecutters() / 'module-f90')

        with messages.TaskInfo(f"Expanding cookiecutter template `{template}`"):
            cookiecutter( template=template
                        , extra_context=cookiecutter_params
                        , output_dir=parent_module_path
                        , no_input=True
                        , overwrite_if_exists=True
                        )

        template = (utils.cookiecutters() / 'module-py-tests' ) if flag_py  else \
                   (utils.cookiecutters() / 'module-cpp-tests') if flag_cpp else \
                   (utils.cookiecutters() / 'module-f90-tests')

        with messages.TaskInfo(f"Expanding cookiecutter template `{template.relative_to(utils.wiptools())}`"):
            output_dir = project_path / 'tests' / parent_module_path_relative
            cookiecutter( template=str(template)
                        , extra_context=cookiecutter_params
                        , output_dir=output_dir
                        , no_input=True
                        , overwrite_if_exists=True
                        )

    elif flag_cli or flag_clisub:

        cli_name = component

        cookiecutter_params.update(
            {'cli_name': cli_name}
        )

        template = (utils.cookiecutters() / 'CLI'   ) if flag_cli else \
                   (utils.cookiecutters() / 'CLIsub')

        with messages.TaskInfo(f"Expanding cookiecutter template `{template.relative_to(utils.wiptools())}`"):
            cookiecutter(template=str(template)
                         , extra_context=cookiecutter_params
                         , output_dir=project_path / package_name
                         , no_input=True
                         , overwrite_if_exists=True
                         )

        template = (utils.cookiecutters() / 'CLI-tests') if flag_cli else \
                   (utils.cookiecutters() / 'CLIsub-tests')

        with messages.TaskInfo(f"Expanding cookiecutter template `{template.relative_to(utils.wiptools())}`"):
            cookiecutter(template=str(template)
                         , extra_context=cookiecutter_params
                         , output_dir=project_path / 'tests' / package_name
                         , no_input=True
                         , overwrite_if_exists=True
                         )

        with messages.TaskInfo("Updating pyproject.toml"):
            with utils.PyProjectTOML("rw") as pyproject:
                script = f"{package_name}.{cli_name}.__main__:main"
                pyproject.toml['tool']['poetry']['scripts'][cli_name] = script

    # check for mkdocs documentation first
    docs_format = utils.docs_format()
    if docs_format == 'md':
        with messages.TaskInfo("updating `docs/api-reference.md`"):
            path_to_api_reference_md = project_path / 'docs' / 'api-reference.md'
            path_to_component = project_path / package_name / component
            if utils.component_type(path_to_component) == 'py':
                with path_to_api_reference_md.open(mode="a") as fp:
                    p = str(path_to_component.relative_to(project_path)).replace(os.sep, '.')
                    fp.write(f'::: {p}')
            # not sure what to do in the other cases

    elif docs_format == 'rst':
        messages.warning_message("RestructuredText documentation generation is not (yet) implemented.")
