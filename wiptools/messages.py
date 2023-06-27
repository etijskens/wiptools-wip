import sys

import click

def error_message(message: str, return_code:int = 1):
    """Print an error message and exit if return_code is non-zero."""
    click.secho(f"\nERROR: {message}", fg='red')
    if return_code:
        click.secho(f"ERROR: exiting ({return_code=})", fg='red')
        sys.exit(return_code)

def warning_message(message:str, return_code:int = 0):
    """Print a warning message."""
    click.secho(f"\nWARNING: {message}", fg='cyan')
    if return_code:
        click.secho(f"WARNING: exiting ({return_code=})", fg='red')
        sys.exit(return_code)

class TaskInfo:
    """Context manager class for printing a message before and after a task """
    def __init__(self, message: str, fg='green'):
        self.message = message
        self.fg = fg
    def __enter__(self):
        click.secho(f"\n[[{self.message}...", fg=self.fg)
    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_value:
            click.secho(f"]] (FAILED {self.message})", fg='red')
        else:
            click.secho(f"]] (done {self.message})", fg=self.fg)


def ask(question: str, type=str, default=None):
    """Ask a question and return the answer as `type`."""

    if default is None:
        answer = click.prompt(text=question, type=type)
    else:
        answer = click.prompt(text=question, default=default)

    return answer

