"""
Layer Utilities
---------------

.. autoclass:: tamm.layers.common.LayerBuilder
    :members:
    :show-inheritance:

.. autoclass:: tamm.layers.common.ModuleConfig
    :members:
    :inherited-members:

.. autoclass:: tamm.layers.common.LayerMixin
    :members:
    :show-inheritance:

.. autoclass:: tamm.layers.common.BuildableMixin
    :members:
    :show-inheritance:

.. autoclass:: tamm.layers.common.ConfigurableLayerMixin
    :members:

.. autoclass:: tamm.layers.common.PretrainedLoader

.. autoclass:: tamm.layers.common.ModuleMetadata

.. autofunction:: tamm.layers.common.map_configs_to_builders


Module Markers
^^^^^^^^^^^^^^

.. autofunction:: tamm.layers.common.init_marker
.. autofunction:: tamm.layers.common.update_marker
.. autofunction:: tamm.layers.common.get_marker

.. autoclass:: tamm.layers.common.ModuleMarker
    :members:

.. automodule:: tamm.layers.common.context_hooks
.. automodule:: tamm.layers.common.post_hooks
"""

from tamm.layers.common import typing
from tamm.layers.common._marker import (
    ModuleMarker,
    get_marker,
    init_marker,
    update_marker,
)
from tamm.layers.common._utils import map_configs_to_builders
from tamm.layers.common.builder import BuildableMixin, LayerBuilder
from tamm.layers.common.config import ModuleConfig
from tamm.layers.common.context_hooks import (
    DefaultDeviceContextHook,
    DtypeContextHook,
    PretrainedContextHook,
    UseMetaInitTrickContextHook,
)
from tamm.layers.common.metadata import ModuleMetadata
from tamm.layers.common.mixins import (
    ConfigurableLayerMixin,
    LayerMixin,
    _BaseConfigurableMixin,
)
from tamm.layers.common.post_hooks import (
    ArchOptimizersPostHook,
    AttachConfigPostHook,
    AttachMetadataPostHook,
    FreezeParamsPostHook,
    ModelInitializerPostHook,
    get_model_adapters_post_hook,
)
from tamm.layers.common.pretrained_loader import PretrainedLoader

__all__ = [
    "LayerBuilder",
    "LayerBuilder",
    "LayerMixin",
    "BuildableMixin",
    "metadata",
    "ConfigurableLayerMixin",
    "ArchOptimizersPostHook",
    "AttachConfigPostHook",
    "AttachMetadataPostHook",
    "FreezeParamsPostHook",
    "ModelInitializerPostHook",
    "ModuleMetadata",
    "get_model_adapters_post_hook",
    "DefaultDeviceContextHook",
    "PretrainedContextHook",
    "UseMetaInitTrickContextHook",
    "PretrainedLoader",
    "DtypeContextHook",
    "ModuleMarker",
    "ModuleConfig",
    "init_marker",
    "update_marker",
    "get_marker",
    "_BaseConfigurableMixin",
    "map_configs_to_builders",
    "typing",
]


# DEPRECATED
# pylint: disable=all
# isort: off

from tamm import _compat

_compat.register_backward_compatibility_import(
    __name__,
    "LayerConfig",
    "tamm.layers.common.config.ModuleConfig",
)

__all__.append("LayerConfig")
