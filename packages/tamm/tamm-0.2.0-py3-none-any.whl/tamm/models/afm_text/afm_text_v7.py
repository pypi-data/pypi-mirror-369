"""
models.afm_text
===============

.. autoclass:: tamm.models.afm_text.AFMTextV7
    :show-inheritance:
    :members:
"""

import copy as _copy
from typing import Optional as _Optional
from typing import Union as _Union

from tamm import layers as _layers
from tamm.models import common as _models_common


class AFMTextV7(_layers.CausalLMTransformer, _models_common.ModelMixin):
    """
    AFM Text v7 model.  This is a decoder-only causal LM with:

    * Key/value reuse across layers
    * Rotary positional embeddings
    * Grouped query attention
    * Tied embedding and head layers
    """

    @classmethod
    def create_basic_builder(
        cls,
        *,
        vocab_size: int = 153600,
        hidden_dim: int = 2048,
        num_layers: int = 56,
        num_kv_reuse_layers: int = 21,
        num_heads: int = 16,
        num_kv_heads: _Optional[int] = 2,
        hidden_dim_scale_factor: float = 3.25,
        rope_theta: float = 500000.0,
        attention_dropout_p: float = 0.0,
        hidden_dropout_p: float = 0.0,
        include_loss_layer: bool = False,
        output_hidden_states: bool = False,
        output_attentions: bool = False,
        sdpa_implementation: _Union[
            _layers.attention.SDPAImplementationChoice, str
        ] = "auto",
    ):
        """
        Creates and returns a configured builder for the model.

        Args:
            vocab_size (:obj:`int`): The vocab size.
            hidden_dim (:obj:`int`): The number of features per token.
            num_layers (:obj:`int`): The number of transformer layers.
            num_kv_reuse_layers (:obj:`int`):  The number of KV reuse attention layers.
                If larger than ``0``, the first ``num_layers - num_kv_reuse_layers``
                layers are regular layers, while the final ``num_kv_reuse_layers`` layers
                reuse ``keys`` and ``values`` states from the last regular layer.
                Defaults to ``21``.
            num_heads (:obj:`int`): The number of attention heads.
            num_kv_heads (:obj:`int`, optional): The number of key-value attention
                heads for grouped query attention.  If ``None``, this defaults to
                ``num_heads``.  If not ``None``, this value must evenly divide
                ``num_heads``.
            hidden_dim_scale_factor (:obj:`float`, optional): For feed-forward layers,
                the ratio of the layer's hidden dimension to the layer's input
                dimension.  Defaults to ``3.25``.
            rope_theta (:obj:`float`, optional): The theta value for rotary positional
                embeddings.  Defaults to ``500000``.
            attention_dropout_p (:obj:`float`, optional): The dropout rate for
                attention probabilities.  Defaults to 0.
            hidden_dropout_p (:obj:`float`, optional): The dropout rate for hidden
                states.
            include_loss_layer (:obj:`bool`): Flag for including a cross-entropy loss
                layer in the model when ``True``.  Defaults to ``False``.  Unlike
                Hugging Face, this layer does not shift the labels.
            output_hidden_states (:obj:`bool`): Flag that when ``True`` results in the
                inclusion of hidden states in the final output of the model.
                Specifically, this is a list of ``num_layers + 1`` tensors that includes
                the initial embeddings and the output of each layer.  Defaults to
                ``False``.
            output_attentions (:obj:`bool`): Flag that when ``True`` results in the
                inclusion of attentions in the output of the model.
                Specifically, this is a list of ``num_layers`` tensors that includes
                attentions of each layer.  Defaults to ``False``.
            sdpa_implementation (:obj:`SDPAImplementationChoice` member or :obj:`str`):
                The attention implementation to use.  The layer uses ``AUTO`` by
                default, which attempts to select the most efficient implementation
                available.  If a :obj:`str`, this argument must equal the name of a
                :class:`.SDPAImplementationChoice` member (case-insensitive).

        Returns:
            The configured :obj:`.AFMTextModelBuilder`.
        """

        # pylint: disable=too-many-locals

        builder = cls.Builder()

        builder.embedding = _layers.Embedding.Builder(
            vocab_size, hidden_dim, padding_idx=0
        )
        builder.attention_mask = _layers.transformer.AttentionMask.Builder(
            is_causal=True
        )

        dim_per_head = hidden_dim // num_heads
        builder.positional_encoding = _layers.RotaryPositionalEmbedding.Builder(
            dim_per_head=dim_per_head, theta=rope_theta
        )

        norm = _layers.RMSNorm.Builder([hidden_dim])

        attention = _layers.attention.TransformerAttention.create_builder(
            target_dim=hidden_dim,
            num_heads=num_heads,
            num_kv_heads=num_kv_heads,
            norm=norm,
            apply_rope=True,
            apply_qk_norm=True,
            attention_dropout_p=attention_dropout_p,
            hidden_dropout_p=hidden_dropout_p,
            output_attentions=output_attentions,
            sdpa_implementation=sdpa_implementation,
        )
        attention.qk_norm.query_norm = _layers.RMSNorm.Builder([dim_per_head])
        attention.qk_norm.key_norm = _layers.RMSNorm.Builder([dim_per_head])

        feed_forward = _layers.feed_forward.TransformerFeedForward.create_builder(
            input_dim=hidden_dim,
            hidden_dim=round(hidden_dim * hidden_dim_scale_factor),
            norm=norm,
            activation=_layers.activation.SwiGLU.Builder(),
            activation_dropout_p=hidden_dropout_p,
            output_dropout_p=hidden_dropout_p,
        )

        layer = _layers.transformer.TransformerLayer.Builder(
            attention=attention, feed_forward=feed_forward
        )

        if num_kv_reuse_layers == 0:
            builder.layers = _layers.UniformTransformerLayerSequence.Builder(
                layer, num_layers=num_layers, output_hidden_states=output_hidden_states
            )
        else:
            builder.layers = cls._create_layers_with_kv_reuse(
                layer=layer,
                num_kv_reuse_layers=num_kv_reuse_layers,
                num_layers=num_layers,
                hidden_dim=hidden_dim,
                output_hidden_states=output_hidden_states,
            )

        builder.output_norm = norm
        builder.output_transform_build_mode = "pass_embedding"
        builder.output_transform = _layers.TiedWeightLinear.Builder(
            parameter_name="weight"
        )

        if include_loss_layer:
            builder.loss = _layers.FlattenedCrossEntropyLoss.Builder()

        return builder

    @staticmethod
    def _create_layers_with_kv_reuse(
        layer, *, num_kv_reuse_layers, num_layers, hidden_dim, output_hidden_states
    ):
        num_regular_layers = num_layers - num_kv_reuse_layers
        if num_regular_layers <= 0:
            raise ValueError(
                "num_regular_layers must be at least 1, but it has value "
                f"{num_regular_layers}"
            )

        segment_0 = [_copy.deepcopy(layer) for _ in range(num_regular_layers)]
        segment_0[-1].attention.scaled_dot_product_attention.output_kv_state = True
        segment_0 = _layers.TransformerLayerSequence.Builder(
            *segment_0, output_hidden_states=output_hidden_states
        )

        kv_reuse_layer = _copy.deepcopy(layer)
        q_transform = _layers.Linear.Builder(hidden_dim, hidden_dim, bias=False)
        sdpa = kv_reuse_layer.attention.scaled_dot_product_attention
        kv_reuse_layer.attention = _layers.KVReuseTransformerAttention.Builder(
            norm=kv_reuse_layer.attention.norm,
            q_transform=q_transform,
            rope_transform=kv_reuse_layer.attention.rope_transform,
            q_norm=kv_reuse_layer.attention.qk_norm,
            scaled_dot_product_attention=sdpa,
            output_transform=kv_reuse_layer.attention.output_transform,
            dropout=kv_reuse_layer.attention.dropout,
            residual_connection=kv_reuse_layer.attention.residual_connection,
        )
        if kv_reuse_layer.attention.q_norm is not None:
            kv_reuse_layer.attention.q_norm.key_norm = None
        segment_1 = _layers.UniformTransformerLayerSequence.Builder(
            kv_reuse_layer,
            num_layers=num_kv_reuse_layers,
            output_hidden_states=output_hidden_states,
        )

        return _layers.KVReuseTransformerLayerSequence.Builder(
            segment_0=segment_0, segment_1=segment_1
        )
