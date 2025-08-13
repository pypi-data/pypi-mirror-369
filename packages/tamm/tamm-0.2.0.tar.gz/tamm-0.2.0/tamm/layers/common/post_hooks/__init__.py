"""
Builder Post Hooks
------------------
.. autofunction:: tamm.layers.common.get_model_adapters_post_hook

.. autoclass:: tamm.layers.common.AttachConfigPostHook
    :members:
    :show-inheritance:

.. autoclass:: tamm.layers.common.AttachMetadataPostHook
    :members:
    :show-inheritance:

.. autoclass:: tamm.layers.common.FreezeParamsPostHook
    :members:
    :show-inheritance:

.. autoclass:: tamm.layers.common.ArchOptimizersPostHook
    :members:
    :show-inheritance:

.. autoclass:: tamm.layers.common.ModelInitializerPostHook
    :members:
    :show-inheritance:
"""
from tamm.layers.common.post_hooks.adapters import get_model_adapters_post_hook
from tamm.layers.common.post_hooks.arch_optimizer import ArchOptimizersPostHook
from tamm.layers.common.post_hooks.attach_config import AttachConfigPostHook
from tamm.layers.common.post_hooks.attach_metadata import AttachMetadataPostHook
from tamm.layers.common.post_hooks.common import CompositePostHook, IdentityPostHook
from tamm.layers.common.post_hooks.freeze_params import FreezeParamsPostHook
from tamm.layers.common.post_hooks.model_initializer import ModelInitializerPostHook

__all__ = [
    "get_model_adapters_post_hook",
    "ArchOptimizersPostHook",
    "FreezeParamsPostHook",
    "AttachConfigPostHook",
    "AttachMetadataPostHook",
    "ModelInitializerPostHook",
    "IdentityPostHook",
    "CompositePostHook",
]
