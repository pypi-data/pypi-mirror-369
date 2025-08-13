"""
transformer.stack
=================

.. autoclass:: tamm.layers.TransformerStack
    :show-inheritance:
    :members:

.. autoclass:: tamm.layers.transformer.stack.TransformerStackOutput
    :members:

.. autoclass:: tamm.layers.ExtendedTransformerStack
    :show-inheritance:
    :members:

.. autoclass:: tamm.layers.transformer.stack.ExtendedTransformerStackOutput
    :members:
    :inherited-members:

.. autoclass:: tamm.layers.transformer.stack.ExtendedTransformerStackMode
    :members:

.. autoclass:: tamm.layers.transformer.stack.ExtendedTransformerStackEmbeddingSignature
    :members:

.. autoclass:: tamm.layers.transformer.stack.ExtendedTransformerStackOutputTransformBuildMode
    :members:
"""

import enum as _enum
from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

from tamm import _helpers
from tamm._helpers import case_insensitive_lookup
from tamm.layers import functional as _tamm_F
from tamm.layers import side_outputs as _side_outputs
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.transformer import attention_mask as _attention_mask
from tamm.layers.transformer import kv_cache as _kv_cache
from tamm.layers.transformer import token_metadata as _token_metadata
from tamm.typing import ModuleBuilder as _ModuleBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder
from tamm.typing import OptionalTensor as _OptionalTensor
from tamm.utils import torch_utils as _torch_utils


@_torch_utils.torch_exportable_dataclass
class TransformerStackOutput:
    """A dataclass for holding outputs from a :class:`TransformerStack`."""

    last_hidden_state: _OptionalTensor = None
    """The (possibly normalized) output of the transformer stack."""

    hidden_states: _Optional[_List[_torch.Tensor]] = None
    """
    An optional list of ``n + 1`` hidden states, where ``n`` is the number of
    transformer layers.  This includes the (possibly normalized) input embeddings and
    the output from each layer.  This is ``None`` unless the layer stack produces side
    outputs with ``hidden_states``.
    """

    attentions: _Optional[_List[_torch.Tensor]] = None
    """
    An optional list of attention probabilities, one from each attention layer in the
    stack.  This is ``None`` unless the layer stack produces side outputs with
    ``attentions``.
    """

    expert_assignments: _Optional[_List[_torch.Tensor]] = None
    """
    An optional list of expert assignments, one from each Mixture of Expert layer in the
    stack.  This is ``None`` unless the layer stack produces side outputs with
    ``expert_assignments``.
    """

    token_metadata: _Optional[_token_metadata.TokenMetadata] = None
    """
    The :obj:`.TokenMetadata` used within the transformer stack, which includes
    segment IDs, positions, and more.
    """


