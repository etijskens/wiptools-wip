# -*- coding: utf-8 -*-
import json
from pathlib import Path
import subprocess

import click

import wiptools.messages as messages


def wip_env(ctx: click.Context):
    """Check the current environment for necessary components."""

    for cmd in ['python', 'git', 'gh']:
        completed_process = subprocess.run([cmd, '--version'])
        if completed_process.returncode:
            messages.error_message(f"Command `{cmd}` is missing from the current environment.", return_code=0)

    cmd = 'bumpversion'
    completed_process = subprocess.run([cmd, '-h'], capture_output=True)
    if not completed_process.returncode:
        lines = completed_process.stdout.decode('utf-8').split('\n')
        for line in lines:
            if 'bumpversion:' in line:
                print(line)
                break
