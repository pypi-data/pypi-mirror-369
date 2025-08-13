import copy as _copy
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch

from tamm.layers import basic as _basic_layers
from tamm.layers import common as _layers_common
from tamm.layers import functional as _tamm_F
from tamm.layers.common import builder as _builder
from tamm.layers.transformer.layer import TransformerLayer as _TransformerLayer
from tamm.layers.transformer.layer_sequence import segmented as _segmented
from tamm.layers.transformer.layer_sequence import vanilla as _vanilla
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class ParallelTrackTransformerLayerSequenceConfig(_layers_common.ModuleConfig):
    """
    A config for the transformer layer sequence of parallel track models.
    The resulting layer type is :class:`.SegmentedTransformerLayerSequence`, which
    divides the sequence into segments of type :class:`.ParallelTrackTransformerSegment`.
    The sequence expects inputs with shape ``(batch_size, seq_len, hidden_dim)``, and
    it outputs hidden states with the same shape.
    """

    sequence: _Tuple[_TransformerLayer.Builder, ...]
    """
    A (flattened) list of transformer layers for the model. The input and output
    hidden states for each layer should have shape
    ``(batch_size, num_tracks, seq_len, hidden_dim)``. Each layer computes
    its output for all of its tracks, typically in vectorized fashion.  The layers
    are not responsible for reducing hidden states across tracks.
    """

    num_tracks: int
    """The number of parallel tracks in the layer sequence"""

    num_layers_per_track_per_sync_point: int
    """
    The number of layers in each track between synchronization points, i.e.,
    the segment (block) size.
    """

    dispatch: _Union[_layers_common.LayerBuilder, None] = None
    """
    An optional builder for ``input_transform`` layers in each
    :obj:`.ParallelTrackTransformerSegment`.
    """

    combine: _Union[_layers_common.LayerBuilder, None] = None
    """
    An optional builder for ``output_transform`` layers in each
    :obj:`.ParallelTrackTransformerSegment`.
    """

    attention_types: _Optional[_Dict[int, str]] = None
    """
    A dictionary that maps transformer layer indices to their secondary attention types.
    For example if ``attention_types={3: "global", 7: "global"}, then layers 3 and 7
    receive the arguments
    ``attention_side_inputs=secondary_attention_side_inputs["global"]``
    rather than ``attention_side_inputs=attention_side_inputs``.  The
    ``secondary_positional_encodings`` layer of :class:`.TransformerStack` controls
    the available attention types.
    """

    output_hidden_states: bool = False
    """
    A flag for including outputs from each layer in the sequence output.  Defaults
    to ``False``.
    """

    @property
    def num_segments(self) -> int:
        """The number of synchronization points in the layer sequence."""
        num_layers_per_track = len(self.sequence)
        segment_size = self.num_layers_per_track_per_sync_point
        if num_layers_per_track % segment_size != 0:
            raise ValueError(
                f"num_layers_per_track_per_sync_point ({segment_size}) "
                "must evenly divide the number of transformer layers "
                f"({num_layers_per_track})"
            )
        return num_layers_per_track // segment_size

    def create_basic_builder(self) -> _builder.LayerBuilder:
        segments = [
            self._create_builder_for_segment(segment_idx)
            for segment_idx in range(self.num_segments)
        ]
        side_inputs_transform = UpdateAttentionMaskForParallelTracks.Builder(
            num_tracks=self.num_tracks
        )
        return _segmented.SegmentedTransformerLayerSequence.Builder(
            *segments, side_inputs_transform=side_inputs_transform
        )

    def _create_builder_for_segment(
        self, segment_idx: int
    ) -> _layers_common.LayerBuilder:
        segment_size = self.num_layers_per_track_per_sync_point
        start_layer_idx = segment_idx * segment_size
        end_layer_idx = start_layer_idx + segment_size

        builder = ParallelTrackTransformerSegment.Builder(
            *self.sequence[start_layer_idx:end_layer_idx],
            input_transform=_copy.deepcopy(self.dispatch),
            output_transform=_copy.deepcopy(self.combine),
            output_hidden_states=self.output_hidden_states,
        )
        if self.attention_types is not None:
            builder.attention_types = {
                idx: self.attention_types[layer_idx]
                for idx, layer_idx in enumerate(range(start_layer_idx, end_layer_idx))
                if layer_idx in self.attention_types
            }
        builder.num_tracks = self.num_tracks
        builder.kv_cache_start_layer_idx = segment_idx * segment_size * self.num_tracks
        return builder


