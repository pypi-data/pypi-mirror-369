"""
AO Layers
=========

.. autoclass:: tamm.ao.layers.KVQuantizer
    :members:

.. autoclass:: tamm.ao.layers.QuantizingKVCacher
    :members:

.. autoclass:: tamm.ao.layers.FakeQuantize
    :members:

.. autoclass:: tamm.ao.layers.SimpleEMAMinMaxObserver
    :members:

.. autoclass:: tamm.ao.layers.SimpleEMAPerChannelMinMaxObserver
    :members:

.. autofunction:: tamm.ao.layers.functional.fake_quantize
"""

import tamm.ao.layers.functional
from tamm.ao.layers.fake_quantize import (
    FakeQuantize,
    SimpleEMAMinMaxObserver,
    SimpleEMAPerChannelMinMaxObserver,
)
from tamm.ao.layers.kv_quantizer import KVQuantizer
from tamm.ao.layers.quantizing_kv_cacher import QuantizingKVCacher

__all__ = [
    "KVQuantizer",
    "QuantizingKVCacher",
    "FakeQuantize",
    "SimpleEMAMinMaxObserver",
    "SimpleEMAPerChannelMinMaxObserver",
]
