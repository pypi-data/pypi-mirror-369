"""
Model mixin
-----------

.. autoclass:: tamm.models.common.ModelMixin
    :members:
"""
from tamm.models.common.mixin import ModelMixin

__all__ = ["ModelMixin"]


# DEPRECATED
# isort: off
# pylint: disable=all
from tamm import _compat
from tamm.models.common import metadata

_compat.register_backward_compatibility_import(
    __name__,
    "ModelMetadata",
    "tamm.layers.common.metadata.ModuleMetadata",
)

from tamm.models.common import config

_compat.register_backward_compatibility_import(
    __name__,
    "ModelConfig",
    "tamm.layers.ModuleConfig",
)

__all__.append("ModelConfig")
