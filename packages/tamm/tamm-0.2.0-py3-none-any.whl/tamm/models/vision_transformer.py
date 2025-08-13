"""
models.vision_transformer
=========================

.. autoclass:: tamm.models.VisionTransformer
    :show-inheritance:
    :members:

.. autoclass:: tamm.models.configs.VisionTransformerConfig
"""

from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

from tamm import layers as _layers
from tamm.models.common import ModelMixin as _ModelMixin


class VisionTransformer(_layers.VisionTransformerEncoder, _ModelMixin):
    """A transformer encoder for image inputs."""

    @classmethod
    def create_basic_builder(
        cls,
        *,
        hidden_dim: int = 768,
        num_layers: int = 12,
        num_heads: int = 12,
        hidden_dim_scale_factor: float = 4.0,
        input_dim: int = 3,
        patch_size: _Union[int, _Tuple[int, int]] = (16, 16),
        stride: _Union[int, _Tuple[int, int], None] = None,
        apply_positional_embedding: bool = True,
        positional_embedding_shape: _Optional[_Tuple[int, int]] = (14, 14),
        positional_embedding_interpolation: _Optional[str] = None,
        num_class_tokens: int = 0,
        activation: str = "relu",
        norm_eps: float = 1e-5,
        norm_bias: bool = False,
        attention_logits_soft_cap: _Optional[float] = None,
        output_transform: _Optional[_layers.common.LayerBuilder] = None,
        attention_dropout_p: float = 0.0,
        hidden_dropout_p: float = 0.0,
    ):
        """
        Args:
            hidden_dim (:obj:`int`): The hidden dim for the model's transformer layers.
            num_layers (:obj:`int`): The number of transformer layers.
            num_heads (:obj:`int`): The number of attention heads.
            hidden_dim_scale_factor (:obj:`float`, optional): For feed-forward layers,
                the ratio of the layer's hidden dimension to the layer's input
                dimension.
            input_dim (:obj:`int`): The input dimension (number of channels) for the
                model's image inputs.
            patch_size (:obj:`int` or pair of :obj:`int`): The kernel size for the
                :obj:`.ConvEmbedding` layer.
            stride (:obj:`int` or pair of :obj:`int`): The stride for the convolutional
                embedding.  If ``None``, this defaults to ``patch_size``.
            apply_positional_embedding (:obj:`bool`): A flag for including a
                :obj:`.SpatialPositionalEmbedding` in the embedding layer.  Defaults to
                ``True``.
            positional_embedding_shape (pair of :obj:`int`): The height and width of
                the positional embedding layer.
            positional_embedding_interpolation (:obj:`str`): An optional
                :class:`.Interpolation` mode (such as ``"bicubic"``) for rescaling the
                positional embeddings to match the shape of the input embeddings.
                Defaults to ``None``, in which case the input embedding shape must match
                the positional embeddings shape.
            num_class_tokens (:obj:`int`): The number of class tokens.
            activation (:obj:`str`, optional): The activation type.  Defaults to ``"relu"``.
            norm_eps (:obj:`float`): The ``eps`` value for norm layers.
            norm_bias (:obj:`bool`, optional): Whether to include a bias term in the
                normalization layer.  Defaults to ``False``.
            attention_logits_soft_cap (:obj:`float`, optional): An optional positive
                threshold for soft-capping attention logits.  Defaults to ``None``,
                which implies no capping.
            output_transform (:obj:`.LayerBuilder`, optional): An optional builder for
                the output transform layer.  Defaults to ``None``.
            attention_dropout_p (:obj:`float`, optional): The dropout rate for
                attention probabilities.  Defaults to 0.
            hidden_dropout_p (:obj:`float`, optional): The dropout rate for hidden
                states.
        """

        # pylint: disable=too-many-locals

        norm = _layers.LayerNorm.Builder(
            [hidden_dim],
            eps=norm_eps,
            bias=norm_bias,
        )

        class_token_embedding = _layers.ConstantEmbedding.Builder(
            num_embeddings=num_class_tokens,
            dim=hidden_dim,
        )
        conv_embedding = _layers.ConvEmbedding.create_builder(
            input_dim=input_dim,
            output_dim=hidden_dim,
            kernel_size=patch_size,
            stride=stride,
            apply_positional_embedding=apply_positional_embedding,
            positional_embedding_shape=positional_embedding_shape,
        )
        if apply_positional_embedding:
            conv_embedding.positional_encoding.interpolation = (
                positional_embedding_interpolation
            )
        conv_embedding.norm = norm
        embedding = _layers.UnionEmbedding.Builder(
            {
                "class_tokens": class_token_embedding,
                "convolution_tokens": conv_embedding,
            }
        )

        class_token_seg = _layers.ConstantSegmentation.Builder(num_class_tokens)
        conv_seg = (
            _layers.ConvEmbeddingPaddingTransform.create_builder_from_convolution_layer(
                conv_embedding.convolution
            )
        )
        segmentation_layers = {
            "class_tokens": class_token_seg,
            "convolution_tokens": conv_seg,
        }
        segmentation = _layers.UnionSegmentation(segmentation_layers)

        attention_mask = _layers.AttentionMask.Builder()

        attention = _layers.TransformerAttention.create_builder(
            target_dim=hidden_dim,
            norm=norm,
            num_heads=num_heads,
            attention_dropout_p=attention_dropout_p,
            hidden_dropout_p=hidden_dropout_p,
            qkv_transform_bias=True,
            output_transform_bias=True,
        )
        if attention_logits_soft_cap is not None:
            attention.scaled_dot_product_attention.logits_soft_cap = (
                attention_logits_soft_cap
            )

        feed_forward = _layers.TransformerFeedForward.create_builder(
            input_dim=hidden_dim,
            hidden_dim=round(hidden_dim * hidden_dim_scale_factor),
            norm=norm,
            activation=activation,
            activation_dropout_p=hidden_dropout_p,
            output_dropout_p=hidden_dropout_p,
            hidden_transform_bias=True,
            output_transform_bias=True,
        )

        layer = _layers.TransformerLayer.Builder(
            attention=attention, feed_forward=feed_forward
        )
        layers = _layers.UniformTransformerLayerSequence.Builder(
            layer, num_layers=num_layers
        )

        if isinstance(output_transform, _layers.common.ModuleConfig):
            output_transform = output_transform.create_builder()

        return cls.Builder(
            embedding=embedding,
            segmentation=segmentation,
            attention_mask=attention_mask,
            layers=layers,
            output_norm=norm,
            output_transform=output_transform,
        )
