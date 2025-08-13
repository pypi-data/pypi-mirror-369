"""This submodule is deprecated."""

from tamm import _compat

_compat.register_backward_compatibility_import(
    __name__,
    "ModelConfig",
    "tamm.layers.ModuleConfig",
)
