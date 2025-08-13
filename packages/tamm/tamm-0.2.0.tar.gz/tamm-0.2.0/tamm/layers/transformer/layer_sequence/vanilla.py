from typing import Any as _Any
from typing import Dict as _Dict
from typing import Iterator as _Iterator
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch

from tamm.layers import sequential as _sequential
from tamm.layers import side_outputs as _side_outputs
from tamm.layers.transformer import kv_cache as _kv_cache
from tamm.layers.transformer import token_metadata as _token_metadata
from tamm.layers.transformer.layer_sequence import common as _common
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class TransformerLayerSequence(
    _sequential.Sequential, _common.BaseTransformerLayerSequence
):
    """
    A generic sequence of transformer layers.  Each layer may be configured
    independently, and the architecture can vary between layers.  For example, layers
    0 and 1 could have different numbers of attention heads.

    Args:
        sequence: One or more transformer layers (or builders).
        input_transform (:obj:`.LayerBuilder`, optional): An optional auxiliary
            layer for the start of the sequence.  Defaults to ``None``.
        output_transform (:obj:`.LayerBuilder`, optional): An optional auxiliary
            layer for the end of the sequence.  Defaults to ``None``.
        output_hidden_states (:obj:`bool`): A flag for including outputs from each
            layer in the sequence output.  Defaults to ``False``.
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
        output_hidden_states: bool = False,
        attention_types: _Optional[_Dict[int, str]] = None,
    ):
        named_layers = {"input_transform": input_transform}
        side_input_keys = {}
        side_output_keys = {}

        for layer_idx, layer in enumerate(sequence):
            layer_name = f"layer_{layer_idx}"
            named_layers[layer_name] = layer
            side_input_keys[layer_name] = [
                "attention_side_inputs",
                (f"attention_side_inputs_{layer_idx}", "attention_side_inputs"),
                "cross_attention_side_inputs",
            ]
            if output_hidden_states:
                side_output_keys[layer_name] = "hidden_states"

        named_layers["output_transform"] = output_transform

        if attention_types is None:
            attention_types = {}
        self.attention_types = attention_types

        super().__init__(
            named_layers,
            side_input_keys=side_input_keys,
            side_output_keys=side_output_keys,
        )

    @property
    def num_transformer_layers(self) -> int:
        result = len(self)
        if self.input_transform is not None:
            result -= 1
        if self.output_transform is not None:
            result -= 1
        return result

    def iter_transformer_layers(self) -> _Iterator[_torch.nn.Module]:
        for name, layer in self.named_layers:
            if name not in ("input_transform", "output_transform"):
                yield layer

    def extra_repr(self):
        if self.attention_types:
            return f"attention_types={self.attention_types}"
        return ""

    # pylint: disable-next=arguments-differ,arguments-renamed
    def forward(
        self,
        hidden_states: _torch.Tensor,
        *,
        attention_side_inputs: _Dict[str, _Any],
        kv_cache: _Optional[_kv_cache.BaseKVCacheView] = None,
        secondary_attention_side_inputs: _Optional[_Dict[str, _Dict[str, _Any]]] = None,
        cross_attention_side_inputs: _Optional[_Dict[str, _Any]] = None,
        token_metadata: _token_metadata.TokenMetadata,
    ) -> _Union[_torch.Tensor, _side_outputs.OutputWithSideOutputs]:
        # pylint: disable=unused-argument
        attention_kwargs = self._get_attention_kwargs(
            attention_side_inputs=attention_side_inputs,
            secondary_attention_side_inputs=secondary_attention_side_inputs,
            kv_cache=kv_cache,
        )
        return super().forward(
            hidden_states,
            **attention_kwargs,
            cross_attention_side_inputs=cross_attention_side_inputs,
            token_metadata=token_metadata,
        )

    def _get_attention_kwargs(
        self, *, attention_side_inputs, secondary_attention_side_inputs, kv_cache
    ):
        if kv_cache is None and not self.attention_types:
            return {"attention_side_inputs": attention_side_inputs}

        prefix = "attention_side_inputs_"
        keys = [
            next(key for key, _ in side_input_keys_i if key.startswith(prefix))
            for side_input_keys_i in self.side_input_keys.values()
        ]

        result = {}
        for layer_idx, key in enumerate(keys):
            attention_type = self.attention_types.get(layer_idx, None)
            if attention_type is None:
                side_inputs_for_layer = attention_side_inputs
            else:
                side_inputs_for_layer = secondary_attention_side_inputs[attention_type]

            result[key] = dict(
                side_inputs_for_layer.items()
            )  # torch.compile friendly copy

            if kv_cache is not None:
                result[key]["kv_cache"] = self._get_cache_arg_for_layer(
                    kv_cache=kv_cache, layer_idx=layer_idx
                )

        return result

    def _get_cache_arg_for_layer(self, *, kv_cache, layer_idx):
        return kv_cache.at_layer(layer_idx)
