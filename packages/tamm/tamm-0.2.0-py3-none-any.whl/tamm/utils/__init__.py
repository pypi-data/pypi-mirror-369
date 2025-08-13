"""
tamm.utils
----------
"""

from tamm.utils import callable  # pylint: disable=redefined-builtin
from tamm.utils import (
    axlearn_utils,
    json,
    partial,
    timer,
    torch_utils,
    transformers_utils,
    user_dir_utils,
    vision_utils,
)
from tamm.utils._torch_compatibility import _is_same_device_type
from tamm.utils.optional_bool import OptionalBool
from tamm.utils.registry import RegistrySpec

__all__ = [
    "axlearn_utils",
    "json",
    "partial",
    "timer",
    "transformers_utils",
    "user_dir_utils",
    "vision_utils",
    "OptionalBool",
    "RegistrySpec",
]
