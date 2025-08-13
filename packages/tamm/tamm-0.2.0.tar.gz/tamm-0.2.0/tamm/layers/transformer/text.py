"""
transformer.text
^^^^^^^^^^^^^^^^

This submodule implements transformer-specific components for language modeling.

.. autoclass:: tamm.layers.CausalLMTransformer
    :show-inheritance:
    :members: forward

.. autoclass:: tamm.layers.transformer.CausalLMTransformerOutput
    :members:
    :inherited-members:

.. autoclass:: tamm.layers.transformer.TextTransformerEncoder
"""

import collections as _collections
from contextlib import contextmanager as _contextmanager
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch

from tamm import _helpers
from tamm.layers import linear as _linear
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.transformer import kv_cache as _kv_cache
from tamm.layers.transformer import stack as _transformer_stack
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder
from tamm.typing import OptionalTensor as _OptionalTensor
from tamm.utils import torch_utils as _torch_utils


class CausalLMTransformer(_transformer_stack.ExtendedTransformerStack, _LayerMixin):
    """
    A general layer for decoder-only causal language models.  This layer is the same as
    :class:`.ExtendedTransformerStack` except for a few changes:

    * The layer has an optional ``segmentation`` layer, which computes default
      ``segment_ids`` when the user passes token ids but no segment IDs.
    * The :meth:`forward` method does not take arguments for cross attention.

    Args:
        segmentation: A layer for converting input token IDs to segment IDs.  Often this
            is a padding mask that returns ``0`` for padding tokens and ``1``
            for non-padding.

    Please see :class:`.ExtendedTransformerStack` for a description of the remaining
    parameters.
    """

    def __init__(
        self,
        *,
        segmentation: _OptionalModuleOrBuilder = None,
        embedding: _OptionalModuleOrBuilder = None,
        embedding_signature: _Optional[str] = "only_inputs",
        token_metadata_logic: _OptionalModuleOrBuilder = None,
        token_type_encoding: _OptionalModuleOrBuilder = None,
        attention_mask: _OptionalModuleOrBuilder = None,
        positional_encoding: _OptionalModuleOrBuilder = None,
        secondary_positional_encodings: _OptionalModuleOrBuilder = None,
        input_transform: _OptionalModuleOrBuilder = None,
        input_norm: _OptionalModuleOrBuilder = None,
        layers: _ModuleOrBuilder,
        output_norm: _OptionalModuleOrBuilder = None,
        output_transform: _OptionalModuleOrBuilder = None,
        output_transform_build_mode: _Optional[str] = "basic",
        loss: _OptionalModuleOrBuilder = None,
        embeddings_cast_dtype: _Optional[_Union[str, _torch.dtype]] = "auto",
    ):
        # pylint: disable=too-many-locals
        super().__init__(
            embedding=embedding,
            embedding_signature=embedding_signature,
            token_metadata_logic=token_metadata_logic,
            token_type_encoding=token_type_encoding,
            attention_mask=attention_mask,
            positional_encoding=positional_encoding,
            secondary_positional_encodings=secondary_positional_encodings,
            input_transform=input_transform,
            input_norm=input_norm,
            layers=layers,
            output_norm=output_norm,
            output_transform=output_transform,
            output_transform_build_mode=output_transform_build_mode,
            loss=loss,
            embeddings_cast_dtype=embeddings_cast_dtype,
        )
        _helpers.prepend_children(self, segmentation=segmentation)
        # Flag to enable tracing behavior, when set to `True`, returns dict instead of dataclass.
        self._return_tuple_output = False

    def forward(  # pylint: disable=arguments-differ
        self,
        inputs: _Any,
        *,
        labels: _Any = None,
        segment_ids: _OptionalTensor = None,
        positions: _OptionalTensor = None,
        token_types: _OptionalTensor = None,
        kv_cache: _Optional[_kv_cache.BaseKVCacheView] = None,
        attention_mask: _OptionalTensor = None,
        cross_attention_source: _OptionalTensor = None,
        cross_attention_mask: _OptionalTensor = None,
        aux_token_metadata: _Optional[_Dict[str, _Any]] = None,
        mode: _Union[_transformer_stack.ExtendedTransformerStackMode, str] = "full",
    ):
        """
        Args:
            inputs (:obj:`torch.Tensor`): Inputs to the ``embedding`` layer, which
                typically are input token IDs with shape ``(batch_size, seq_len)``.  For
                some values of ``mode``, this should instead be input embeddings with
                shape ``(batch_size, seq_len, hidden_dim)``.
            labels: Optional labels for the ``loss`` layer.  If provided, the loss layer
                should accept two positional arguments; the first is the output of
                ``output_transform``, and the second is ``labels``.
            segment_ids (:obj:`torch.Tensor`, optional): An integer tensor with shape
                ``(batch_size, seq_len)`` that controls the attention mask for
                self attention layers.  For sequence ``i``, if
                ``segment_ids[i, j] != segment_ids[i, k]``, then tokens ``j`` and
                ``k`` do not attend to each other.  If unspecified, the ``kv_cache``
                argument (if provided) or ``segmentation`` layer (otherwise) determines
                the ``segment_ids``.  If neither of these are provided, ``segment_ids``
                defaults to all ones.
            positions (:obj:`torch.Tensor`, optional): An integer tensor with shape
                ``(batch_size, seq_len)`` that specifies the position of each
                token.  If unspecified, ``positions`` defaults to
                ``0, 1, 2, ...`` for each segment of each sequence.
            token_types (:obj:`torch.Tensor`, optional): An integer tensor with shape
                ``(batch_size, seq_len)`` that specifies a "type" for each token.
                The ``token_type_encoding`` and ``attention_mask`` child layers may use
                this type information in different ways, depending on the model.
            kv_cache (:obj:`BaseKVCacheView`, optional): A KV cache view with cached
                keys and values for self-attention layers.
            attention_mask (:obj:`torch.Tensor`, optional): A boolean tensor with shape
                ``(batch_size, seq_len, kv_seq_len)``.  A ``True`` value indicates that
                the corresponding pair of tokens should take part in attention.  The
                ``kv_seq_len`` should be the same as ``seq_len`` unless using a
                ``kv_cache``, in which case ``kv_seq_len`` is the cache length.
            cross_attention_source (:obj:`torch.Tensor`, optional): Input source
                embeddings for possible cross attention layers with shape
                ``(batch_size, source_seq_len, hidden_dim)``. Note: causal LMs typically
                do not have cross attention layers, but this is sometimes useful for
                extending the model (for example to handle long contexts).
            cross_attention_mask (:obj:`torch.Tensor`, optional): An attention mask for
                cross attention with shape ``(batch_size, seq_len, source_seq_len)``.
            aux_token_metadata (:obj:`dict`): A dictionary of optional auxiliary inputs for
                extending model behavior.  This gets attached to the ``token_metadata``
                input of several child layers, including the attention mask, layer
                sequence, and positional encoding layers.
            mode (:obj:`str` or :obj:`.ExtendedTransformerStackMode`, optional): A
                mode for controlling the forward behavior.  Defaults to ``FULL``.
        """

        mode = _helpers.get_enum_member_from_name(
            _transformer_stack.ExtendedTransformerStackMode, mode
        )
        segment_ids = self._maybe_update_segment_ids(
            segment_ids, inputs=inputs, mode=mode, kv_cache=kv_cache
        )
        # pylint: disable=duplicate-code
        output = super().forward(
            inputs=inputs,
            labels=labels,
            segment_ids=segment_ids,
            positions=positions,
            token_types=token_types,
            kv_cache=kv_cache,
            attention_mask=attention_mask,
            cross_attention_source=cross_attention_source,
            cross_attention_mask=cross_attention_mask,
            aux_token_metadata=aux_token_metadata,
            mode=mode,
        )
        output_dict = _helpers.dataclass_to_dict(output)

        if self._return_tuple_output:
            return self._create_output_tuple(output_dict)

        return CausalLMTransformerOutput(**output_dict)

    @staticmethod
    def _create_output_tuple(output_dict):
        """Creates a named tuple from the output dictionary, filtering None values."""

        output_dict.pop(
            "token_metadata",
            None,
            # drop this because this method is only used for torch.jit tracing
            # and jit trace doesn't like the fact that token_metadata is a dataclass.
            # jit tracing has been replaced by torch.export for export, so it is not
            # important to support token metadata here
        )
        output_dict_without_none = {
            k: v for k, v in output_dict.items() if v is not None
        }
        output_type = _collections.namedtuple(
            "CausalLMDynamicOutput", list(output_dict_without_none.keys())
        )
        return output_type(**output_dict_without_none)

    def _maybe_update_segment_ids(self, segment_ids, *, inputs, mode, kv_cache):
        if segment_ids is not None:
            return segment_ids
        if self._should_skip_embedding_layer(mode):
            return None
        if self.segmentation is None:
            return None
        if kv_cache is not None:
            return None
        return self.segmentation(inputs)

    @property
    def is_embedding_tied_to_output_transform(self):
        if not isinstance(self.output_transform, _linear.TiedWeightLinear):
            return False
        try:
            return self.embedding.weight is self.output_transform.weight
        except AttributeError:
            return False

    @_contextmanager
    def jit_traceable_context(self):
        """
        Context manager to enable torch.jit.trace by returning tuple outputs
        instead of dataclass during tracing.
        """
        original_output = self._return_tuple_output
        self._return_tuple_output = True

        try:
            yield
        finally:
            self._return_tuple_output = original_output


