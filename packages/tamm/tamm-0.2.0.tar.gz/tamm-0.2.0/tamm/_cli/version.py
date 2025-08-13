"""Command for printing tamm's version."""

from tamm import __version__
from tamm._cli.common import command


@command("version", help_text="Print tamm's version")
def print_version():
    print(__version__)
