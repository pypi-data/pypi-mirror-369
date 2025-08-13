"""
This submodule implements different pooling modules.

.. autoclass:: tamm.layers.SimpleAdaptiveAvgPooling
    :show-inheritance:
    :members: forward

.. autoclass:: tamm.layers.ConvPooler
    :members: create_basic_builder
"""

from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

from tamm.layers import activation as _activation
from tamm.layers import basic as _basic
from tamm.layers import convolution as _convolution
from tamm.layers import embedding as _embedding
from tamm.layers import feed_forward as _feed_forward
from tamm.layers import norm as _norm
from tamm.layers import sequential as _sequential
from tamm.layers import torch_nn as _torch_nn
from tamm.layers.common import ConfigurableLayerMixin as _ConfigurableLayerMixin
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.positional_encoding import (
    SpatialPositionalEmbedding as _SpatialPositionalEmbedding,
)
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class SimpleAdaptiveAvgPooler(_nn.Module, _LayerMixin):
    """
    Applies average pooling to produce outputs with a specific shape.
    For the pooling, this layer uses ``stride = input_size // output_size`` and
    ``kernel_size = input_size - (output_size - 1) * stride``.  While this is a
    common way to perform adaptive average pooling, note that it may differ
    from :class:`torch.nn.AdaptiveAvgPool2d`.

    This layer expects inputs in NCHW format.

    Args:
        output_shape (:obj:`tuple` or :obj:`int`): The target height and width of the
            output.  This can be a single :obj:`int` for a square.  If either height
            or width are ``None``, then the output dimension is the same as the input
            dimension.
    """

    def __init__(self, output_shape: _Union[int, _Tuple[int, int]]):
        super().__init__()
        try:
            height, width = output_shape
        except TypeError:
            height, width = (output_shape, output_shape)

        if not isinstance(height, (int, type(None))):
            raise TypeError(f"height must be an integer or None, not a {type(height)}")
        if not isinstance(width, (int, type(None))):
            raise TypeError(f"width must be an integer or None, not a {type(width)}")

        self.output_shape = (height, width)

    def extra_repr(self):
        return f"output_shape={self.output_shape}"

    def forward(self, x: _torch.Tensor) -> _torch.Tensor:
        """
        Args:
            x (:obj:`torch.Tensor`): The input tensor in NCHW format.
        """

        input_shape = x.shape[-2:]
        output_shape = tuple(
            odim if odim is not None else idim
            for idim, odim in zip(input_shape, self.output_shape)
        )

        stride = tuple(idim // odim for idim, odim in zip(input_shape, output_shape))
        kernel_size = tuple(
            idim - (odim - 1) * stride_i
            for idim, odim, stride_i in zip(input_shape, output_shape, stride)
        )

        output = _torch.nn.functional.avg_pool2d(  # pylint: disable=not-callable
            x, kernel_size=kernel_size, stride=stride, padding=0
        )

        true_output_shape = output.shape[-2:]
        if true_output_shape != output_shape:
            raise ValueError(
                f"Output shape is not as expected ({true_output_shape} != "
                f"{output_shape}) "
            )

        return output


class CAbstractorPooler(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    An image pooler from the paper `Honeybee: Locality-enhanced Projector for
    Multimodal LLM <https://arxiv.org/abs/2312.06742>`__.  This layer transforms
    2D embeddings using a convolution block, 2D pooler, and then another
    convolution block.  It also contains various layers for extra tokens, positional
    encodings, and feed forward passes.

    This layer expects inputs in channels-last format.
    """

    def __init__(
        self,
        *,
        drop_tokens: _OptionalModuleOrBuilder = None,
        to_channels_first: _ModuleOrBuilder,
        positional_encoding: _OptionalModuleOrBuilder = None,
        convolution_0: _OptionalModuleOrBuilder = None,
        pooler: _ModuleOrBuilder,
        convolution_1: _OptionalModuleOrBuilder = None,
        to_channels_last: _ModuleOrBuilder,
        feed_forward: _OptionalModuleOrBuilder = None,
        add_tokens: _OptionalModuleOrBuilder = None,
    ):
        layers = {
            "drop_tokens": drop_tokens,
            "to_channels_first": to_channels_first,
            "positional_encoding": positional_encoding,
            "convolution_0": convolution_0,
            "pooler": pooler,
            "convolution_1": convolution_1,
            "to_channels_last": to_channels_last,
            "feed_forward": feed_forward,
            "add_tokens": add_tokens,
        }
        super().__init__(layers)

    @classmethod
    def create_basic_builder(  # pylint: disable=arguments-differ
        cls,
        *,
        input_dim: int,
        convolution_output_dim: _Optional[int] = None,
        feed_forward_hidden_dim: _Optional[int] = None,
        output_dim: _Optional[int] = None,
        apply_positional_embedding: bool = False,
        positional_embedding_shape: _Optional[_Tuple[int, int]] = None,
        positional_embedding_interpolation: _Optional[str] = None,
        blocks_per_regnet_stage: int = 3,
        regnet_activation: str = "relu",
        norm_eps: float = 1e-5,
        norm_bias: bool = False,
        squeeze_excitation_reduced_dim: _Optional[int] = None,
        squeeze_excitation_bias: bool = False,
        pooler_output_shape: _Tuple[int, int],
        feed_forward_activation: str = "relu",
        num_prepend_tokens: int = 0,
        num_append_tokens: int = 0,
    ):
        """
        Creates a builder for a :obj:`.CAbstractorPooler`.

        Args:
            input_dim (:obj:`int`): The number of features in the inputs.
            convolution_output_dim (:obj:`int`, optional): The output dimension of the
                convolution stages.  If ``None``, this defaults to ``input_dim``.
            feed_forward_hidden_dim (:obj:`int`, optional): The hidden dimension of the
                feed forward layer.  If ``None``, this defaults to
                ``convolution_output_dim``.
            output_dim (:obj:`int`, optional): The output dimension of the layer.  If
                ``None``, this defaults to ``input_dim``.
            apply_positional_embedding (:obj:`bool`): A flag for applying positional
                embeddings.  Defaults to ``False``.
            positional_embedding_shape (pair of :obj:`int`): The height and width of
                the spatial positional embedding.
            positional_embedding_interpolation (:obj:`str`): The mode for the
                :class:`Interpolation` layer for resizing positional embeddings.
                Defaults to ``None``, which means no interpolation.
            blocks_per_regnet_stage (:obj:`int`): The number of blocks in each
                convolution stage.
            regnet_activation (:obj:`str`): The activation type for the convolution
                stages.
            norm_eps (:obj:`float`): The epsilon value for norm layers in the
                convolution stages.
            norm_bias (:obj:`bool`): A flag for including a bias parameter in the
                norm layers of convolution stages.  Defaults to ``False``.
            squeeze_excitation_reduced_dim (:obj:`int`): The "squeezed" dimension for
                :class:`.SqueezeExcitation` layers in the convolution stages.
            squeeze_excitation_bias (:obj:`bool`): A flag for including a bias parameter
                in the :class:`.SqueezeExcitation` layers.
            pooler_output_shape (pair of :obj:`int`): The height and width of the
                adaptive pooler's outputs.
            feed_forward_activation (:obj:`str`): The activation type for the
                feed-forward layer.
            num_prepend_tokens (:obj:`int`): The number of constant embedding tokens
                to prepend to the output sequence.
            num_append_tokens (:obj:`int`): The number of constant embedding tokens to
                append to the output sequence.

        Returns:
            The configured :obj:`.LayerBuilder`.
        """

        # pylint: disable=too-many-locals
        if convolution_output_dim is None:
            convolution_output_dim = input_dim
        if feed_forward_hidden_dim is None:
            feed_forward_hidden_dim = convolution_output_dim
        if output_dim is None:
            output_dim = input_dim

        kwargs = {}
        kwargs["drop_tokens"] = _basic.SelectByKey.Builder("convolution_tokens")
        kwargs["to_channels_first"] = _basic.ChannelsLastToFirst.Builder()

        if apply_positional_embedding:
            kwargs["positional_encoding"] = _SpatialPositionalEmbedding.Builder(
                positional_embedding_shape,
                dim=input_dim,
                interpolation=positional_embedding_interpolation,
            )

        regnet_kwargs = {
            "num_blocks": blocks_per_regnet_stage,
            "activation": regnet_activation,
            "norm": "layer_norm",
            "norm_eps": norm_eps,
            "norm_bias": norm_bias,
            "squeeze_excitation_reduced_dim": squeeze_excitation_reduced_dim,
            "squeeze_excitation_bias": squeeze_excitation_bias,
        }
        kwargs["convolution_0"] = _convolution.ResNetStage.create_regnet_builder(
            input_dim=input_dim,
            dim_per_group=1,
            output_dim=convolution_output_dim,
            **regnet_kwargs,
        )

        kwargs["pooler"] = SimpleAdaptiveAvgPooler.Builder(pooler_output_shape)

        kwargs["convolution_1"] = _convolution.ResNetStage.create_regnet_builder(
            input_dim=convolution_output_dim,
            output_dim=convolution_output_dim,
            dim_per_group=1,
            **regnet_kwargs,
        )

        kwargs["to_channels_last"] = _basic.ChannelsFirstToLast.Builder(
            flatten_spatial_dims=True
        )

        kwargs["feed_forward"] = _feed_forward.FeedForward.create_builder(
            input_dim=convolution_output_dim,
            hidden_dim=feed_forward_hidden_dim,
            output_dim=output_dim,
            activation=feed_forward_activation,
            hidden_transform_bias=True,
            output_transform_bias=True,
        )

        if num_prepend_tokens > 0 or num_append_tokens > 0:
            kwargs["add_tokens"] = _embedding.ConcatEmbedding.Builder(
                dim=output_dim,
                num_start=num_prepend_tokens,
                num_end=num_append_tokens,
            )

        return cls.Builder(**kwargs)


class AdaptiveConvPooler(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    An image pooling layer which performs a convolution and optional norm/activation, followed by a pooling layer.
    This layer expects inputs in NHWC format (channels-last).  The output has shape
    ``(batch size, sequence len, output dim)``, where the sequence length is determined by the pooler layer.
    """

    def __init__(
        self,
        *,
        to_channels_first: _ModuleOrBuilder,
        convolution: _ModuleOrBuilder,
        norm: _OptionalModuleOrBuilder = None,
        activation: _activation.ActivationSpecType = "relu",
        pooler: _ModuleOrBuilder,
        to_channels_last: _ModuleOrBuilder,
    ):
        activation = _activation.create_activation_layer(activation)
        layers = {
            "to_channels_first": to_channels_first,
            "convolution": convolution,
            "norm": norm,
            "activation": activation,
            "pooler": pooler,
            "to_channels_last": to_channels_last,
        }
        super().__init__(layers)

    @classmethod
    def create_basic_builder(  # pylint: disable=arguments-differ,too-many-locals
        cls,
        *,
        input_dim: int,
        output_dim: _Optional[int] = None,
        kernel_size: _Union[int, _Tuple[int, int]],
        stride: _Union[int, _Tuple[int, int]] = 1,
        padding: _Union[str, int, _Tuple[int, int]] = 0,
        bias: bool = False,
        activation: _activation.ActivationSpecType = "relu",
        norm: str = "rms_norm",
        norm_bias: bool = False,
        norm_eps: float = 1e-5,
        pooler_output_shape: _Tuple[int, int],
    ):
        """
        Creates a builder for a :obj:`.AdaptiveConvPooler`.

        Args:
            input_dim (:obj:`int`): The number of features in the inputs.
            output_dim (:obj:`int`): The number of features in the outputs.  If ``None``, defaults to ``input_dim``.
            kernel_size (:obj:`Union[int, Tuple[int, int]]`): The kernel size of the convolution.
            stride (:obj:`Union[int, Tuple[int, int]]`): The stride of the convolution.  Defaults to ``1``.
            padding (:obj:`Union[str, int, Tuple[int, int]]`): The padding of the convolution.  Defaults to ``0``.
            bias (:obj:`bool`, optional): Whether to include a bias term in the convolution layer.  Defaults
                to ``False``.
            activation (:obj:`str`, optional): The activation type.  Defaults to ``"relu"``.
            norm (:obj:`str`, optional): The normalization type.  Defaults to ``"rms_norm"``.
            norm_bias (:obj:`bool`, optional): Whether to include a bias term in the normalization layer.  Defaults
                to ``False``.
            norm_eps (:obj:`float`, optional): The norm epsilon value.  Defaults to ``1e-5``.
            pooler_output_shape (pair of :obj:`int`): The height and width of the
                adaptive pooler's outputs.

        Returns:
            The configured :obj:`.LayerBuilder`.
        """
        if output_dim is None:
            output_dim = input_dim

        to_channels_first = _basic.ChannelsLastToFirst.Builder()
        convolution = _convolution.Conv2d.Builder(
            input_dim,
            output_dim,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            bias=bias,
        )

        if norm is not None:
            norm = _norm.create_norm_builder(
                (output_dim,), norm, dim=1, bias=norm_bias, eps=norm_eps
            )

        pooler = SimpleAdaptiveAvgPooler.Builder(pooler_output_shape)

        to_channels_last = _basic.ChannelsFirstToLast.Builder(flatten_spatial_dims=True)

        return cls.Builder(
            to_channels_first=to_channels_first,
            convolution=convolution,
            norm=norm,
            activation=activation,
            pooler=pooler,
            to_channels_last=to_channels_last,
        )


class ConvPooler(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    An image pooling layer that applies the following layer sequence:

    * Channels last-to-first
    * Convolution
    * Optional padding
    * Norm
    * Activation
    * Average pooling 2D
    * Channels first-to-last
    """

    def __init__(
        self,
        *,
        to_channels_first: _ModuleOrBuilder,
        convolution: _ModuleOrBuilder,
        padding: _OptionalModuleOrBuilder,
        norm: _OptionalModuleOrBuilder = None,
        activation: _activation.ActivationSpecType = "relu",
        pooler: _ModuleOrBuilder,
        to_channels_last: _ModuleOrBuilder,
    ):
        activation = _activation.create_activation_layer(activation)
        layers = {
            "to_channels_first": to_channels_first,
            "convolution": convolution,
            "padding": padding,
            "norm": norm,
            "activation": activation,
            "pooler": pooler,
            "to_channels_last": to_channels_last,
        }
        super().__init__(layers)

    @classmethod
    def create_basic_builder(  # pylint: disable=arguments-differ,too-many-locals
        cls,
        *,
        input_dim: int,
        output_dim: _Optional[int] = None,
        pad_to_multiple: _Optional[int] = None,
        convolution_kernel_size: _Union[int, _Tuple[int, int]],
        convolution_stride: _Union[int, _Tuple[int, int]] = 1,
        convolution_padding: _Union[str, int, _Tuple[int, int]] = 0,
        convolution_bias: bool = False,
        activation: _activation.ActivationSpecType = "relu",
        norm: str = "rms_norm",
        norm_bias: bool = False,
        norm_eps: float = 1e-5,
        pooler_kernel_size: _Union[int, _Tuple[int, int]],
        pooler_stride: _Union[int, _Tuple[int, int]] = 1,
    ):
        """
        Creates a builder for a :obj:`.ConvPooler`.

        Args:
            input_dim (:obj:`int`): The number of features in the inputs.
            output_dim (:obj:`int`): The number of features in the outputs.  If ``None``, defaults to ``input_dim``.
            pad_to_multiple (:obj:`int`, optional): An integer padding amount.  If specified, the layer pads
                the inputs (using top-left zero padding) so that the height and width are divisible by this value.
                This can be useful when the pooler has a nonzero stride.
            convolution_kernel_size (:obj:`Union[int, Tuple[int, int]]`): The kernel size of the convolution.
            convolution_stride (:obj:`Union[int, Tuple[int, int]]`): The stride of the convolution.  Defaults to
                ``1``.
            convolution_padding (:obj:`Union[str, int, Tuple[int, int]]`): The padding of the convolution.
                Defaults to ``0``.
            convolution_bias (:obj:`bool`, optional): Whether to include a bias term in the convolution layer.
                Defaults to ``False``.
            activation (:obj:`str`, optional): The activation type.  Defaults to ``"relu"``.
            norm (:obj:`str`, optional): The normalization type.  Defaults to ``"rms_norm"``.
            norm_bias (:obj:`bool`, optional): Whether to include a bias term in the normalization layer.  Defaults
                to ``False``.
            norm_eps (:obj:`float`, optional): The norm epsilon value.  Defaults to ``1e-5``.
            pooler_kernel_size (:obj:`Union[int, Tuple[int, int]]`): The kernel size of the average pooling layer.
            pooler_stride (:obj:`Union[int, Tuple[int, int]]`): The stride of the average pooling layer.  Defaults
                to ``1``.

        Returns:
            The configured :obj:`.LayerBuilder`.
        """
        if output_dim is None:
            output_dim = input_dim

        result = cls.Builder()

        result.to_channels_first = _basic.ChannelsLastToFirst.Builder()
        if pad_to_multiple:
            result.padding = _basic.PadToMultiple.Builder(
                multiple=pad_to_multiple, dim=(-2, -1)
            )
        result.convolution = _convolution.Conv2d.Builder(
            input_dim,
            output_dim,
            kernel_size=convolution_kernel_size,
            stride=convolution_stride,
            padding=convolution_padding,
            bias=convolution_bias,
        )
        if norm is not None:
            result.norm = _norm.create_norm_builder(
                (output_dim,), norm, dim=1, bias=norm_bias, eps=norm_eps
            )
        result.activation = _activation.create_activation_layer(activation)
        result.pooler = _torch_nn.AvgPool2d.Builder(
            kernel_size=pooler_kernel_size, stride=pooler_stride
        )
        result.to_channels_last = _basic.ChannelsFirstToLast.Builder(
            flatten_spatial_dims=True
        )

        return result
