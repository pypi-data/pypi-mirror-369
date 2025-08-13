"""
Command for listing contents of tamm registries (such as the available models or
tokenizers).
"""

from tamm._cli._listers import get_registered_listers, get_registered_listers_names
from tamm._cli.common import argument, command

# pylint: disable=redefined-builtin


@command("ls", help_text="List a tamm object registry")
@argument("-w", "--wide", action="store_true", help="Disable output truncation")
@argument("-l", "--long", action="store_true", help="Include descriptions")
@argument(
    "-d", "--show-deprecated", action="store_true", help="Include deprecated items"
)
@argument("-a", "--all", action="store_true", help="Include all discoverable items")
@argument("registry", type=str, choices=get_registered_listers_names())
def list_subcommand(registry, all, long, wide, show_deprecated):
    get_registered_listers()[registry](all, long, wide, show_deprecated).print()
