"""
layers.attention
^^^^^^^^^^^^^^^^

This module implements attention layers for transformer models.

.. autoclass:: tamm.layers.attention.SDPAImplementationChoice
    :members:
"""

# pylint: disable=too-many-lines

import enum as _enum
import logging as _logging
import math as _math
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
from torch import _dynamo
from torch import nn as _nn

from tamm import _adapters_v1, _helpers
from tamm._helpers import case_insensitive_lookup
from tamm._helpers import (
    is_torch_base_version_less_than as _is_torch_base_version_less_than,
)
from tamm.layers import decoding as _decoding
from tamm.layers import dropout as _dropout
from tamm.layers import functional as _tamm_F
from tamm.layers import linear as _linear
from tamm.layers import norm as _norm
from tamm.layers import residual as _residual
from tamm.layers import rope as _rope
from tamm.layers import sequential as _sequential
from tamm.layers import side_outputs as _side_outputs
from tamm.layers.common import ConfigurableLayerMixin as _ConfigurableLayerMixin
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.flash_attention import _qkv_flash_attention_compatible
from tamm.layers.flash_attention import (
    flash_attn_func_with_low_rank_mask as _flash_attn_func_with_low_rank_mask,
)
from tamm.layers.flash_attention import (
    is_flash_attention_available as _is_flash_attn_available,
)
from tamm.typing import ModuleBuilder as _ModuleBuilder
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder

try:
    # pylint: disable-next=ungrouped-imports
    from torch.nn.attention import flex_attention as _flex_attention  # noqa

    _IS_FLEX_ATTENTION_AVAILABLE = True
except ImportError:
    _IS_FLEX_ATTENTION_AVAILABLE = False


_logger = _logging.getLogger(__name__)