class TransformerStack(_nn.Module, _LayerMixin):
    """
    A generic transformer stack for encoders and decoders.  The output is the result of
    the following layer sequence:

    * An optional token type encoding
    * An optional positional encoding
    * An optional input transform
    * An optional input norm
    * A sequence of transformer layers
    * An optional output norm

    In addition, this layer uses attention mask and positional encoding layers to control
    the behavior of attention.

    This layer also has a :obj:`token_metadata_logic` child layer, which controls the
    value of token positions and segment ids.  Users can implement custom behavior by
    subclassing :class:`tamm.layers.transformer.token_metadata.TokenMetadataLogic`.

    Args:
        token_metadata_logic: An optional builder for a :class:`.TokenMetadataLogic`
            layer.  If ``None``, this defaults to :class:`.VanillaTokenMetadataLogic`.
        token_type_encoding:  An optional layer that transforms input embeddings as a
            function of the ``token_types`` passed to :meth:`.forward`.
        attention_mask: An optional attention mask builder for controlling which tokens
            attend to one another.
        positional_encoding: An optional position encoder builder for incorporating
            positions into the attention computation.
        secondary_positional_encodings: An optional
            :class:`.SecondaryPositionalEncodings` layer for passing additional
            positional encoding outputs to ``layers``.  This is useful for models that
            mix positional encoding types (such as local and global attention).
        input_transform: An optional builder for mapping target embeddings into
            different dimensions.
        input_norm: An optional norm builder for normalizing target embeddings.
        layers: A builder for the sequence of transformer layers.
        output_norm: An optional norm builder for normalizing outputs.
        embeddings_cast_dtype (:obj:`torch.dtype` or ``str``, optional): A target dtype
            for casting input embeddings, which should match the dtype for computation.
            If ``"auto"``, the layer attempts to infer the correct dtype.  If ``None``,
            the layer performs no cast.
    """

    def __init__(
        self,
        *,
        token_metadata_logic: _OptionalModuleOrBuilder = None,
        token_type_encoding: _OptionalModuleOrBuilder = None,
        attention_mask: _OptionalModuleOrBuilder = None,
        positional_encoding: _OptionalModuleOrBuilder = None,
        secondary_positional_encodings: _OptionalModuleOrBuilder = None,
        input_transform: _OptionalModuleOrBuilder = None,
        input_norm: _OptionalModuleOrBuilder = None,
        layers: _ModuleBuilder,
        output_norm: _OptionalModuleOrBuilder = None,
        embeddings_cast_dtype: _Optional[_Union[str, _torch.dtype]] = "auto",
    ):
        super().__init__()

        if token_metadata_logic is None:
            token_metadata_logic = _token_metadata.VanillaTokenMetadataLogic.Builder()
        if attention_mask is None:
            attention_mask = _attention_mask.AttentionMask.Builder()

        _helpers.append_children(
            # pylint: disable=duplicate-code
            self,
            token_metadata_logic=token_metadata_logic,
            token_type_encoding=token_type_encoding,
            attention_mask=attention_mask,
            positional_encoding=positional_encoding,
            secondary_positional_encodings=secondary_positional_encodings,
            input_transform=input_transform,
            input_norm=input_norm,
            layers=layers,
            output_norm=output_norm,
        )
        self.embeddings_cast_dtype = embeddings_cast_dtype

    @property
    def num_layers(self) -> int:
        """The number of transformer layers in the stack."""
        return self.layers.num_layers

    def forward(
        self,
        inputs: _torch.Tensor,
        *,
        segment_ids: _OptionalTensor = None,
        positions: _OptionalTensor = None,
        token_types: _OptionalTensor = None,
        kv_cache: _Optional[_kv_cache.BaseKVCacheView] = None,
        attention_mask: _OptionalTensor = None,
        cross_attention_source: _OptionalTensor = None,
        cross_attention_mask: _OptionalTensor = None,
        aux_token_metadata: _Optional[_Dict[str, _Any]] = None,
    ) -> TransformerStackOutput:
        """
        Args:
            inputs (:obj:`torch.Tensor` or :obj:`dict`): Input target embeddings,
                typically with shape ``(batch_size, seq_len, hidden_dim)``.  The inputs
                can also have multiple sequence dimensions, in which case the layer
                flattens the input sequence and unflattens the output sequence.  The
                inputs can even be a :obj:`dict` the maps strings to embeddings, in
                which case the layer concatenates the inputs and splits the outputs.
            segment_ids (:obj:`torch.Tensor`, optional): An integer tensor with shape
                ``(batch_size, seq_len)`` that controls the attention mask for
                self attention layers.  For sequence ``i``, if
                ``segment_ids[i, j] != segment_ids[i, k]``, then tokens ``j`` and
                ``k`` do not attend to each other.  If unspecified, ``segment_ids``
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
                ``kv_cache``, in which case it is the cache length.
            cross_attention_source (:obj:`torch.Tensor`, optional): Input source
                embeddings for cross attention layers with shape
                ``(batch_size, source_seq_len, hidden_dim)``.
            cross_attention_mask (:obj:`torch.Tensor`, optional): An attention mask for
                cross attention with shape ``(batch_size, seq_len, source_seq_len)``.
            aux_token_metadata (:obj:`dict`): A dictionary of optional auxiliary inputs for
                extending model behavior.  This gets attached to the ``token_metadata``
                input of several child layers, including the attention mask, layer
                sequence, and positional encoding layers.
        """

        # pylint: disable=too-many-locals

        x = _tamm_F.maybe_flatten_embeddings(inputs)
        segment_ids = _tamm_F.maybe_flatten_sequence(segment_ids)
        positions = _tamm_F.maybe_flatten_sequence(positions)
        token_types = _tamm_F.maybe_flatten_sequence(token_types)
        cross_attention_source = _tamm_F.maybe_flatten_embeddings(
            cross_attention_source
        )

        x = self._maybe_cast_inputs(x, kv_cache=kv_cache)
        cross_attention_source = self._maybe_cast_inputs(
            cross_attention_source, kv_cache=kv_cache
        )

        token_metadata = self.token_metadata_logic(
            embeddings=x,
            segment_ids=segment_ids,
            positions=positions,
            token_types=token_types,
            kv_cache=kv_cache,
            aux_metadata=aux_token_metadata,
        )

        if attention_mask is None:
            attention_side_inputs = self.attention_mask(
                token_metadata, compute_dtype=x.dtype
            )
        else:
            attention_side_inputs = {
                "attention_mask": attention_mask,
                "flash_attention_options": None,  # Flash does not support custom masks
            }

        if self.token_type_encoding is not None:
            x, attention_side_inputs = self.token_type_encoding(
                token_metadata=token_metadata,
                embeddings=x,
                attention_side_inputs=attention_side_inputs,
            )

        if self.secondary_positional_encodings is not None:
            secondary_attention_side_inputs = self.secondary_positional_encodings(
                token_metadata=token_metadata,
                embeddings=x,
                attention_side_inputs=attention_side_inputs,
            )
        else:
            secondary_attention_side_inputs = None

        if self.positional_encoding is not None:
            x, attention_side_inputs = self.positional_encoding(
                token_metadata=token_metadata,
                embeddings=x,
                attention_side_inputs=attention_side_inputs,
            )

        if self.input_transform is not None:
            x = self.input_transform(x)

        if self.input_norm is not None:
            x = self.input_norm(x)

        cross_attention_side_inputs = {
            "source": cross_attention_source,
            "attention_mask": cross_attention_mask,
        }

        x = self.layers(
            x,
            attention_side_inputs=attention_side_inputs,
            kv_cache=kv_cache,
            secondary_attention_side_inputs=secondary_attention_side_inputs,
            cross_attention_side_inputs=cross_attention_side_inputs,
            token_metadata=token_metadata,
        )

        if isinstance(x, _side_outputs.OutputWithSideOutputs):
            outputs = x.side_outputs
            x = x.output
        else:
            outputs = {}

        if self.output_norm is not None:
            x = self.output_norm(x)

        x = _tamm_F.maybe_unflatten_embeddings(x, original=inputs)

        outputs["token_metadata"] = token_metadata
        outputs["last_hidden_state"] = x
        return TransformerStackOutput(**outputs)

    def _maybe_cast_inputs(
        self,
        tensor: _Union[_torch.Tensor, None],
        *,
        kv_cache: _Optional[_kv_cache.BaseKVCacheView] = None,
    ) -> _Union[_torch.Tensor, None]:
        if tensor is None:
            return None
        if self.embeddings_cast_dtype is None:
            return tensor
        if self.embeddings_cast_dtype != "auto":
            return tensor.type(self.embeddings_cast_dtype)
        if kv_cache is not None and kv_cache.dtype is not None:
            dtype = kv_cache.dtype
        else:
            dtype = _helpers.get_dtype_after_autocast(tensor.dtype, tensor.device)
        if dtype is None:
            return tensor
        return tensor.type(dtype)