@_torch_utils.torch_exportable_dataclass
class CausalLMTransformerOutput(_transformer_stack.ExtendedTransformerStackOutput):
    """A dataclass for holding outputs from a :class:`CausalLMTransformer`."""

    @property
    def logits(self):
        """An alias of :attr:`predictions`."""
        return self.predictions


class TextTransformerEncoder(_transformer_stack.ExtendedTransformerStack, _LayerMixin):
    """
    A general layer for text encoder language models.  This layer is the same as
    :class:`.ExtendedTransformerStack` except for a few changes:

    * The layer has an optional ``segmentation`` layer, which computes default
      ``segment_ids`` when the user passes token ids but no segment IDs.
    * The :meth:`forward` method does not take arguments for cross attention.

    Args:
        segmentation: A layer for converting input token IDs to segment IDs.  Often this
            is a padding mask that returns ``0`` for padding tokens and ``1``
            for non-padding.

    Please see :class:`.ExtendedTransformerStack` for a description of the remaining
    parameters.
    """

    def __init__(
        self,
        *,
        segmentation: _OptionalModuleOrBuilder = None,
        embedding: _OptionalModuleOrBuilder = None,
        embedding_signature: _Optional[str] = "only_inputs",
        token_metadata_logic: _OptionalModuleOrBuilder = None,
        token_type_encoding: _OptionalModuleOrBuilder = None,
        attention_mask: _OptionalModuleOrBuilder = None,
        positional_encoding: _OptionalModuleOrBuilder = None,
        secondary_positional_encodings: _OptionalModuleOrBuilder = None,
        input_transform: _OptionalModuleOrBuilder = None,
        input_norm: _OptionalModuleOrBuilder = None,
        layers: _ModuleOrBuilder,
        output_norm: _OptionalModuleOrBuilder = None,
        output_transform: _OptionalModuleOrBuilder = None,
        output_transform_build_mode: _Optional[str] = "basic",
        loss: _OptionalModuleOrBuilder = None,
        embeddings_cast_dtype: _Optional[_Union[str, _torch.dtype]] = "auto",
    ):
        # pylint: disable=too-many-locals
        super().__init__(
            embedding=embedding,
            embedding_signature=embedding_signature,
            token_metadata_logic=token_metadata_logic,
            token_type_encoding=token_type_encoding,
            attention_mask=attention_mask,
            positional_encoding=positional_encoding,
            secondary_positional_encodings=secondary_positional_encodings,
            input_transform=input_transform,
            input_norm=input_norm,
            layers=layers,
            output_norm=output_norm,
            output_transform=output_transform,
            output_transform_build_mode=output_transform_build_mode,
            loss=loss,
            embeddings_cast_dtype=embeddings_cast_dtype,
        )
        _helpers.prepend_children(self, segmentation=segmentation)

    def forward(  # pylint: disable=arguments-differ
        self,
        inputs: _Any,
        *,
        labels: _Any = None,
        segment_ids: _OptionalTensor = None,
        positions: _OptionalTensor = None,
        token_types: _OptionalTensor = None,
        kv_cache: _Optional[_kv_cache.BaseKVCacheView] = None,
        attention_mask: _OptionalTensor = None,
        aux_token_metadata: _Optional[_Dict[str, _Any]] = None,
        mode: _Union[_transformer_stack.ExtendedTransformerStackMode, str] = "full",
    ) -> "_transformer_stack.ExtendedTransformerStackOutput":
        """
        Args:
            inputs (:obj:`torch.Tensor`): Inputs to the ``embedding`` layer, which
                typically are input token IDs with shape ``(batch_size, seq_len)``.  For
                some values of ``mode``, this should instead be input embeddings with
                shape ``(batch_size, seq_len, hidden_dim)``.
            labels: Optional labels for the ``loss`` layer.  If provided, the loss layer
                should accept two positional arguments; the first is the output of
                ``output_transform``, and the second is ``labels``.
            segment_ids (:obj:`torch.Tensor`, optional): An integer tensor with shape
                ``(batch_size, seq_len)`` that controls the attention mask for
                self attention layers.  For sequence ``i``, if
                ``segment_ids[i, j] != segment_ids[i, k]``, then tokens ``j`` and
                ``k`` do not attend to each other.  If unspecified, the ``kv_cache``
                argument (if provided) or ``segmentation`` layer (otherwise) determines
                the ``segment_ids``.  If neither of these are provided, ``segment_ids``
                defaults to all ones.
            positions (:obj:`torch.Tensor`, optional): An integer tensor with shape
                ``(batch_size, seq_len)`` that specifies the position of each
                token.  If unspecified, ``positions`` defaults to
                ``0, 1, 2, ...`` for each segment of each sequence.
            token_types (:obj:`torch.Tensor`, optional): An integer tensor with shape
                ``(batch_size, seq_len)`` that specifies a "type" for each token.
                The ``token_type_encoding`` and ``attention_mask`` child layers may use
                this type information in different ways, depending on the model.
            kv_cache (:obj:`BaseKVCacheView`, optional): A KV cache view with cached
                keys and values for self-attention layers.
            attention_mask (:obj:`torch.Tensor`, optional): A boolean tensor with shape
                ``(batch_size, seq_len, kv_seq_len)``.  A ``True`` value indicates that
                the corresponding pair of tokens should take part in attention.  The
                ``kv_seq_len`` should be the same as ``seq_len`` unless using a
                ``kv_cache``, in which case ``kv_seq_len`` is the cache length.
            aux_token_metadata (:obj:`dict`): A dictionary of optional auxiliary inputs for
                extending model behavior.  This gets attached to the ``token_metadata``
                input of several child layers, including the attention mask, layer
                sequence, and positional encoding layers.
            mode (:obj:`str` or :obj:`.ExtendedTransformerStackMode`, optional): A
                mode for controlling the forward behavior.  Defaults to ``FULL``.
        """

        mode = _helpers.get_enum_member_from_name(
            _transformer_stack.ExtendedTransformerStackMode, mode
        )
        segment_ids = self._maybe_update_segment_ids(
            segment_ids, inputs=inputs, mode=mode, kv_cache=kv_cache
        )
        output = super().forward(
            inputs=inputs,
            labels=labels,
            segment_ids=segment_ids,
            positions=positions,
            token_types=token_types,
            kv_cache=kv_cache,
            attention_mask=attention_mask,
            aux_token_metadata=aux_token_metadata,
            mode=mode,
        )
        return _transformer_stack.ExtendedTransformerStackOutput(
            **_helpers.dataclass_to_dict(output)
        )

    def _maybe_update_segment_ids(self, segment_ids, *, inputs, mode, kv_cache):
        if segment_ids is not None:
            return segment_ids
        if self._should_skip_embedding_layer(mode):
            return None
        if self.segmentation is None:
            return None
        if kv_cache is not None:
            return None
        return self.segmentation(inputs)
