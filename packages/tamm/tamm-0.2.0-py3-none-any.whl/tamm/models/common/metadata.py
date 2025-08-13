"""
This submodule is deprecated.  Please use tamm.layers.common.metadata
instead.
"""

from tamm import _compat

_compat.register_backward_compatibility_import(
    __name__,
    "ModelMetadata",
    "tamm.layers.common.metadata.ModuleMetadata",
)