class ParallelTrackTransformerSegment(_vanilla.TransformerLayerSequence):
    """
    A segment of parallel track transformer layers.  The segment expects inputs
    with shape ``(batch_size, seq_len, hidden_dim)``, and it outputs hidden states with
    the same shape.

    Args:
        *sequence (:obj:`.TransformerLayer.Builder`): A sequence of transformer layers
            for the segment.  The input and output shape for each layer is
            ``(batch_size, num_tracks, seq_len, hidden_dim)``. Each layer computes
            the outputs for all of its tracks, typically in vectorized fashion.
        input_transform (:obj:`.LayerBuilder` or :obj:`nn.Module`, optional): A layer for
            dispatching hidden states to all tracks.  The layer maps inputs of shape
            ``(batch_size, seq_len, hidden_dim)`` to per-track outputs of shape
            ``(batch_size, num_tracks, seq_len, hidden_dim)``.  If ``None``, the default
            layer replicates hidden states across tracks.
        output_transform (:obj:`.LayerBuilder` or :obj:`nn.Module`, optional): A layer for
            combining outputs across tracks. The layer maps inputs of shape
            ``(batch_size, num_tracks, seq_len, hidden_dim)`` to outputs of shape
            ``(batch_size, seq_len, hidden_dim)``.  If ``None``, the default layer
            takes the mean of hidden states across tracks.
        num_tracks (:obj:`int`): The number of parallel tracks.
        kv_cache_start_layer_idx (:obj:`int`): An offset for accessing the KV cache.
        output_hidden_states (:obj:`bool`): A flag for returning the hidden states after
            each layer.  Defaults to ``False``.
        attention_types (:obj:`dict`, optional): A dictionary that
            maps layer indices to their secondary attention types.  For example
            if ``attention_types={3: "global", 7: "global"},
            then layers 3 and 7 receive the arguments
            ``attention_side_inputs=secondary_attention_side_inputs["global"]``
            rather than ``attention_side_inputs=attention_side_inputs``.
    """

    def __init__(
        self,
        *sequence: _ModuleOrBuilder,
        input_transform: _OptionalModuleOrBuilder = None,
        output_transform: _OptionalModuleOrBuilder = None,
        num_tracks: int,
        kv_cache_start_layer_idx: int,
        output_hidden_states: bool = False,
        attention_types: _Optional[_Dict[int, str]] = None,
    ):
        self.num_tracks = num_tracks
        self.kv_cache_start_layer_idx = kv_cache_start_layer_idx

        if input_transform is None:
            input_transform = _basic_layers.ExpandDim.Builder(
                self.num_tracks, dim=1, unsqueeze=True
            )  # dispatches hidden states to all tracks
        if output_transform is None:
            output_transform = _basic_layers.Mean.Builder(
                dim=1
            )  # combines hidden states across tracks

        super().__init__(
            *sequence,
            input_transform=input_transform,
            output_transform=output_transform,
            output_hidden_states=output_hidden_states,
            attention_types=attention_types,
        )

    def extra_repr(self):
        pieces = [
            f"num_tracks={self.num_tracks}",
            f"kv_cache_start_layer_idx={self.kv_cache_start_layer_idx}",
        ]
        return ", ".join(pieces)

    def _get_cache_arg_for_layer(self, *, kv_cache, layer_idx):
        start_idx_for_layer = (
            self.kv_cache_start_layer_idx + self.num_tracks * layer_idx
        )
        end_idx_for_layer = start_idx_for_layer + self.num_tracks
        layer_indices = list(range(start_idx_for_layer, end_idx_for_layer))
        return kv_cache.at_layers(layer_indices)


class UpdateAttentionMaskForParallelTracks(_torch.nn.Module, _layers_common.LayerMixin):
    """
    A layer that updates attention mask tensors for parallel track architectures.
    Specifically, this layer replicates the attention mask intermediates for each track,
    resulting in a new shape of ``(batch_size, num_tracks, 1, kv_seq_len, query_seq_len)``
    (the ``1`` here is for the heads dimension, which is sometimes ``num_heads``).

    This layer works as a "side inputs transform" (see the ``side_inputs_transform``
    option of :class:`.Sequential`) of :class:`.BaseTransformerLayerSequence`.  This
    means that it receives all keyword arguments to the layer sequence and returns
    an updated version of them.

    Args:
        num_tracks (:obj:`int`): The number of parallel tracks.
    """

    def __init__(self, num_tracks: int):
        super().__init__()
        self.num_tracks = num_tracks

    def extra_repr(self):
        return f"num_tracks={self.num_tracks}"

    def forward(self, side_inputs: _Dict[str, _Any]):
        result = dict(side_inputs)
        result["attention_side_inputs"] = self._update_attention_side_inputs(
            side_inputs["attention_side_inputs"]
        )
        result["secondary_attention_side_inputs"] = {
            k: self._update_attention_side_inputs(v)
            for k, v in side_inputs.get("secondary_attention_side_inputs", {}).items()
        }
        return result

    def _update_attention_side_inputs(self, attention_side_inputs):
        mask = attention_side_inputs.get("attention_mask", None)
        if mask is None:
            return attention_side_inputs
        batch_size = mask.size(0)
        if mask.ndim == 3:
            mask = mask.unsqueeze(1)  # add a heads dimension if there isn't one yet
        if batch_size != 1:
            # In this branch we repeat rather than expand, which makes a copy
            # of the mask for each track.  We do this because our native_torch
            # SDPA flattens the batch and track dims together, and if we use
            # expand instead of replicate, this flatten will create copies of the
            # tensor anyway.  We do the copy here so that the copy happens only once.
            mask = mask.repeat_interleave(self.num_tracks, dim=0)
            mask = mask.unflatten(0, (batch_size, self.num_tracks))
        else:
            # An optimization for batch size 1.  We can use expand instead of repeat
            # because we can later flatten the batch and track dims without copying.
            mask = _tamm_F.expand_dim(mask, self.num_tracks, dim=1, unsqueeze=True)

        result = dict(attention_side_inputs)
        result["attention_mask"] = mask
        return result
