"""
transformer.token_type_encoding
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This module implements token type encoding layers for :class:`.TransformerStack`.
These layers encode token types into embeddings and attention masks prior to the
sequence of transformer layers.

.. autoclass:: tamm.layers.TransformerTokenTypeEncoding
    :show-inheritance:
    :members: forward

.. autoclass:: TransformerTokenTypeEncodingOutput

.. autoclass:: tamm.layers.TransformerTokenTypeEmbedding
    :show-inheritance:
    :members: create_builder
"""


import abc as _abc
import collections as _collections
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional

import torch as _torch
import torch.nn as _nn

from tamm import _helpers
from tamm.layers import embedding as _embedding
from tamm.layers.common import ConfigurableLayerMixin as _ConfigurableLayerMixin
from tamm.layers.transformer import token_metadata as _token_metadata
from tamm.typing import ModuleBuilder as _ModuleBuilder

TransformerTokenTypeEncodingOutput = _collections.namedtuple(
    "TransformerTokenTypeEncodingOutput", ["embeddings", "attention_side_inputs"]
)
"""
A :class:`namedtuple` for holding outputs from a :class:`TransformerTokenTypeEncoding`.

.. py:attribute:: embeddings

    Embedding inputs to the first layer of a transformer.

.. py:attribute:: attention_side_inputs

    Side inputs to self attention layers of a transformer.
"""


class TransformerTokenTypeEncoding(_nn.Module, _abc.ABC):
    """
    A base class for layers that encode token types into the inputs of
    a transformer layer sequence.
    """

    def __init__(self):
        super().__init__()

    @_abc.abstractmethod
    def forward(
        self,
        *,
        token_metadata: _token_metadata.TokenMetadata,
        embeddings: _torch.Tensor,
        attention_side_inputs: _Dict[_Any, _Any],
    ) -> TransformerTokenTypeEncodingOutput:
        """
        Args:
            token_metadata (:obj:`TokenMetaData`): A :obj:`TokenMetaData`
                object, which includes a ``q_token_types`` tensor with shape
                ``(batch_size, seq_len)``.
            embeddings (:obj:`torch.Tensor`): The input embeddings to a transformer
                model with shape ``(batch_size, seq_len, hidden_dim)``.  The dtype
                should match the computation dtype for attention layers.
            attention_side_inputs (:obj:`dict`): A dictionary of side inputs to
                attention layers.  This should contain ``"attention_mask"`` and
                ``"flash_attention_options"`` keys.

        Returns:
            A :obj:`TransformerTokenTypeEncodingOutput`, which contains new
            ``embeddings`` and ``attention_side_inputs`` objects with
            token types encoded.
        """


class TransformerTokenTypeEmbedding(
    TransformerTokenTypeEncoding, _ConfigurableLayerMixin
):
    """
    This layer maps token types to trainable embedding tensors and then adds these
    embeddings to the token embeddings.

    Args:
        embedding: An embedding layer (or builder) that maps token types to embeddings.
        sequence_start (:obj:`int`, optional): An option that controls which tokens
            receive token type embeddings.  If ``sequence_start > 0``, then the first
            ``sequence_start`` tokens do not receive them.
    """

    # pylint: disable=duplicate-code

    def __init__(
        self,
        embedding: _ModuleBuilder,
        sequence_start: _Optional[int] = None,
    ):
        super().__init__()
        self.embedding = _helpers.maybe_build_module(embedding)
        self.sequence_start = sequence_start

    @classmethod
    def create_basic_builder(  # pylint: disable=arguments-differ
        cls,
        num_embeddings: int,
        embedding_dim: int,
        *,
        sequence_start: _Optional[int] = None,
    ) -> _ModuleBuilder:
        """
        Creates and returns a builder for :class:`TransformerTokenTypeEmbedding` layers.

        Args:
            num_embeddings (:obj:`int`): The number of embeddings in the token type
                embedding table.
            embedding_dim (:obj:`int`): The dimension of the embeddings.
            sequence_start (:obj:`int`, optional): The ``sequence_start`` option for the
                layer.

        Returns:
            The configured :obj:`LayerBuilder`.
        """
        embedding = _embedding.Embedding.Builder(
            num_embeddings=num_embeddings,
            embedding_dim=embedding_dim,
        )
        return cls.Builder(
            embedding=embedding,
            sequence_start=sequence_start,
        )

    def forward(  # pylint: disable=arguments-differ
        self,
        *,
        token_metadata: _token_metadata.TokenMetadata,
        embeddings: _torch.Tensor,
        attention_side_inputs: _Dict[_Any, _Any],
    ) -> TransformerTokenTypeEncodingOutput:
        token_types = token_metadata.q_token_types

        if self.sequence_start in (None, 0):
            start_embeddings = None
        else:
            start_embeddings = embeddings[:, : self.sequence_start]
            embeddings = embeddings[:, self.sequence_start :]
            token_types = token_types[:, self.sequence_start :]

        type_embeddings = self.embedding(token_types)
        type_embeddings = type_embeddings.type_as(embeddings)
        outputs = embeddings + type_embeddings

        if start_embeddings is not None:
            outputs = _torch.cat([start_embeddings, outputs], dim=1)

        return TransformerTokenTypeEncodingOutput(
            embeddings=outputs, attention_side_inputs=attention_side_inputs
        )

    def extra_repr(self) -> str:
        if self.sequence_start in (None, 0):
            return ""
        return f"sequence_start={self.sequence_start}"
