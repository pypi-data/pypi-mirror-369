import itertools as _itertools
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Iterator as _Iterator
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch

from tamm import _helpers
from tamm.layers import side_outputs as _side_outputs
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.transformer import kv_cache as _kv_cache
from tamm.layers.transformer import token_metadata as _token_metadata
from tamm.layers.transformer.layer_sequence import common as _common
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder


class KVReuseTransformerLayerSequence(
    _common.BaseTransformerLayerSequence, _LayerMixin
):
    """
    A sequence consisting of two :class:`.BaseTransformerLayerSequence` segments.
    Rather than computing its own keys and values for self-attention, the second
    segment reuses keys and values returned from the first segment.

    The first segment must return ``keys`` and ``values`` hidden states as
    side outputs.  The second segment receives ``keys`` and ``values``
    as inputs in the ``attention_side_inputs`` argument.  The second segment
    also does not receive a ``kv_cache`` argument.

    Args:
        segment_0: A builder for the first segment.
        segment_1: A builder for the second segment.
    """

    def __init__(self, segment_0: _ModuleOrBuilder, segment_1: _ModuleOrBuilder):
        super().__init__()
        _helpers.append_children(self, segment_0=segment_0, segment_1=segment_1)

    @property
    def num_transformer_layers(self) -> int:
        return (
            self.segment_0.num_transformer_layers
            + self.segment_1.num_transformer_layers
        )

    def iter_transformer_layers(self) -> _Iterator[_torch.nn.Module]:
        return _itertools.chain(
            self.segment_0.iter_transformer_layers(),
            self.segment_1.iter_transformer_layers(),
        )

    def forward(
        self,
        hidden_states: _torch.Tensor,
        *,
        attention_side_inputs: _Dict[str, _Any],
        kv_cache: _Optional[_kv_cache.BaseKVCacheView] = None,
        secondary_attention_side_inputs: _Optional[_Dict[str, _Dict[str, _Any]]] = None,
        cross_attention_side_inputs: _Dict[str, _Any],
        token_metadata: _token_metadata.TokenMetadata,
    ) -> _Union[_torch.Tensor, _side_outputs.OutputWithSideOutputs]:
        # pylint: disable=unused-argument

        outputs_0 = self.segment_0(
            hidden_states=hidden_states,
            attention_side_inputs=attention_side_inputs,
            kv_cache=kv_cache,
            secondary_attention_side_inputs=secondary_attention_side_inputs,
            cross_attention_side_inputs=cross_attention_side_inputs,
            token_metadata=token_metadata,
        )

        side_outputs_0 = outputs_0.side_outputs

        keys, values = side_outputs_0.pop("key"), side_outputs_0.pop("value")
        if isinstance(keys, list):
            keys = keys[-1]
        if isinstance(values, list):
            values = values[-1]
        attention_side_inputs["key"] = keys
        attention_side_inputs["value"] = values

        outputs_1 = self.segment_1(
            hidden_states=outputs_0.output,
            attention_side_inputs=attention_side_inputs,
            secondary_attention_side_inputs=secondary_attention_side_inputs,
            cross_attention_side_inputs=cross_attention_side_inputs,
            token_metadata=token_metadata,
        )

        if isinstance(outputs_1, _side_outputs.OutputWithSideOutputs):
            outputs_1.side_outputs.pop("key", None)
            outputs_1.side_outputs.pop("value", None)
            outputs_1.side_outputs = _side_outputs.merge_side_outputs(
                side_outputs_0, outputs_1.side_outputs
            )
        elif len(side_outputs_0) > 0:
            outputs_1.side_outputs = _side_outputs.OutputWithSideOutputs(
                outputs_1, side_outputs=side_outputs_0
            )

        return outputs_1