@_torch_utils.torch_exportable_dataclass
class ExtendedTransformerStackOutput(TransformerStackOutput):
    """A dataclass for holding outputs from an :class:`ExtendedTransformerStack`."""

    embeddings: _OptionalTensor = None
    """The output of the embedding layer."""

    predictions: _OptionalTensor = None
    """The output of the output transform layer."""

    loss: _OptionalTensor = None
    """The output of the loss layer."""


class ExtendedTransformerStackMode(str, _enum.Enum):
    """
    An :obj:`Enum` for controlling the behavior of
    :meth:`ExtendedTransformerStack.forward`.
    """

    #: Perform the full forward pass using all available layers.
    FULL = "FULL"

    #: Skip the embedding layer (user passes input embeddings).
    SKIP_EMBEDDING_LAYER = "SKIP_EMBEDDING_LAYER"

    #: Return the output of the embedding layer only.
    ONLY_EMBEDDING_LAYER = "ONLY_EMBEDDING_LAYER"

    #: Return the output of the transformer layers but skip the head layer.
    SKIP_OUTPUT_LAYER = "SKIP_OUTPUT_LAYER"

    #: Skip both the embedding and head layers.
    SKIP_EMBEDDING_AND_OUTPUT_LAYERS = "SKIP_EMBEDDING_AND_OUTPUT_LAYERS"

    @classmethod
    def _missing_(cls, value):
        return case_insensitive_lookup(cls, value)


