"""
transformer.vision
^^^^^^^^^^^^^^^^^^

This submodule implements transformer-specific components for vision models.

.. autoclass:: tamm.layers.VisionTransformerEncoder
    :show-inheritance:
    :members: forward
"""

# pylint: disable=duplicate-code

from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch

from tamm import _helpers
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.transformer import stack as _transformer_stack
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder
from tamm.typing import OptionalTensor as _OptionalTensor


class VisionTransformerEncoder(
    _transformer_stack.ExtendedTransformerStack, _LayerMixin
):
    """
    A general layer for vision encoders.  This layer is the same as
    :class:`.ExtendedTransformerStack` except for a few changes:

    * The layer has an optional ``segmentation`` layer, and the :meth:`forward` method
      accepts an optional ``padding_mask`` argument.  The segmentation layer computes
      default ``segment_ids`` from the ``padding_mask``.
    * The :meth:`forward` method does not take arguments for KV caching or cross
      attention.

    Args:
        segmentation: A layer for converting per-pixel ``padding_mask`` inputs to
            per-token segment IDs with shape ``(batch_size, *seq_shape)``.  Typically
            the segment IDs also form a padding mask with ``0`` for padding values and
            ``1`` for non-padding.

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
        padding_mask: _Any = None,
        segment_ids: _OptionalTensor = None,
        positions: _OptionalTensor = None,
        token_types: _OptionalTensor = None,
        attention_mask: _OptionalTensor = None,
        aux_token_metadata: _Optional[_Dict[str, _Any]] = None,
        mode: _Union[_transformer_stack.ExtendedTransformerStackMode, str] = "full",
    ) -> _transformer_stack.ExtendedTransformerStackOutput:
        """
        Args:

            inputs (:obj:`torch.Tensor`): Inputs to the ``embedding`` layer, which
                typically are images in NCHW format.  For some values of ``mode``, this
                should instead be input embeddings.
            labels: Optional labels for the ``loss`` layer.  If provided, the loss layer
                should accept two positional arguments; the first is the output of
                ``output_transform``, and the second is ``labels``.
            padding_mask (:obj:`torch.Tensor`, optional): An optional padding mask to
                pass to the ``segmentation`` layer.  Typically this is a pixel-level
                mask.  Defaults to ``None``.
            segment_ids (:obj:`torch.Tensor`, optional): An integer tensor with shape
                ``(batch_size, seq_len)`` that controls the attention mask for
                self attention layers.  For sequence ``i``, if
                ``segment_ids[i, j] != segment_ids[i, k]``, then tokens ``j`` and
                ``k`` do not attend to each other.  If unspecified, the ``segmentation``
                layer computes ``segment_ids`` from the ``padding_mask``.  If the
                ``segmentation`` layer or ``padding_mask`` is not provided, then
                ``segment_ids`` defaults to all ones.
            positions (:obj:`torch.Tensor`, optional): An integer tensor with shape
                ``(batch_size, seq_len)`` that specifies the position of each
                token.  If unspecified, ``positions`` defaults to
                ``0, 1, 2, ...`` for each segment of each sequence.
            token_types (:obj:`torch.Tensor`, optional): An integer tensor with shape
                ``(batch_size, seq_len)`` that specifies a "type" for each token.
                The ``token_type_encoding`` and ``attention_mask`` child layers may use
                this type information in different ways, depending on the model.
            attention_mask (:obj:`torch.Tensor`, optional): A boolean tensor with shape
                ``(batch_size, seq_len, seq_len)``.  A ``True`` value indicates that
                the corresponding pair of tokens should take part in attention.
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
            segment_ids, padding_mask=padding_mask
        )
        return super().forward(
            inputs=inputs,
            labels=labels,
            segment_ids=segment_ids,
            positions=positions,
            token_types=token_types,
            attention_mask=attention_mask,
            aux_token_metadata=aux_token_metadata,
            mode=mode,
        )

    def _maybe_update_segment_ids(self, segment_ids, *, padding_mask):
        if segment_ids is not None:
            return segment_ids
        if self.segmentation is not None and padding_mask is not None:
            return self.segmentation(padding_mask)
        return None
