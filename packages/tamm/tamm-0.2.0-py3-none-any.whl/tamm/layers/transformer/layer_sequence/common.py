import abc as _abc
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Iterator as _Iterator
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch

from tamm.layers import side_outputs as _side_outputs
from tamm.layers.transformer import kv_cache as _kv_cache
from tamm.layers.transformer import token_metadata as _token_metadata


class BaseTransformerLayerSequence(_torch.nn.Module, _abc.ABC):
    """
    A base class that defines the interface for transformer layer sequences.
    """

    def __init__(self):
        super().__init__()

    @property
    def num_transformer_layers(self):
        """The number of transformer layers within the layer sequence."""
        return len(self.transformer_layers)

    @property
    def num_layers(self):
        """Deprecated alias of :attr:`.num_transformer_layers`."""
        return self.num_transformer_layers

    @_abc.abstractmethod
    def iter_transformer_layers(self) -> _Iterator[_torch.nn.Module]:
        """Returns an iterator over all transformer layers in the sequence."""

    @_abc.abstractmethod
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
        """
        Args:
            hidden_states (:obj:`torch.Tensor`): Input hidden states to the transformer
                layers.
            attention_side_inputs (:obj:`dict`): Keyword arguments to self-attention
                layers within the layer sequence, excluding KV cache values.
            kv_cache (:obj:`.BaseKVCacheView`, optional): Optional cached keys
                and values for self-attention layers.
            secondary_attention_side_inputs (:obj:`dict`, optional): The output of a
                :class:`.SecondaryPositionalEncodings` layer, which contains
                additional attention side inputs for different types of positional
                encodings.
            cross_attention_side_inputs (:obj:`dict`): Keyword arguments to
                cross-attention layers within the sequence.
            token_metadata (:obj:`TokenMetadata`): The :obj:`TokenMetadata` from
                the :class:`TransformerStack`.
        """
