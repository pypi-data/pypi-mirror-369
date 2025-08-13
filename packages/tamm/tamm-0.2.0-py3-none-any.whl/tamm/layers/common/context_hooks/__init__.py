"""
Builder Context Hooks
---------------------

.. autoclass:: tamm.layers.common.DefaultDeviceContextHook
    :members:
    :show-inheritance:

.. autoclass:: tamm.layers.common.DtypeContextHook
    :members:
    :show-inheritance:

.. autoclass:: tamm.layers.common.PretrainedContextHook
    :members:
    :show-inheritance:

.. autoclass:: tamm.layers.common.UseMetaInitTrickContextHook
    :members:
    :show-inheritance:
"""

from tamm.layers.common.context_hooks.default_device import DefaultDeviceContextHook
from tamm.layers.common.context_hooks.dtype import DtypeContextHook
from tamm.layers.common.context_hooks.freeze_params import FreezeParamsContextHook
from tamm.layers.common.context_hooks.pretrained import PretrainedContextHook
from tamm.layers.common.context_hooks.use_meta_init_trick import (
    UseMetaInitTrickContextHook,
)

__all__ = [
    "DefaultDeviceContextHook",
    "DtypeContextHook",
    "PretrainedContextHook",
    "UseMetaInitTrickContextHook",
    "FreezeParamsContextHook",
]
