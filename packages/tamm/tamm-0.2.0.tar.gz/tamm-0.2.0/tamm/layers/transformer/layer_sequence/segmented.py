import itertools as _itertools
from typing import Iterator as _Iterator

import torch as _torch

from tamm.layers import sequential as _sequential
from tamm.layers.transformer.layer_sequence import common as _common
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class SegmentedTransformerLayerSequence(
    _sequential.Sequential, _common.BaseTransformerLayerSequence
):
    """
    A composite sequence of :class:`.BaseTransformerLayerSequence` layers.
    Each child is called a "segment".  The layer forwards all keyword arguments
    to its child segments.

    Args:
        *segments (:obj:`.LayerBuilder` or :obj:`nn.Module`): Any number of child
            segment layers.  The layer names will be ``segment_0``, ``segment_1``,
            etc.
        side_inputs_transform (:obj:`.LayerBuilder`, optional): An optional layer
            for transforming keyword arguments to ``forward()``.
    """

    def __init__(
        self,
        *segments: _ModuleOrBuilder,
        side_inputs_transform: _OptionalModuleOrBuilder = None,
    ):
        named_layers = {f"segment_{i}": segment for i, segment in enumerate(segments)}
        side_input_keys = {
            name: ["**side_inputs"] for name in named_layers
        }  # forward all kwargs to each segment
        super().__init__(
            named_layers,
            side_input_keys=side_input_keys,
            side_inputs_transform=side_inputs_transform,
        )

    @property
    def num_transformer_layers(self) -> int:
        return sum(layer.num_transformer_layers for layer in self)

    def iter_transformer_layers(self) -> _Iterator[_torch.nn.Module]:
        iters = (layer.iter_transformer_layers() for layer in self)
        return _itertools.chain(*iters)
