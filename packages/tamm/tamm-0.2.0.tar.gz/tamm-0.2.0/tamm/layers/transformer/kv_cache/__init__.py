"""
transformer.kv_cache
^^^^^^^^^^^^^^^^^^^^

This module implements key-value cache components to speed up streaming inference with
causal transformer stacks.  Language model text generation is an important example of
this.


Base classes
~~~~~~~~~~~~

These classes define the interface for KV caching.

.. autoclass:: tamm.layers.transformer.BaseKVCache
    :members:

.. autoclass:: tamm.layers.transformer.BaseKVCacheView
    :members:

.. autoclass:: tamm.layers.transformer.KVCacheLayerView
    :members:


Vanilla cache implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These classes provide a simple cache implementation that covers basic inference
scenarios.

.. autoclass:: tamm.layers.transformer.VanillaKVCache
    :members:
    :show-inheritance:

.. autoclass:: tamm.layers.transformer.VanillaKVCacheView
    :members:
    :show-inheritance:
"""

from tamm.layers.transformer.kv_cache.common import (
    BaseKVCache,
    BaseKVCacheView,
    KVCacheLayerView,
)
from tamm.layers.transformer.kv_cache.speculative import (
    SpeculativeKVCache,
    SpeculativeKVCacheView,
)
from tamm.layers.transformer.kv_cache.v0 import V0KVCache, V0KVCacheView
from tamm.layers.transformer.kv_cache.vanilla import VanillaKVCache, VanillaKVCacheView