class ExtendedTransformerStackEmbeddingSignature(str, _enum.Enum):
    """
    An :obj:`Enum` for controlling the arguments passed to the embedding layer
    during  :meth:`ExtendedTransformerStack.forward`.
    """

    #: Pass only the transformer's ``inputs`` to the embedding layer.
    ONLY_INPUTS = "ONLY_INPUTS"

    #: Pass ``inputs, cache=cache, segment_ids=segment_ids`` to the embedding
    # layer.
    WITH_CACHE_AND_SEGMENT_IDS = "WITH_CACHE_AND_SEGMENT_IDS"


class ExtendedTransformerStackOutputTransformBuildMode(str, _enum.Enum):
    """
    An :class:`Enum` for modifying the building of ``output_transform`` layers
    during :class:`ExtendedTransformerStack` initialization.  The main purpose is to
    support tying ``embedding`` and ``output_transform`` weights.
    """

    #: Pass no arguments to :meth:`builder.build` when building the output transform
    #: layer.
    BASIC = "BASIC"

    #: Pass the embedding layer as the only argument when building the layer.
    PASS_EMBEDDING = "PASS_EMBEDDING"

    @classmethod
    def _missing_(cls, value):
        return case_insensitive_lookup(cls, value)


class ExtendedTransformerStack(TransformerStack, _LayerMixin):
    """
    This layer extends :class:`.TransformerStack` by adding optional embedding, output
    transform, and loss layers.

    Args:
        embedding: An optional builder for a layer that transforms inputs into token
            embeddings.
        embedding_signature (:obj:`str`, optional): An optional member of
            :class:`.ExtendedTransformerStackEmbeddingSignature` to control the
            arguments passed to the embedding layer during :meth:`.forward`.
            Defaults to ``"only_inputs"``.
        token_metadata_logic: An optional builder for a :class:`.TokenMetadataLogic` layer.
        token_type_encoding: An optional builder for a layer that encodes token types.
        attention_mask: An optional attention mask builder for controlling which tokens
            attend to one another.
        positional_encoding: An optional position encoder builder for incorporating
            positions into the attention computation.
        secondary_positional_encodings: An optional
            :class:`.SecondaryPositionalEncodings` layer for passing additional
            positional encoding outputs to ``layers``.
        input_transform: An optional builder for mapping target embeddings into
            different dimensions.
        input_norm: An optional norm builder for normalizing target embeddings.
        layers: A builder for the sequence of transformer layers.
        output_norm: An optional norm builder for normalizing outputs.
        output_transform: An optional builder for mapping (possibly normalized) outputs
            of the transformer layers into predictions.
        output_transform_build_mode (:obj:`str`, optional): An optional member of
            :class:`.ExtendedTransformerStackOutputTransformBuildMode` to modify the
            building of ``output_transform``.
        loss: An optional builder for computing a loss value from the predictions and
            labels.
        embeddings_cast_dtype (:obj:`torch.dtype` or ``str``, optional): A target dtype
            for casting input embeddings, which should match the dtype for computation.
            If ``"auto"``, the layer attempts to infer the correct dtype.  If ``None``,
            the layer performs no cast.
    """

    def __init__(
        self,
        *,
        embedding: _OptionalModuleOrBuilder = None,
        embedding_signature: _Optional[str] = "only_inputs",
        token_metadata_logic: _OptionalModuleOrBuilder = None,
        token_type_encoding: _OptionalModuleOrBuilder = None,
        attention_mask: _OptionalModuleOrBuilder = None,
        positional_encoding: _OptionalModuleOrBuilder = None,
        secondary_positional_encodings: _OptionalModuleOrBuilder = None,
        input_transform: _OptionalModuleOrBuilder = None,
        input_norm: _OptionalModuleOrBuilder = None,
        layers: _ModuleBuilder,
        output_norm: _OptionalModuleOrBuilder = None,
        output_transform: _OptionalModuleOrBuilder = None,
        output_transform_build_mode: _Optional[str] = "basic",
        loss: _OptionalModuleOrBuilder = None,
        embeddings_cast_dtype: _Optional[_Union[str, _torch.dtype]] = "auto",
    ):
        # pylint: disable=too-many-locals
        super().__init__(
            layers=layers,
            token_metadata_logic=token_metadata_logic,
            token_type_encoding=token_type_encoding,
            attention_mask=attention_mask,
            positional_encoding=positional_encoding,
            secondary_positional_encodings=secondary_positional_encodings,
            input_transform=input_transform,
            input_norm=input_norm,
            output_norm=output_norm,
            embeddings_cast_dtype=embeddings_cast_dtype,
        )
        _helpers.prepend_children(self, embedding=embedding)
        self._init_output_transform(output_transform, mode=output_transform_build_mode)
        _helpers.append_children(self, loss=loss)

        self.embedding_signature = _helpers.get_enum_member_from_name(
            ExtendedTransformerStackEmbeddingSignature, embedding_signature
        )

    def _init_output_transform(self, output_transform, *, mode):
        mode = _helpers.get_enum_member_from_name(
            ExtendedTransformerStackOutputTransformBuildMode, mode
        )
        if mode is ExtendedTransformerStackOutputTransformBuildMode.PASS_EMBEDDING:
            args = (self.embedding,)
        else:
            args = ()
        self.output_transform = _helpers.maybe_build_module(output_transform, *args)

    @property
    def head_layer(self) -> _Union[_nn.Module, None]:
        """
        Returns the head layer of the model.  In this case, it's the same as
        ``output_transform``.
        """
        return self.output_transform

    def forward(
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
        mode: _Union[ExtendedTransformerStackMode, str] = "full",
    ) -> ExtendedTransformerStackOutput:
        """
        Args:
            inputs (:obj:`torch.Tensor`): Inputs to the ``embedding`` layer.  For some
                values of ``mode``, this should instead be input embeddings.
            labels: Optional labels for the ``loss`` layer.  The loss layer should
                accept two positional arguments: (1) the output of ``output_transform``
                and (2) ``labels``.
            segment_ids (:obj:`torch.Tensor`, optional): An integer tensor with shape
                ``(batch_size, seq_len)`` that controls the attention mask for
                self attention layers.  For sequence ``i``, if
                ``segment_ids[i, j] != segment_ids[i, k]``, then tokens ``j`` and
                ``k`` do not attend to each other.  If unspecified, ``segment_ids``
                defaults to all ones.
            positions (:obj:`torch.Tensor`, optional): Integer tensor with shape
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
                ``kv_cache``, in which case it is the cache length.
            cross_attention_source (:obj:`torch.Tensor`, optional): Input source
                embeddings for cross attention layers with shape
                ``(batch_size, source_seq_len, hidden_dim)``.
            cross_attention_mask (:obj:`torch.Tensor`, optional): An attention mask for
                cross attention with shape ``(batch_size, seq_len, source_seq_len)``.
            aux_token_metadata (:obj:`dict`): A dictionary of optional auxiliary inputs for
                extending model behavior.  This gets attached to the ``token_metadata``
                input of several child layers, including the attention mask, layer
                sequence, and positional encoding layers.
            mode (:obj:`str` or :obj:`.ExtendedTransformerStackMode`, optional): A
                mode for controlling the forward behavior.  Defaults to ``FULL``.
        """

        mode = _helpers.get_enum_member_from_name(ExtendedTransformerStackMode, mode)

        if self._should_skip_embedding_layer(mode):
            x = inputs
        else:
            x = self._call_embedding(inputs, cache=kv_cache, segment_ids=segment_ids)
        x, outputs = self._maybe_merge_side_outputs(x, {})
        outputs["embeddings"] = x

        if mode is ExtendedTransformerStackMode.ONLY_EMBEDDING_LAYER:
            return ExtendedTransformerStackOutput(**outputs)

        x = super().forward(
            inputs=x,
            segment_ids=segment_ids,
            positions=positions,
            token_types=token_types,
            kv_cache=kv_cache,
            attention_mask=attention_mask,
            cross_attention_source=cross_attention_source,
            cross_attention_mask=cross_attention_mask,
            aux_token_metadata=aux_token_metadata,
        )
        x, outputs = self._merge_transformer_stack_outputs(x, outputs)

        if self._should_skip_output_transform(mode):
            return ExtendedTransformerStackOutput(**outputs)

        x = self.output_transform(x)
        x, outputs = self._maybe_merge_side_outputs(x, outputs)
        outputs["predictions"] = x

        if self.loss is not None and labels is not None:
            outputs["loss"] = self.loss(x, labels)

        return ExtendedTransformerStackOutput(**outputs)

    def _call_embedding(self, inputs, *, cache, segment_ids):
        should_pass_kwargs = (
            self.embedding_signature
            is ExtendedTransformerStackEmbeddingSignature.WITH_CACHE_AND_SEGMENT_IDS
        )
        kwargs = (
            {"cache": cache, "segment_ids": segment_ids} if should_pass_kwargs else {}
        )
        return self.embedding(inputs, **kwargs)

    @staticmethod
    def _maybe_merge_side_outputs(
        new_outputs: _Any, old_side_outputs: _Dict[str, _Any]
    ) -> _Tuple[_Any, _Dict[str, _Any]]:
        if isinstance(new_outputs, _side_outputs.OutputWithSideOutputs):
            new_side_outputs = _side_outputs.merge_side_outputs(
                old_side_outputs, new_outputs.side_outputs
            )
            new_outputs = new_outputs.output
        else:
            new_side_outputs = old_side_outputs

        return new_outputs, new_side_outputs

    @staticmethod
    def _merge_transformer_stack_outputs(
        new_outputs: TransformerStackOutput, old_side_outputs: _Dict[str, _Any]
    ) -> _Tuple[_Any, _Dict[str, _Any]]:
        new_side_outputs = dict(
            old_side_outputs.items()
            # this is a torch.compile-friendly shallow copy of the dict, since
            # torch.compile graph-breaks on old_side_outputs.copy()
        )
        new_side_outputs["last_hidden_state"] = new_outputs.last_hidden_state
        new_side_outputs["hidden_states"] = new_outputs.hidden_states
        new_side_outputs["attentions"] = new_outputs.attentions
        new_side_outputs["expert_assignments"] = new_outputs.expert_assignments
        new_side_outputs["token_metadata"] = new_outputs.token_metadata
        return new_outputs.last_hidden_state, new_side_outputs

    def _should_skip_embedding_layer(self, mode: ExtendedTransformerStackMode) -> bool:
        if self.embedding is None:
            return True
        return mode in (
            ExtendedTransformerStackMode.SKIP_EMBEDDING_LAYER,
            ExtendedTransformerStackMode.SKIP_EMBEDDING_AND_OUTPUT_LAYERS,
        )

    def _should_skip_output_transform(self, mode: ExtendedTransformerStackMode) -> bool:
        if self.output_transform is None:
            return True
        return mode in (
            ExtendedTransformerStackMode.SKIP_OUTPUT_LAYER,
            ExtendedTransformerStackMode.SKIP_EMBEDDING_AND_OUTPUT_LAYERS,
        )
