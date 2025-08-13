"""
Command for cleaning cache or temporary directories
"""

import shutil as _shutil
from pathlib import Path as _Path

from tamm._cli.common import argument, command
from tamm.utils import user_dir_utils


@command("clean", help_text="Clean cache or temporary directories")
@argument(
    "entity",
    nargs="?",
    choices=["cache", "tempdir", "all"],
    default="all",
    help="The location(s) to clean",
)
def clean(entity):
    paths = {}
    if entity == "cache":
        paths["cache"] = user_dir_utils.get_tamm_cache_dir()
    elif entity == "tempdir":
        paths["tempdir"] = user_dir_utils.get_tamm_tmp_dir()
    elif entity == "all":
        paths["tempdir"] = user_dir_utils.get_tamm_tmp_dir()
        paths["cache"] = user_dir_utils.get_tamm_cache_dir()
    else:
        raise ValueError(f"Unknown entity type '{entity}'. Cannot clean this path.")

    for name, path in paths.items():
        print(f"Cleaning '{name}': {path}")
        _shutil.rmtree(path, ignore_errors=False)
        _Path(path).mkdir(parents=True, exist_ok=True)