class TransformerAttention(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    Attention layer with configurable normalization and residual connection.  Takes inputs of shape
    ``(batch_size, sequence_length, target_dim)`` and optional source inputs of shape
    ``(batch_size, sequence_length, source_dim)``.  The output is the result of the
    following layer sequence:

    * Norm
    * Query/key/value transform
    * QKV scale
    * RoPE transform
    * QK norm
    * KV cacher
    * Scaled dot product attention
    * Output transform
    * Dropout
    * Norm
    * Residual add
    * Norm

    The QKV transform layer should take an optional ``source`` argument, and the KV
    cacher should accept an optional ``kv_cache`` argument.  Also, the SDPA layer should
    take an optional ``attention_mask`` argument and an
    optional ``flash_attention_options`` argument.

    Args:
        norm: The norm layer (:obj:`nn.Module`) or builder (callable that returns the
            :obj:`nn.Module` when called without args).
        qkv_transform: The QKV transform layer or builder.
        qkv_scale: The QKV scale layer or builder.
        rope_transform: The RoPE transform layer or builder.
        qk_norm: Layer for applying scaling on key and query vectors.
            It is optional and defined if QK normalization is applied.
        kv_cacher: The KV cacher layer or builder.
        scaled_dot_product_attention: The SDPA layer or builder.
        output_transform: The output transform layer or builder.
        dropout: The dropout layer or builder.
        residual_connection: The residual connection layer or builder.
        kv_dim: The dimension of the key and value tensors.
        attention_layer_type: The type of attention layer to use.

    Users can also create this layer using its :meth:`create` method, which has
    simpler args.  Alternatively, use :meth:`create_builder` to create the layer via
    a configurable builder.
    """

    def __init__(
        self,
        *,
        norm: _OptionalModuleOrBuilder,
        qkv_transform: _ModuleOrBuilder,
        qkv_scale: _ModuleOrBuilder,
        rope_transform: _OptionalModuleOrBuilder,
        qk_norm: _OptionalModuleOrBuilder,
        kv_cacher: _ModuleOrBuilder,
        scaled_dot_product_attention: _ModuleOrBuilder,
        output_transform: _ModuleOrBuilder,
        dropout: _ModuleOrBuilder,
        residual_connection: _ModuleOrBuilder,
        kv_dim: float,
        attention_layer_type: _Optional[str] = None,
    ):
        # pylint: disable=too-many-locals
        self.kv_dim = kv_dim

        # We do the following since converters have difficulty
        # distinguishing between layers which have positional encoding
        # which leads to differences in the state dict.
        qkv_transform_key = "qkv_transform"
        if attention_layer_type == "global_nope":
            qkv_transform_key = "qkv_transform_global_nope"

        named_layers = {
            "norm": norm,
            qkv_transform_key: qkv_transform,
            "qkv_scale": qkv_scale,
            "rope_transform": rope_transform,
            "qk_norm": qk_norm,
            "kv_cacher": kv_cacher,
            "scaled_dot_product_attention": scaled_dot_product_attention,
            "output_transform": output_transform,
            "dropout": dropout,
        }
        side_input_keys = {
            qkv_transform_key: [("source", "key"), ("source", "value")],
            "rope_transform": ["query_rope_coefficients", "key_rope_coefficients"],
            "kv_cacher": ["kv_cache"],
            "scaled_dot_product_attention": [
                "attention_mask",
                "flash_attention_options",
            ],
        }

        if rope_transform is None:
            named_layers.pop("rope_transform")
            side_input_keys.pop("rope_transform")
        if qk_norm is None:
            named_layers.pop("qk_norm")

        super().__init__(
            named_layers,
            side_input_keys=side_input_keys,
            unpack_tuple_inputs=True,
            residual_connection=residual_connection,
        )
        self.qkv_transform_key = qkv_transform_key
        self._mark_adaptable_layers()

    @classmethod
    def create_basic_builder(
        cls,
        *,
        target_dim: int,
        source_dim: _Optional[int] = None,
        num_heads: int = 1,
        num_kv_heads: _Optional[int] = None,
        norm: _Union[str, _OptionalModuleOrBuilder] = "layer_norm",
        apply_rope: bool = False,
        apply_qk_norm: bool = False,
        attention_dropout_p: float = 0.0,
        hidden_dropout_p: float = 0.0,
        qkv_transform_bias: bool = False,
        output_transform_bias: bool = False,
        apply_residual_add: bool = True,
        output_attentions: bool = False,
        output_kv_state: bool = False,
        sdpa_implementation: _Union["SDPAImplementationChoice", str] = "auto",
        vec_dim: _Optional[_List[int]] = None,
        atten_hidden_dim: _Optional[int] = None,
        attention_layer_type: _Optional[str] = None,
        sliding_window_size: _Optional[int] = None,
        apply_pre_norm: bool = True,
        apply_pre_residual_norm: bool = False,
        apply_post_norm: bool = False,
    ):  # pylint: disable=arguments-differ
        """
        Creates and returns a default builder for creating :obj:`TransformerAttention`
        objects.  The builder uses :class:`LayerNorm` for the norm layer and
        :class:`Linear` for the output transform.  For the QKV transform, the layer uses
        :class:`FusedMultiOutputLinear` if ``source_dim`` is ``None`` and
        :class:`QKVLinear` otherwise.

        Use :meth:`create` to directly create an attention layer.

        Args:
            target_dim (:obj:`int`): The hidden dimension of the target input.  This
                tensor should have shape ``(batch_size, sequence_length, source_dim)``.
            source_dim (:obj:`int`, optional): The hidden dimension of the optional
                source input.
            num_heads (:obj:`int`): The number of attention heads.
            num_kv_heads (:obj:`int`, optional): The number of key-value heads for
                grouped query attention (GQA: https://arxiv.org/pdf/2305.13245.pdf).
                The default value is ``num_heads``, which results in vanilla
                multi-head attention.
            norm: The norm layer (:obj:`nn.Module`) or builder (a callable that returns
                the norm layer when called without args).  If ``None``, this defaults to
                :class:`LayerNorm`.
            apply_rope (:obj:`bool`, optional): Flag for including a RoPE transform
                layer to rotate query and key tensors.  Defaults to ``False``.  If
                ``True``, the attention layer expects ``query_rope_coefficients``
                and ``key_rope_coefficients`` keyword arguments during
                :meth:`.forward`.
            apply_qk_norm (:obj:`bool`, optional): Flag for applying normalization on
                key and query vectors.  Defaults to ``False``.
            attention_dropout_p (:obj:`float`): The dropout probability for attention
                probabilities.
            hidden_dropout_p (:obj:`float`): The dropout probability for the dropout
                layer prior to the residual add.
            qkv_transform_bias (:obj:`bool`): Should the QKV Projection Layer
                use a bias term.
            output_transform_bias (:obj:`bool`): Should the output transform
                linear layer use a bias term.
            apply_residual_add (:obj:`bool`): Should apply a residual add layer.
            output_attentions (:obj:`bool`): Flag that when ``True`` results in the
                inclusion of attentions weights in ScaledDotProductAttention.
            output_kv_state (:obj:`bool`): Flag that when ``True`` results in the
                inclusion of kv_state of current layer as side outputs. Defaults to ``False``.
            apply_pre_norm (:obj:`bool`): Whether to apply normalization before the
                attention computation. Defaults to ``True``.
            apply_pre_residual_norm (:obj:`bool`): Whether to apply normalization after the
                attention computation but before the residual connection. Defaults to ``False``.
                If ``True``, ``apply_residual_add`` must also be ``True``.
            apply_post_norm (:obj:`bool`): Whether to apply normalization after the
                residual connection using :class:`NormalizedResidualConnection`. When ``True``,
                requires ``apply_residual_add`` to also be ``True``. Defaults to ``False``.

        Returns:
            A :obj:`TransformerAttentionLayer.Builder` for creating layers.
        """

        # pylint: disable=too-many-locals, duplicate-code

        # Don't apply rope if global_nope (nope = no positional encoding)
        if attention_layer_type == "global_nope":
            apply_rope = False

        norm = _norm.create_norm_builder((target_dim,), spec=norm)

        num_kv_heads = num_kv_heads if num_kv_heads is not None else num_heads
        if num_heads % num_kv_heads != 0:
            raise ValueError(
                "num_heads must be a multiple of num_kv_heads"
                f"(received num_heads={num_heads} and num_kv_heads={num_kv_heads})"
            )

        atten_hidden_dim = (
            atten_hidden_dim if atten_hidden_dim is not None else target_dim
        )
        if atten_hidden_dim % num_heads != 0:
            raise ValueError(
                "atten_hidden_dim must be a multiple of num_heads "
                f"(received atten_hidden_dim={atten_hidden_dim} and "
                f"num_heads={num_heads})"
            )

        kv_output_dim = (atten_hidden_dim * num_kv_heads) // num_heads

        qkvlinear_kwargs = {}
        multioutputlinear_kwargs = {}
        linear_kwargs = {}
        linear_cls = _linear.Linear
        if vec_dim is not None:
            qkvlinear_kwargs = {"vec_dim": vec_dim}
            multioutputlinear_kwargs = {"vec_dim": vec_dim}
            linear_kwargs = {"vec_dim": vec_dim}
            linear_cls = _linear.VectorizedLinear

        if source_dim is not None:
            qkv_transform = QKVLinear.Builder(
                query_dim=target_dim,
                key_dim=source_dim,
                value_dim=source_dim,
                key_output_dim=kv_output_dim,
                value_output_dim=kv_output_dim,
                bias=qkv_transform_bias,
                **qkvlinear_kwargs,
            )
        else:
            qkv_transform = _linear.FusedMultiOutputLinear.Builder(
                target_dim,
                [atten_hidden_dim, kv_output_dim, kv_output_dim],
                bias=qkv_transform_bias,
                **multioutputlinear_kwargs,
            )

        rope_transform = RoPETransform.Builder() if apply_rope else None

        qk_norm = None
        if apply_qk_norm:
            dim_per_head = atten_hidden_dim // num_heads
            qk_norm = QKNorm.Builder(
                dim_per_head=dim_per_head,
                query_norm=_norm.LayerNorm.Builder([dim_per_head]),
                key_norm=_norm.LayerNorm.Builder([dim_per_head]),
            )

        scaled_dot_product_attention = ScaledDotProductAttention.Builder(
            num_heads,
            num_kv_heads=num_kv_heads,
            dropout_p=attention_dropout_p,
            output_attentions=output_attentions,
            implementation=sdpa_implementation,
            sliding_window_size=(
                sliding_window_size if attention_layer_type == "local" else None
            ),
            output_kv_state=output_kv_state,
        )

        output_transform = linear_cls.Builder(
            atten_hidden_dim, target_dim, bias=output_transform_bias, **linear_kwargs
        )

        dropout = _dropout.Dropout.Builder(p=hidden_dropout_p)

        residual_connection = _residual._maybe_create_residual_add_builder(
            apply_residual_add=apply_residual_add,
            apply_pre_residual_norm=apply_pre_residual_norm,
            apply_post_norm=apply_post_norm,
            norm=norm,
        )

        return cls.Builder(
            norm=norm if apply_pre_norm else None,
            qkv_transform=qkv_transform,
            rope_transform=rope_transform,
            qk_norm=qk_norm,
            kv_cacher=_decoding.KVCacher.Builder(),
            scaled_dot_product_attention=scaled_dot_product_attention,
            output_transform=output_transform,
            dropout=dropout,
            residual_connection=residual_connection,
            kv_dim=kv_output_dim,
            attention_layer_type=attention_layer_type,
        )

    def _mark_adaptable_layers(self):
        qkv_transform = getattr(self, self.qkv_transform_key)

        output_transform_layer_type = (
            "BatchedAttentionOutputTransform"
            if isinstance(self.output_transform, _linear.VectorizedLinear)
            else "AttentionOutputTransform"
        )
        _adapters_v1.annotate_layer(
            self.output_transform,
            [(output_transform_layer_type,)],
        )
        if isinstance(qkv_transform, _linear.FusedMultiOutputLinear):
            qkv_transform_layer_type = "AttentionInputTransformFused"
            fused_linear_layer_fields = {
                "input_dim_field": "input_dim",
                "output_dims_field": "output_dims",
                "weight_param_name": "fused_linear.weight",
            }
            if isinstance(qkv_transform.fused_linear, _linear.VectorizedLinear):
                qkv_transform_layer_type = "BatchedAttentionInputTransformFused"
                fused_linear_layer_fields["vec_dim_field"] = "vec_dim"
            _adapters_v1.annotate_layer(
                qkv_transform,
                [(qkv_transform_layer_type, fused_linear_layer_fields)],
            )
        elif isinstance(qkv_transform, QKVLinear):
            layer_type = (
                "BatchedAttentionInputTransformQuery"
                if isinstance(qkv_transform.query_linear, _linear.VectorizedLinear)
                else "AttentionInputTransformQuery"
            )
            _adapters_v1.annotate_layer(
                qkv_transform.query_linear,
                [(layer_type,)],
            )
            layer_type = (
                "BatchedAttentionInputTransformKey"
                if isinstance(qkv_transform.key_linear, _linear.VectorizedLinear)
                else "AttentionInputTransformKey"
            )
            _adapters_v1.annotate_layer(
                qkv_transform.key_linear,
                [(layer_type,)],
            )
            layer_type = (
                "BatchedAttentionInputTransformValue"
                if isinstance(qkv_transform.value_linear, _linear.VectorizedLinear)
                else "AttentionInputTransformValue"
            )
            _adapters_v1.annotate_layer(
                qkv_transform.value_linear,
                [(layer_type,)],
            )


class KVReuseTransformerAttention(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    An attention layer that reuses keys and values from an earlier layer. Takes inputs
    of shape ``(batch_size, sequence_length, target_dim)``.  The output is the result
    of the following layer sequence:

    * Norm
    * Query transform
    * RoPE transform
    * Query norm
    * Scaled dot product attention
    * Output transform
    * Dropout
    * Norm
    * Residual add
    * Norm

    The SDPA layer should take in an external key and value, an optional ``attention_mask``
    argument, and an optional ``flash_attention_options`` argument.

    Args:
        norm: The norm layer (:obj:`nn.Module`) or builder (callable that returns the
            :obj:`nn.Module` when called without args).
        q_transform: The query transform layer or builder.
        rope_transform: The RoPE transform layer or builder.
        q_norm: Layer for applying scaling on key and query vectors.
            It is optional and defined if query normalization is applied.
        scaled_dot_product_attention: The SDPA layer or builder.
        output_transform: The output transform layer or builder.
        dropout: The dropout layer or builder.
        residual_connection: The residual connection layer or builder.
    """

    def __init__(
        self,
        *,
        norm: _OptionalModuleOrBuilder,
        q_transform: _ModuleOrBuilder,
        rope_transform: _OptionalModuleOrBuilder,
        q_norm: _OptionalModuleOrBuilder,
        scaled_dot_product_attention: _ModuleOrBuilder,
        output_transform: _ModuleOrBuilder,
        dropout: _ModuleOrBuilder,
        residual_connection: _ModuleOrBuilder,
    ):
        named_layers = {
            "norm": norm,
            "q_transform": q_transform,
            "rope_transform": rope_transform,
            "q_norm": q_norm,
            "scaled_dot_product_attention": scaled_dot_product_attention,
            "output_transform": output_transform,
            "dropout": dropout,
        }
        side_input_keys = {
            "rope_transform": ["query_rope_coefficients"],
            "scaled_dot_product_attention": [
                "key",
                "value",
                "attention_mask",
                "flash_attention_options",
            ],
        }
        if rope_transform is None:
            named_layers.pop("rope_transform")
            side_input_keys.pop("rope_transform")
        if q_norm is None:
            named_layers.pop("q_norm")
        super().__init__(
            named_layers,
            side_input_keys=side_input_keys,
            unpack_tuple_inputs=True,
            residual_connection=residual_connection,
        )
        self._mark_adaptable_layers()

    @classmethod
    def create_basic_builder(
        cls,
        *,
        target_dim: int,
        num_heads: int = 1,
        num_kv_heads: _Optional[int] = None,
        norm: _Union[str, _OptionalModuleOrBuilder] = "layer_norm",
        apply_rope: bool = False,
        apply_q_norm: bool = False,
        attention_dropout_p: float = 0.0,
        hidden_dropout_p: float = 0.0,
        q_transform_bias: bool = False,
        output_transform_bias: bool = False,
        apply_residual_add: bool = True,
        output_attentions: bool = False,
        output_kv_state: bool = False,
        sdpa_implementation: _Union["SDPAImplementationChoice", str] = "auto",
        apply_pre_norm: bool = True,
        apply_pre_residual_norm: bool = False,
        apply_post_norm: bool = False,
    ):  # pylint: disable=arguments-differ
        """
        Creates and returns a default builder for creating :obj:`KVReuseTransformerAttention`
        objects.  The builder uses :class:`LayerNorm` for the norm layer and
        :class:`Linear` for the output transform. The norm layer, q_transform layer,
        rope_transform layer, q_norm layer only applies to query tensors.

        Use :meth:`create` to directly create an attention layer.

        Args:
            target_dim (:obj:`int`): The hidden dimension of the target input.  This
                tensor should have shape ``(batch_size, sequence_length, source_dim)``.
            num_heads (:obj:`int`): The number of attention heads.
            num_kv_heads (:obj:`int`, optional): The number of key-value heads for
                grouped query attention (GQA: https://arxiv.org/pdf/2305.13245.pdf).
                The default value is ``num_heads``, which results in vanilla
                multi-head attention.
            norm: The norm layer (:obj:`nn.Module`) or builder (a callable that returns
                the norm layer when called without args).  If ``None``, this defaults to
                :class:`LayerNorm`.
            apply_rope (:obj:`bool`, optional): Flag for including a RoPE transform
                layer to rotate only query tensors.  Defaults to ``False``.  If
                ``True``, the attention layer expects ``query_rope_coefficients``
                keyword arguments during :meth:`.forward`.
            apply_q_norm (:obj:`bool`, optional): Flag for applying normalization on
                only query vectors.  Defaults to ``False``.
            attention_dropout_p (:obj:`float`): The dropout probability for attention
                probabilities.
            hidden_dropout_p (:obj:`float`): The dropout probability for the dropout
                layer prior to the residual add.
            q_transform_bias (:obj:`bool`): Should the Query Projection Layer
                use a bias term.
            output_transform_bias (:obj:`bool`): Should the output transform
                linear layer use a bias term.
            apply_residual_add (:obj:`bool`): Should apply a residual add layer.
            output_attentions (:obj:`bool`): Flag that when ``True`` results in the
                inclusion of attentions weights in ScaledDotProductAttention.
            output_kv_state (:obj:`bool`): Flag that when ``True`` results in the
                inclusion of kv_state of current layer as side outputs. Defaults to ``False``.
            apply_pre_norm (:obj:`bool`): Whether to apply normalization before the
                attention computation. Defaults to ``True``.
            apply_pre_residual_norm (:obj:`bool`): Whether to apply normalization after the
                attention computation but before the residual connection. Defaults to ``False``.
                If ``True``, ``apply_residual_add`` must also be ``True``.
            apply_post_norm (:obj:`bool`): Whether to apply normalization after the
                residual connection using PostNormResidualConnection. When ``True``,
                requires ``apply_residual_add`` to also be ``True``. Defaults to ``False``.

        Returns:
            A :obj:`KVReuseTransformerAttention.Builder` for creating layers.
        """

        # pylint: disable=too-many-locals, duplicate-code

        norm = _norm.create_norm_builder((target_dim,), spec=norm)

        if target_dim % num_heads != 0:
            raise ValueError(
                "target_dim must be a multiple of num_heads "
                f"(received target_dim={target_dim} and num_heads={num_heads})"
            )

        num_kv_heads = num_kv_heads if num_kv_heads is not None else num_heads
        if num_heads % num_kv_heads != 0:
            raise ValueError(
                "num_heads must be a multiple of num_kv_heads"
                f"(received num_heads={num_heads} and num_kv_heads={num_kv_heads})"
            )

        linear_kwargs = {}
        linear_cls = _linear.Linear

        q_transform = linear_cls.Builder(
            target_dim, target_dim, bias=q_transform_bias, **linear_kwargs
        )

        rope_transform = RoPETransform.Builder() if apply_rope else None

        q_norm = None
        if apply_q_norm:
            dim_per_head = target_dim // num_heads
            q_norm = QKNorm.Builder(
                dim_per_head=dim_per_head,
                query_norm=_norm.LayerNorm.Builder([dim_per_head]),
            )
        scaled_dot_product_attention = ScaledDotProductAttention.Builder(
            num_heads,
            num_kv_heads=num_kv_heads,
            dropout_p=attention_dropout_p,
            output_attentions=output_attentions,
            implementation=sdpa_implementation,
            output_kv_state=output_kv_state,
        )

        output_transform = linear_cls.Builder(
            target_dim, target_dim, bias=output_transform_bias, **linear_kwargs
        )

        dropout = _dropout.Dropout.Builder(p=hidden_dropout_p)

        norm = _norm.create_norm_builder((target_dim,), spec=norm)

        residual_connection = _residual._maybe_create_residual_add_builder(
            apply_residual_add=apply_residual_add,
            apply_pre_residual_norm=apply_pre_residual_norm,
            apply_post_norm=apply_post_norm,
            norm=norm,
        )

        return cls.Builder(
            norm=norm if apply_pre_norm else None,
            q_transform=q_transform,
            rope_transform=rope_transform,
            q_norm=q_norm,
            scaled_dot_product_attention=scaled_dot_product_attention,
            output_transform=output_transform,
            dropout=dropout,
            residual_connection=residual_connection,
        )

    def _mark_adaptable_layers(self):
        _adapters_v1.annotate_layer(
            self.q_transform,
            [("AttentionInputTransformQuery",)],
        )

        _adapters_v1.annotate_layer(
            self.output_transform,
            [("AttentionOutputTransform",)],
        )


def _split_batch_dimensions(output, original_value_shape):
    original_batch_shapes = original_value_shape[0:2]
    rest_shape = output.shape[1:]
    output = output.reshape(original_batch_shapes + rest_shape)

    return output


def _merge_batch_dimensions(query, key, value, bias):
    # Optimization for SDPA:
    #
    # We know that qkv has shape (N,...,L or S,E or Ev) (this may be transposed in non-torch format)
    #
    # In some cases (i.e: with 5d shape, for example, (batch, tracks, heads, seqlen, target_dim),
    # native torch does not use memory efficient attention. Additionally, Flash Attention assume 4d input.
    # So we merge dimensions in the front with batch so that
    # pytorch uses memory-efficient attention and flash attention can be used.
    #
    # Currently this only works with 5-D inputs (i.e: VectorizedParallelTrackTransformer)
    def merged_optional_shape(x):
        return _math.prod(x.shape[0:2])

    optimize_merge_batch_dimensions = (
        (len(query.shape) == 5)
        and (len(query.shape) == len(value.shape) == len(key.shape) == len(bias.shape))
        and (
            merged_optional_shape(query)
            == merged_optional_shape(key)
            == merged_optional_shape(value)
        )
    )

    if optimize_merge_batch_dimensions:
        # We need to repeat the attn mask before reshaping
        # This looks like (batch, 8, 1, 4096, 4096) for PTT
        # Which is a reasonable amnt of memory.
        if bias.size(1) != query.size(1):
            bias = bias.repeat(1, query.size(1), 1, 1, 1)

        query = query.flatten(end_dim=1)
        key = key.flatten(end_dim=1)
        value = value.flatten(end_dim=1)
        bias = bias.flatten(end_dim=1)

    return (query, key, value, bias, optimize_merge_batch_dimensions)


def _add_heads_dim(*tensors, dim_per_head):
    """Reshapes the features dimension of tensors to (heads, features per head)"""
    if len(tensors) != 1:
        return tuple(_add_heads_dim(t, dim_per_head=dim_per_head) for t in tensors)
    tensor = tensors[0]
    shape = tensor.shape
    return tensor.view(*shape[:-1], -1, dim_per_head)


def _remove_heads_dim(*tensors):
    if len(tensors) != 1:
        return tuple(_remove_heads_dim(t) for t in tensors)
    tensor = tensors[0]
    return tensor.flatten(start_dim=-2)


class QKVLinear(
    _nn.Module, _LayerMixin
):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        query_dim: int,
        *,
        key_dim: _Optional[int] = None,
        value_dim: _Optional[int] = None,
        query_output_dim: _Optional[int] = None,
        key_output_dim: _Optional[int] = None,
        value_output_dim: _Optional[int] = None,
        bias: bool = False,
        vec_dim: _Optional[_List[int]] = None,
        device=None,
        dtype=None,
    ):
        super().__init__()

        self.query_dim = query_dim
        self.key_dim = key_dim if key_dim is not None else query_dim
        self.value_dim = value_dim if value_dim is not None else query_dim

        self.query_output_dim = (
            self.query_dim if query_output_dim is None else query_output_dim
        )
        self.key_output_dim = self.key_dim if key_output_dim is None else key_output_dim
        self.value_output_dim = (
            self.value_dim if value_output_dim is None else value_output_dim
        )
        dtype = _helpers.get_dtype_from_maybe_string(dtype)
        tensor_meta = {"device": device, "dtype": dtype}

        # Handle vectorized
        self.vec_dim = vec_dim
        if vec_dim is not None:
            linear_cls = _linear.VectorizedLinear
            tensor_meta["vec_dim"] = vec_dim
        else:
            linear_cls = _linear.Linear

        self.query_linear = linear_cls(
            self.query_dim, self.query_output_dim, bias=bias, **tensor_meta
        )
        self.key_linear = linear_cls(
            self.key_dim, self.key_output_dim, bias=bias, **tensor_meta
        )
        self.value_linear = linear_cls(
            self.value_dim, self.value_output_dim, bias=bias, **tensor_meta
        )

    def forward(self, query, key=None, value=None):
        key = key if key is not None else query
        value = value if value is not None else query
        return (
            self.query_linear(query),
            self.key_linear(key),
            self.value_linear(value),
        )


class RoPETransform(_nn.Module, _LayerMixin):
    def __init__(self):
        super().__init__()

    def forward(
        self,
        query: _torch.Tensor,
        key: _Optional[_torch.Tensor] = None,
        value: _Optional[_torch.Tensor] = None,
        *,
        query_rope_coefficients: _torch.Tensor,
        key_rope_coefficients: _Optional[_torch.Tensor] = None,
    ):
        dim_per_head = 2 * query_rope_coefficients.size(-3)
        if key is not None and key_rope_coefficients is None:
            raise ValueError(
                "key_rope_coefficients should not be None when key is not None since key transform is expected."
            )
        if key is None:
            query = _add_heads_dim(query, dim_per_head=dim_per_head)
            query = _rope.rotate(query, rope_coefficients=query_rope_coefficients)
            query = _remove_heads_dim(query)
            return query

        query, key = _add_heads_dim(query, key, dim_per_head=dim_per_head)
        query = _rope.rotate(query, rope_coefficients=query_rope_coefficients)
        key = _rope.rotate(key, rope_coefficients=key_rope_coefficients)
        query, key = _remove_heads_dim(query, key)
        return query, key, value


class QKNorm(_nn.Module, _LayerMixin):
    def __init__(
        self,
        dim_per_head: int,
        *,
        query_norm: _Optional[_ModuleBuilder] = None,
        key_norm: _Optional[_ModuleBuilder] = None,
    ):
        super().__init__()
        self.dim_per_head = dim_per_head
        self.query_norm = _helpers.maybe_build_module(query_norm)
        self.key_norm = _helpers.maybe_build_module(key_norm)

    def forward(
        self,
        query: _torch.Tensor,
        key: _Optional[_torch.Tensor] = None,
        value: _Optional[_torch.Tensor] = None,
    ) -> _torch.Tensor:
        """Scales the projected queries and keys."""
        if key is None:
            query = _add_heads_dim(query, dim_per_head=self.dim_per_head)
        else:
            query, key = _add_heads_dim(query, key, dim_per_head=self.dim_per_head)

        if self.query_norm is not None:
            query = self.query_norm(query)
        if self.key_norm is not None:
            key = self.key_norm(key)

        if key is None:
            query = _remove_heads_dim(query)
            return query
        query, key = _remove_heads_dim(query, key)
        return query, key, value


class SDPAImplementationChoice(str, _enum.Enum):
    """
    An :class:`Enum` for specifying the implementation of scaled dot product attention.
    """

    #: Delegate the implementation choice to |tamm|, which attempts to select the most
    #: efficient available implementation
    AUTO = "AUTO"

    #: Use ``torch.nn.functional.scaled_dot_product_attention()``
    NATIVE_TORCH = "NATIVE_TORCH"

    #: Use :func:`flash_attn.flash_attn_func`
    FLASH = "FLASH"

    #: Use :func:`torch.nn.attention.flex_attention()`
    FLEX = "FLEX"

    #: Use ``xformers.ops.memory_efficient_attention()``
    XFORMERS_MEMORY_EFFICIENT = "XFORMERS_MEMORY_EFFICIENT"

    #: Use a basic PyTorch implementation, which can also output attention probabilities
    BASIC = "BASIC"

    @classmethod
    def _missing_(cls, value):
        return case_insensitive_lookup(cls, value)


class ScaledDotProductAttention(_nn.Module, _LayerMixin):
    """
    Multihead scaled dot product attention layer.  Takes inputs ``query``, ``key``,
    and ``value``.  The shape for ``query`` is
    ``(batch_size, sequence_length, num_heads * dim_per_head)``, and the shape for
    ``key`` and ``value`` is
    ``(batch_size, sequence_length, num_kv_heads * dim_per_head)``.
    Returns an output with the same shape as ``query``.

    Args:
        num_heads (:obj:`int`): The number of attention heads.
        num_kv_heads (:obj:`int`, optional): The number of key-value heads for grouped
            query attention.  This is ``num_heads`` by default, which results in vanilla
            multi-head attention.
        dropout_p (:obj:`float`): The dropout probability.
        implementation (:obj:`SDPAImplementationChoice` member or :obj:`str`): The
            attention implementation to use.  The layer uses ``AUTO`` by default, which
            attempts to select the most efficient implementation available.  If a
            :obj:`str`, this argument must equal the name of a
            :class:`.SDPAImplementationChoice` member (case insensitive).
        scale (:obj:`float`, optional): Scaling factor prior to the softmax.  Defaults
            to ``1 / sqrt(dim_per_head)``.
        output_attentions (:obj:`bool`): Flag that when ``True`` results in the
            inclusion of attentions weights as side outputs. Defaults to ``False``.
        output_kv_state (:obj:`bool`): Flag that when ``True`` results in the
            inclusion of kv_state of current layer as side outputs. Defaults to ``False``.
    """

    def __init__(
        self,
        num_heads: int,
        *,
        num_kv_heads: _Optional[int] = None,
        scale: _Optional[float] = None,
        logits_soft_cap: _Optional[float] = None,
        dropout_p: float = 0.0,
        implementation: _Union[SDPAImplementationChoice, str] = "auto",
        output_attentions: bool = False,
        output_kv_state: bool = False,
        sliding_window_size: _Optional[int] = None,
    ):
        super().__init__()
        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads if num_kv_heads is not None else num_heads
        self.sliding_window_size = sliding_window_size
        if self.num_heads % self.num_kv_heads > 0:
            raise ValueError(
                f"Num kv heads ({self.num_kv_heads}) does not evenly divide num heads "
                f"({self.num_heads})"
            )

        self.logits_soft_cap = logits_soft_cap
        self.dropout_p = dropout_p
        self.implementation = _helpers.get_enum_member_from_name(
            SDPAImplementationChoice, implementation
        )
        self.scale = scale
        self.output_attentions = output_attentions
        self.output_kv_state = output_kv_state

        # Call this function at initialization time to make sure the result is cached
        # so that `torch.compile` works
        _is_flash_attn_available()

        is_impl_flash = self.implementation is SDPAImplementationChoice.FLASH
        if is_impl_flash and not _is_flash_attn_available():
            raise RuntimeError(
                "Created an SDPA layer with flash attention as the implementation "
                "choice, but flash_attn is not available."
            )

    # pylint: disable-next=all
    def forward(
        self,
        query: _torch.Tensor,
        key: _torch.Tensor,
        value: _torch.Tensor,
        attention_mask: _Optional[_torch.Tensor] = None,
        flash_attention_options: _Optional[_Dict] = None,
    ):
        """
        Args:
            query (:obj:`torch.Tensor`): Query tensor of shape ``(batch_size, seq_len_q, num_heads * dim_per_head)``.
            key (:obj:`torch.Tensor`): Key tensor of shape ``(batch_size, seq_len_kv, num_kv_heads * dim_per_head)``.
            value (:obj:`torch.Tensor`): Value tensor of shape ``(batch_size, seq_len_kv, num_kv_heads * dim_per_head)``
            attention_mask (:obj:`torch.Tensor` or Optional): Mask for self-attention or cross-attention of shape
                ``(batch_size, seq_len_q, seq_len_kv)``.
            flash_attention_options (:obj:`dict` or Optional): Additional options for flash attention.
        """

        if self.output_kv_state:
            input_key, input_value = key, value
        dim_per_head = query.size(-1) // self.num_heads
        query, key, value = _add_heads_dim(query, key, value, dim_per_head=dim_per_head)

        if attention_mask is not None and attention_mask.ndim == 3:
            attention_mask = attention_mask[:, None, ...]

        implementation = self._get_implementation(
            query, key, value, flash_options=flash_attention_options
        )

        original_value_shape = value.shape
        (
            query,
            key,
            value,
            attention_mask,
            did_merge_batch_dimension,
        ) = _merge_batch_dimensions(query, key, value, attention_mask)

        if (
            self.output_attentions
            and implementation is not SDPAImplementationChoice.BASIC
        ):
            raise ValueError(
                "Only `BASIC` implementation supports output_attentions. "
                "Please set the implementation to either `AUTO` or `BASIC`."
            )

        kwargs = {
            "query": query,
            "key": key,
            "value": value,
            "bias": attention_mask,
            "scale": self.scale,
            "logits_soft_cap": self.logits_soft_cap,
            "dropout_p": self.dropout_p if self.training else 0.0,
        }

        if implementation is SDPAImplementationChoice.NATIVE_TORCH:
            output = self._sdpa_native_torch(**kwargs)
        elif implementation is SDPAImplementationChoice.FLEX:
            output = self._sdpa_flex(**kwargs)
        elif implementation is SDPAImplementationChoice.XFORMERS_MEMORY_EFFICIENT:
            output = self._sdpa_xformers_memory_efficient(**kwargs)
        elif implementation is SDPAImplementationChoice.BASIC:
            output = self._sdpa_basic(**kwargs)
        elif implementation is SDPAImplementationChoice.FLASH:
            if flash_attention_options is None:
                raise ValueError(
                    "Using Flash SDPA implementation but forward() received None for "
                    "flash_attention_options"
                )
            kwargs = {
                key: val
                for key, val in kwargs.items()
                if key not in ("bias", "logits_soft_cap")
            }
            kwargs.update(flash_attention_options)

            # If merged batch dimension (i.e: in case of parallel track models)
            # we need to repeat some of the arguments for flash attention
            # so that the first dimension matches.
            if did_merge_batch_dimension:
                for flash_attn_key_to_update in [
                    "query_bias",
                    "key_bias",
                    "value_padding",
                ]:
                    if flash_attn_key_to_update not in kwargs:
                        continue
                    tensor = kwargs[flash_attn_key_to_update]
                    repeat_times = query.size(0) // tensor.size(0)
                    tensor = tensor.repeat_interleave(repeat_times, dim=0)
                    kwargs[flash_attn_key_to_update] = tensor

            if self.sliding_window_size is not None:
                kwargs["window_size"] = [self.sliding_window_size, 0]

            if self.logits_soft_cap is not None:
                raise NotImplementedError(
                    "logits_soft_cap is currently unsupported for flash attention"
                )

            output = _flash_attn_func_with_low_rank_mask(**kwargs)
        else:
            raise ValueError(f"SDPA implementation {implementation} not recognized")

        if isinstance(output, _side_outputs.OutputWithSideOutputs):
            new_output = output.output
            if did_merge_batch_dimension:
                new_output = _split_batch_dimensions(
                    output.output, original_value_shape
                )
            new_output = _remove_heads_dim(new_output)
            side_outputs = output.side_outputs
            if self.output_kv_state:
                side_outputs = _side_outputs.merge_side_outputs(
                    side_outputs, {"key": input_key, "value": input_value}
                )
            return _side_outputs.OutputWithSideOutputs(
                new_output, side_outputs=side_outputs
            )

        if did_merge_batch_dimension:
            output = _split_batch_dimensions(output, original_value_shape)
        output = _remove_heads_dim(output)
        if self.output_kv_state:
            output = _side_outputs.OutputWithSideOutputs(
                output, side_outputs={"key": input_key, "value": input_value}
            )
        return output

    def _get_implementation(self, query, key, value, *, flash_options):
        if self.implementation is SDPAImplementationChoice.AUTO:
            return self._get_auto_implementation(
                query, key, value, flash_options=flash_options
            )
        return self.implementation

    def _should_use_flex_attention(self, query):
        if not _IS_FLEX_ATTENTION_AVAILABLE:
            return False

        if _is_torch_base_version_less_than("2.7"):
            return False

        if query.device.type == "mps":
            return False

        dim_per_head = query.size(-1) // self.num_heads
        if dim_per_head < 16:
            return False

        return True

    def _get_auto_implementation(self, query, key, value, *, flash_options):
        if self.output_attentions:
            return SDPAImplementationChoice.BASIC
        if self.logits_soft_cap is not None:
            if self._should_use_flex_attention(query):
                return SDPAImplementationChoice.FLEX
            return SDPAImplementationChoice.BASIC

        if (
            flash_options is not None
            and _is_flash_attn_available()
            and _qkv_flash_attention_compatible(query, key, value)
            and self.num_heads <= 256
            and self.num_kv_heads <= 256
        ):
            return SDPAImplementationChoice.FLASH

        return SDPAImplementationChoice.NATIVE_TORCH

    def _sdpa_xformers_memory_efficient(
        self,
        *,
        query,
        key,
        value,
        bias,
        dropout_p,
        scale=None,
        logits_soft_cap=None,
    ):
        if logits_soft_cap is not None:
            raise NotImplementedError(
                "XFORMERS_MEMORY_EFFICIENT attention does not support logits_soft_cap"
            )
        query, key, value = self._maybe_tile_qkv_for_gqa(query, key, value)
        output = _xformers_optimized_attention(
            query,
            key,
            value,
            attn_bias=bias,
            p=dropout_p,
            scale=scale,
        )
        return output

    def _sdpa_native_torch(
        self, *, query, key, value, bias, dropout_p, scale=None, logits_soft_cap=None
    ):
        if logits_soft_cap is not None:
            raise NotImplementedError(
                "NATIVE_TORCH attention does not support logits_soft_cap"
            )

        query, key, value = self._maybe_tile_qkv_for_gqa(query, key, value)
        query = query.transpose(-3, -2)
        key = key.transpose(-3, -2)
        value = value.transpose(-3, -2)

        if self.sliding_window_size is not None:
            if bias.shape[-1] == bias.shape[-2]:
                # Square matrices (such as for training) we can use triu for sliding window mask
                bias = bias.triu_(-self.sliding_window_size)
            elif bias.shape[-1] > bias.shape[-2]:
                # For decode w/ kv cache, the shapes are non-square, the last dimension
                # is which keys are attended to by current query; mask them out according to window size
                #
                # bias = [[True, True, True, True, True, True, False],
                #         [True, True, True, True, True, True, True]]
                # sliding_window_size = 3
                # kv_seq_len = 7
                # query_seq_len = 2
                # end_indices = [2, 3]
                # seq_indices = [0, 1, 2, 3, 4, 5, 6]
                # mask = [[False, False, True, True, True, True, False],
                #         [False, False, False, True, True, True, True]]
                kv_seq_len = bias.shape[-1]
                query_seq_len = bias.shape[-2]
                query_indices = _torch.arange(query_seq_len, device=bias.device)
                end_indices = (
                    kv_seq_len
                    - self.sliding_window_size
                    - 1
                    - (query_seq_len - query_indices - 1)
                )

                seq_indices = _torch.arange(kv_seq_len, device=bias.device)
                mask = seq_indices[None, :] >= end_indices[:, None]
                bias[:, :, :query_seq_len, :] = _torch.logical_and(
                    bias[:, :, :query_seq_len, :], mask[None, None, :, :]
                )

        kwargs = {"attn_mask": bias, "dropout_p": dropout_p, "is_causal": False}
        if scale is not None:
            # don't include this always because it's not supported in torch 2.0
            kwargs["scale"] = scale
        # pylint: disable-next=not-callable
        output = _nn.functional.scaled_dot_product_attention(
            query, key, value, **kwargs
        )

        return output.transpose(-3, -2)

    def _sdpa_basic(
        self, query, key, value, bias, dropout_p, scale=None, logits_soft_cap=None
    ):
        """
        Returns attentions weights as side outputs,
        which is calculated after the attention softmax.
        Attentions weights are used to compute the weighted average
        in the self-attention heads. This method is used when
        output_attentions is set to ``True``.
        Ref: torch.nn.functional.scaled_dot_product_attention
        """
        query, key, value = self._maybe_tile_qkv_for_gqa(query, key, value)
        query = query.transpose(-3, -2)
        key = key.transpose(-3, -2)
        value = value.transpose(-3, -2)

        scale_factor = 1 / _math.sqrt(query.size(-1)) if scale is None else scale

        attn_weight = (scale_factor * query) @ key.transpose(-2, -1)

        if logits_soft_cap is not None:
            attn_weight = _tamm_F.soft_cap(attn_weight, cap=logits_soft_cap)

        if bias is not None:
            if bias.dtype is _torch.bool:
                zero = _torch.tensor(0.0, dtype=attn_weight.dtype, device=bias.device)
                neginf = _torch.tensor(
                    float("-inf"), dtype=attn_weight.dtype, device=bias.device
                )
                bias = _torch.where(bias, zero, neginf)
            attn_weight += bias

        attn_weight = _torch.softmax(attn_weight, dim=-1)

        dropout_attn_weight = _torch.dropout(
            attn_weight, dropout_p, train=self.training
        )
        attn = dropout_attn_weight @ value
        attn = attn.transpose(-3, -2)
        if self.output_attentions:
            return _side_outputs.OutputWithSideOutputs(
                attn, side_outputs={"attentions": attn_weight}
            )
        return attn

    @_torch.compile
    def _sdpa_flex(
        self, *, query, key, value, bias, dropout_p, scale=None, logits_soft_cap=None
    ):
        # pylint: disable=unused-argument,too-many-locals

        if dropout_p != 0.0:
            raise NotImplementedError("flex attention does not support dropout_p")

        query = query.transpose(-3, -2)
        key = key.transpose(-3, -2)
        value = value.transpose(-3, -2)

        if self.sliding_window_size is not None:
            bias = bias.triu_(-self.sliding_window_size)

        if bias is not None and bias.is_floating_point():
            raise NotImplementedError(
                "FLEX attention does not support floating point attention masks"
            )

        bool_mask = bias
        if bool_mask.size(1) == 1:
            bool_mask = _tamm_F.expand_dim(bool_mask, query.size(1), dim=1)

        def mask_mod(b, h, q_idx, kv_idx):
            return bool_mask[b, h, q_idx, kv_idx]

        # TODO: Fix the graph break once PyTorch 2.8 is out.
        # As of PyTorch 2.7 and earlier, flex attention with block masks is not
        # fully graph compilable. This should be fixed in PyTorch 2.8+ as discussed
        # in https://github.com/pytorch/pytorch/issues/139374
        block_mask = _flex_attention.create_block_mask(
            mask_mod,
            B=query.shape[0],
            H=query.shape[1],
            Q_LEN=query.shape[2],
            KV_LEN=key.shape[2],
            device=str(query.device),
        )

        kwargs = {"block_mask": block_mask}
        if self.num_heads != self.num_kv_heads:
            kwargs["enable_gqa"] = True

        if logits_soft_cap is not None:

            def compute_soft_cap_score(score, *_):
                return _tamm_F.soft_cap(score, cap=logits_soft_cap)

            kwargs["score_mod"] = compute_soft_cap_score

        if scale is not None:
            kwargs["scale"] = scale

        output = _flex_attention.flex_attention(query, key, value, **kwargs)

        return output.transpose(-3, -2)

    def _maybe_tile_qkv_for_gqa(
        self, query: _torch.Tensor, key: _torch.Tensor, value: _torch.Tensor
    ) -> _Tuple[_torch.Tensor, _torch.Tensor, _torch.Tensor]:
        key = self._tile_single_input_for_gqa(key)
        value = self._tile_single_input_for_gqa(value)
        return query, key, value

    def _tile_single_input_for_gqa(self, key_or_value: _torch.Tensor) -> _torch.Tensor:
        heads_ratio = self.num_heads // self.num_kv_heads
        if heads_ratio == 1:
            return key_or_value
        result = _torch.tile(key_or_value, (heads_ratio,))
        return result.reshape(*result.shape[:-2], self.num_heads, -1)

    def extra_repr(self) -> str:
        implementation = self.implementation.name.lower()
        return (
            f"num_heads={self.num_heads},\n"  # noqa
            f"scale={self.scale},\n"  # noqa
            f"logits_soft_cap={self.logits_soft_cap},\n"  # noqa
            f"dropout_p={self.dropout_p},\n"  # noqa
            f"implementation='{implementation}',"  # noqa
        )


@_dynamo.disable
def _xformers_optimized_attention(*args, **kwargs):
    # pylint: disable-next=import-outside-toplevel,import-error
    from xformers.ops import memory_efficient_attention

    return memory_efficient_attention(*args, **kwargs)


# DEPRECATED
# pylint: disable=all
from tamm import _compat  # noqa

_compat.register_backward_compatibility_import(
    __name__,
    "TransformerLayer",
    "tamm.layers.transformer.layer.TransformerLayer",
)
