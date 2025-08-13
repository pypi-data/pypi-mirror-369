"""
Common functionality for the cli, including command and argument decorators for
defining new commands.
"""

import argparse
import functools
from typing import Optional

from tamm import _plugin
from tamm.context_vars import _plugin_init

PARSERS = {}
HEADER = r"""
  __
_/  |_ _____     _____    _____
\   __\\__  \   /     \  /     \
 |  |   / __ \_|  | |  \|  | |  \
 |__|  (______/|__|_|__/|__|_|__/

"""


def command(*command_path, help_text: Optional[str] = None):
    """
    A decorator for registering a command with the cli.

    Args:
        *command_path: strings that specify the command path.
        help_text: a brief description of the command.

    Example for adding a ``> tamm print hello`` subcommand:

        @command("print", "hello", help_text="Prints hello")
        def print_hello():
            print("Hello!")
    """

    def decorator(fn):
        if not isinstance(fn, Command):
            fn = Command(fn)
        fn.register(*command_path, help_text=help_text)
        return fn

    return decorator


def argument(*args, **kwargs):
    """
    A decorator for adding arguments to the cli command.

    Args:
        *args, **kwargs: Arguments for ArgumentParser.add_argument()
    """

    def decorator(fn):
        if not isinstance(fn, Command):
            fn = Command(fn)
        fn.add_argument(*args, **kwargs)
        return fn

    return decorator


def register_namespace_help_text(*command_path, help_text: str) -> None:
    """
    Register help text for a cli command path that does not implement
    a command function.

    Args:
        *command_path: strings that specify the command path.
        help_text: a brief description of the command.

    Example for a "publish" namespace:

        register_namespace_help_text(
            "publish", help_text="Commands for publishing objects"
        )

        @command("publish", "model", help_text="Publish a model")
        def publish_model():
            ...

        @command("publish", "preprocessor", help_text="Publish a preprocessor")
        def publish_model():
            ...
    """
    get_parser(*command_path, help_text=help_text)


def get_parser(*command_path, help_text=None):
    """
    Returns the parser for a subcommand.

    Args:
        *command_path: Strings that specify the command path.
    """
    try:
        return PARSERS[command_path]
    except KeyError:
        if not command_path:
            parser = argparse.ArgumentParser(prog="tamm")
        else:
            if len(command_path) == 1:
                help_text = _maybe_update_help_text_with_plugin_name(help_text)
            parent_parser = get_parser(*command_path[:-1])
            subparser = get_subparsers(parent_parser)
            parser = subparser.add_parser(command_path[-1], help=help_text)
        PARSERS[command_path] = parser
        return PARSERS[command_path]


def get_extended_root_parser() -> argparse.ArgumentParser:
    """Returns the root parser extended with plugin commands."""
    _plugin.register_cli_commands()
    return get_parser()


def _maybe_update_help_text_with_plugin_name(help_text: str):
    plugin_name = _plugin_init.get_initializing_plugin_module_name()
    if plugin_name is None:
        return help_text
    return f"{help_text} ({plugin_name} plugin command)"


@functools.cache
def get_subparsers(parser):
    """Creates and returns the subparsers object for a parser."""
    return parser.add_subparsers(title="subcommands")


class Command:
    """A class for wrapping a function and turning it into a tamm cli command."""

    def __init__(self, fn):
        self.fn = fn
        functools.update_wrapper(self, fn)
        self.arguments = []

    def register(self, *command_path, help_text=None):
        """Registers the command with the CLI"""
        parser = get_parser(*command_path, help_text=help_text)
        parser.set_defaults(func=self)
        for args, kwargs in self.arguments:
            parser.add_argument(*args, **kwargs)
        self.arguments = None

    def add_argument(self, *add_argument_args, **add_argument_kwargs):
        """
        Adds arguments to the command.

        Args:
            *args, **kwargs: Arguments for ArgumentParser.add_argument()
        """
        self.arguments.append((add_argument_args, add_argument_kwargs))

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)
