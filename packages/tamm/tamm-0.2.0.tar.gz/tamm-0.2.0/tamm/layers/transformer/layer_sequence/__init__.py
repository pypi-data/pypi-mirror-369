"""
transformer.layer_sequence
^^^^^^^^^^^^^^^^^^^^^^^^^^

This submodule implements the sequence of transformer layers within a
:mod:`transformer stack <tamm.layers.transformer.stack>`.

Base class
==========

.. autoclass:: tamm.layers.transformer.BaseTransformerLayerSequence
    :members:


General layers
==============

.. autoclass:: tamm.layers.UniformTransformerLayerSequence
    :show-inheritance:

.. autoclass:: tamm.layers.TransformerLayerSequence
    :show-inheritance:

.. autoclass:: tamm.layers.SegmentedTransformerLayerSequence
    :show-inheritance:


KV reuse layer
==============

.. autoclass:: tamm.layers.KVReuseTransformerLayerSequence
    :show-inheritance:


Parallel track layers
=====================

.. autoclass:: tamm.layers.transformer.layer_sequence.ParallelTrackTransformerLayerSequenceConfig
    :show-inheritance:
    :members:
    :exclude-members: create_basic_builder

.. autoclass:: tamm.layers.transformer.layer_sequence.ParallelTrackTransformerSegment
    :show-inheritance:

.. autoclass:: tamm.layers.transformer.layer_sequence.parallel_track.UpdateAttentionMaskForParallelTracks
    :show-inheritance:
"""

from tamm.layers.transformer.layer_sequence.common import BaseTransformerLayerSequence
from tamm.layers.transformer.layer_sequence.kv_reuse import (
    KVReuseTransformerLayerSequence,
)
from tamm.layers.transformer.layer_sequence.parallel_track import (
    ParallelTrackTransformerLayerSequenceConfig,
    ParallelTrackTransformerSegment,
)
from tamm.layers.transformer.layer_sequence.segmented import (
    SegmentedTransformerLayerSequence,
)
from tamm.layers.transformer.layer_sequence.uniform import (
    UniformTransformerLayerSequence,
)
from tamm.layers.transformer.layer_sequence.vanilla import TransformerLayerSequence
