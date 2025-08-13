"""
layers.convolution
^^^^^^^^^^^^^^^^^^

This module implements convolution-related layer building blocks.

.. autoclass:: tamm.layers.Conv2d

.. autoclass:: tamm.layers.Conv1d

.. autoclass:: tamm.layers.CausalConv1d

.. autofunction:: tamm.layers.convolution.compute_convolution_output_dims

.. autoclass:: tamm.layers.ResNetBlock
    :members:

.. autoclass:: tamm.layers.ResNetStage
    :members:

.. autoclass:: tamm.layers.SqueezeExcitation
    :members:
"""

import math as _math
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch

from tamm.layers import activation as _activation
from tamm.layers import basic as _basic
from tamm.layers import common as _layers_common
from tamm.layers import norm as _norm
from tamm.layers import residual as _residual
from tamm.layers import sequential as _sequential
from tamm.layers.common import ConfigurableLayerMixin as _ConfigurableLayerMixin
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalDeviceOrString as _OptionalDeviceOrString
from tamm.typing import OptionalDtypeOrString as _OptionalDtypeOrString
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class _ConvMixin:
    """
    A mixin for |tamm| Conv layers.  Ideally this class would inherit from
    :class:`torch.nn.modules.conv._ConvNd`, but since PyTorch does not expose
    this base class, we extend it "indirectly" by defining helper methods
    and then calling those helpers in :class:`.Conv1d` and other |tamm| layers.
    """

    def __init__(self, channels_dim: int = 1):
        self.channels_dim = channels_dim

    def _to_channels_first(self, x: _torch.Tensor) -> _torch.Tensor:
        if self.channels_dim != 1:
            x = x.movedim(self.channels_dim, 1)
        return x

    def _from_channels_first(self, x: _torch.Tensor) -> _torch.Tensor:
        if self.channels_dim != 1:
            x = x.movedim(1, self.channels_dim)
        return x

    def _tamm_conv_extra_repr(self: _torch.nn.Module) -> str:
        attributes = ["in_channels", "out_channels", "kernel_size", "stride", "bias"]
        if getattr(self, "channels_dim", 1) != 1:
            attributes.append("channels_dim")
        if self.padding != (0,) * len(self.padding):
            attributes.append("padding")
        if self.dilation != (1,) * len(self.dilation):
            attributes.append("dilation")
        if self.output_padding != (0,) * len(self.output_padding):
            attributes.append("output_padding")
        if self.groups != 1:
            attributes.append("groups")
        if self.padding_mode != "zeros":
            attributes.append("padding_mode")

        pieces = {
            attr: getattr(self, attr) for attr in attributes if hasattr(self, attr)
        }
        pieces["bias"] = self.bias is not None
        pieces = [f"{key}={value}" for key, value in pieces.items()]
        return ",\n".join(pieces)


class Conv2d(_torch.nn.Conv2d, _ConvMixin, _LayerMixin):
    """
    A |tamm| version of :class:`torch.nn.Conv2d`.  The differs from the ``torch``
    version in the following ways:

    1. The ``bias`` flag defaults to ``False``.
    2. A ``channels_dim`` option provides flexibility for different input layouts.
       This option defaults to ``1`` for channels-first inputs.  Set to ``-1`` for
       channels-last inputs.

    The signature is otherwise the same as :class:`torch.nn.Conv2d`.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _Union[int, _Tuple[int, int]],
        stride: _Union[int, _Tuple[int, int]] = 1,
        padding: _Union[str, int, _Tuple[int, int]] = 0,
        dilation: _Union[int, _Tuple[int, int]] = 1,
        groups: int = 1,
        bias: bool = False,
        padding_mode: str = "zeros",
        *,
        channels_dim: int = 1,
        device=None,
        dtype=None,
    ):
        super().__init__(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            groups=groups,
            bias=bias,
            padding_mode=padding_mode,
            device=device,
            dtype=dtype,
        )
        _ConvMixin.__init__(self, channels_dim=channels_dim)

    # pylint: disable-next=redefined-builtin
    def forward(self, input: _torch.Tensor) -> _torch.Tensor:
        x = self._to_channels_first(input)
        x = super().forward(x)
        return self._from_channels_first(x)

    def extra_repr(self):
        return self._tamm_conv_extra_repr()


class Conv1d(_torch.nn.Conv1d, _ConvMixin, _LayerMixin):
    """
    A |tamm| version of :class:`torch.nn.Conv1d`.  The differs from the ``torch``
    version in the following ways:

    1. The ``bias`` flag defaults to ``False``.
    2. A ``channels_dim`` option provides flexibility for different input layouts.
       This option defaults to ``1`` for channels-first inputs.  Set to ``-1`` for
       channels-last inputs.

    The signature is otherwise the same as :class:`torch.nn.Conv1d`.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _Union[int, _Tuple[int]],
        stride: _Union[int, _Tuple[int]] = 1,
        padding: _Union[str, int, _Tuple[int]] = 0,
        dilation: _Union[int, _Tuple[int]] = 1,
        groups: int = 1,
        bias: bool = False,
        padding_mode: str = "zeros",
        *,
        channels_dim: int = 1,
        device: _OptionalDeviceOrString = None,
        dtype: _OptionalDtypeOrString = None,
    ):
        super().__init__(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            groups=groups,
            bias=bias,
            padding_mode=padding_mode,
            device=device,
            dtype=dtype,
        )
        _ConvMixin.__init__(self, channels_dim=channels_dim)

    # pylint: disable-next=redefined-builtin
    def forward(self, input: _torch.Tensor) -> _torch.Tensor:
        x = self._to_channels_first(input)
        x = super().forward(x)
        return self._from_channels_first(x)

    def extra_repr(self):
        return self._tamm_conv_extra_repr()


class CausalConv1d(Conv1d):
    """
    A 1d convolution layer that is causal, meaning that the output for each
    time step depends only on the current and prior steps.  To achieve this,
    the layer pads the start of the sequence with zeros.

    The :meth:`__init__` signature is the same as that for :class:`.Conv1d`,
    except that the causal does not take padding or stride values.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _Union[int, _Tuple[int]],
        dilation: _Union[int, _Tuple[int]] = 1,
        groups: int = 1,
        bias: bool = False,
        *,
        channels_dim: int = 1,
        device: _OptionalDeviceOrString = None,
        dtype: _OptionalDtypeOrString = None,
    ):
        super().__init__(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            dilation=dilation,
            groups=groups,
            bias=bias,
            channels_dim=channels_dim,
            device=device,
            dtype=dtype,
        )

    def _pad_for_causal_conv(self, x: _torch.Tensor) -> _torch.Tensor:
        if self.padding[-1] != 0:
            raise ValueError(
                f"{self.__class__.__name__} does not support padding {self.padding} "
                "(the last value must be 0)"
            )
        if self.stride[-1] != 1:
            raise ValueError(
                f"{self.__class__.__name__} does not support stride {self.stride} "
                "(the last value must be 1)"
            )
        padding_len = self.dilation[-1] * (self.kernel_size[-1] - 1)
        return _torch.nn.functional.pad(x, (padding_len, 0))

    # pylint: disable-next=redefined-builtin
    def forward(self, input: _torch.Tensor) -> _torch.Tensor:
        x = self._to_channels_first(input)
        x = self._pad_for_causal_conv(x)
        x = _torch.nn.Conv1d.forward(self, x)
        return self._from_channels_first(x)


def compute_convolution_output_dims(
    *input_dims: int,
    kernel_size: _Tuple[int, ...],
    stride: _Tuple[int, ...] = 1,
    padding: _Tuple[int, ...] = 0,
) -> _torch.Size:
    """
    A helper function that computes the shape of a convolution's output given the shape
    of its input.

    Args:
        input_dims (:obj:`int`): One or more integers representing the convolution's
            input shape in the convolution dimensions (height and width in the case of
            a 2D conv).
        kernel_size (:obj:`tuple` of :obj:`int`): The ``kernel_size`` of the
            convolution.
        stride (:obj:`tuple` of :obj:`int`, optional): The ``stride`` of the
            convolution.  Defaults to ``1``.
        padding (:obj:`tuple` of :obj:`int`, optional): The ``padding`` of the
            convolution.  Defaults to ``0``.

    For ``kernel_size``, ``stride``, and ``padding``, the length should match the number
    of ``input_dims``.

    Returns:
        The shape of the convolution's output in the convolution dimensions.

    Raises:
        RuntimeError: If the kernel size exceeds the padded input size.
    """

    def normalize(inputs, *, length):
        try:
            return tuple(inputs)
        except TypeError:
            return (inputs,) * length

    ndim = len(input_dims)
    kernel_size = normalize(kernel_size, length=ndim)
    stride = normalize(stride, length=ndim)
    padding = normalize(padding, length=ndim)

    if len(kernel_size) != ndim:
        raise ValueError(f"kernel_size length ({len(kernel_size)}) != ndim ({ndim})")
    if len(stride) != ndim:
        raise ValueError(f"stride length ({len(stride)}) != ndim ({ndim})")
    if len(padding) != ndim:
        raise ValueError(f"padding length ({len(padding)}) != ndim ({ndim})")

    shapes = zip(input_dims, kernel_size, stride, padding)
    result = []
    for dim_i, kernel_size_i, stride_i, padding_i in shapes:
        numerator = dim_i + 2 * padding_i - kernel_size_i + 1
        if numerator <= 0:
            raise RuntimeError("Kernel size can't exceed the input size")
        output_dim = _math.ceil(numerator / stride_i)
        result.append(output_dim)
    return _torch.Size(result)


class ResNetBlock(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    A generic ResNet block.  This supports both basic block and bottleneck layers as
    well as ResNet variants such as RegNet.  The layer expects NCHW image tensor inputs.
    """

    def __init__(
        self,
        *,
        convolution_0: _ModuleOrBuilder,
        norm_0: _ModuleOrBuilder,
        activation_0: _activation.ActivationSpecType,
        convolution_1: _ModuleOrBuilder,
        norm_1: _ModuleOrBuilder,
        activation_1: _Optional[_activation.ActivationSpecType] = None,
        squeeze_excitation_1: _OptionalModuleOrBuilder = None,
        convolution_2: _OptionalModuleOrBuilder = None,
        norm_2: _OptionalModuleOrBuilder = None,
        squeeze_excitation_2: _OptionalModuleOrBuilder = None,
        residual_connection: _OptionalModuleOrBuilder = None,
    ):
        layers = {
            "convolution_0": convolution_0,
            "norm_0": norm_0,
            "activation_0": _activation.create_activation_layer(activation_0),
            "convolution_1": convolution_1,
            "norm_1": norm_1,
            "activation_1": _activation.create_activation_layer(activation_1),
            "squeeze_excitation_1": squeeze_excitation_1,
            "convolution_2": convolution_2,
            "norm_2": norm_2,
            "squeeze_excitation_2": squeeze_excitation_2,
        }
        super().__init__(layers, residual_connection=residual_connection)

    @classmethod
    def create_basic_builder(  # pylint: disable=arguments-differ
        cls,
        *,
        input_dim: int,
        hidden_dim: _Optional[int] = None,
        output_dim: _Optional[int] = None,
        kernel_size: _Union[int, _Tuple[int, int]] = 3,
        stride: _Union[int, _Tuple[int, int]] = 1,
        padding: _Union[int, _Tuple[int, int]] = 1,
        groups: int = 1,
        bias: bool = False,
        activation: str = "relu",
        norm: str = "rms_norm",
        norm_eps: float = 1e-5,
        norm_bias: bool = False,
        apply_squeeze_excitation: bool = False,
        squeeze_excitation_reduced_dim: _Optional[int] = None,
        squeeze_excitation_bias: bool = False,
        squeeze_excitation_activation: str = "glu",
    ) -> _layers_common.LayerBuilder:
        """
        Creates a builder for a `ResNet <https://arxiv.org/abs/1512.03385>`__ bottleneck
        layer.

        Args:
            input_dim (:obj:`int`): The number of input channels.
            hidden_dim (:obj:`int`, optional): The number of hidden channels.  If
                ``None``, this defaults to ``input_dim``.
            output_dim (:obj:`int`, optional): The number of output channels.  If
                ``None``, this defaults to ``input_dim``.
            kernel_size (:obj:`int` or :obj:`tuple`, optional): The ``kernel_size``
                argument for ``convolution_1``.  Defaults to ``3``.
            stride (:obj:`int`): The ``stride`` argument for ``convolution_1``.
                Defaults to ``1``.
            padding (:obj:`int` or :obj:`tuple`): The ``padding`` argument for
                ``convolution_1``.  Defaults to ``1``.
            groups (:obj:`int`): The number of groups for ``convolution_1``.  Defaults
                to ``1``.
            bias (:obj:`bool`, optional): A flag for including ``bias`` parameters in
                convolution layers.  Defaults to ``False``.
            activation (:obj:`str`, optional): The activation type.  Defaults to
                ``"relu"``.
            norm (:obj:`str`, optional): A norm "spec" argument for
                :func:.`create_norm_builder`.  Defaults to ``"rms_norm"``.
            norm_eps (:obj:`float`, optional): The epsilon value for norm layers.
                Defaults to ``1e-5``.
            norm_bias (:obj:`bool`, optional): Whether or not to use a ``bias``
                parameter in norm layers.  Defaults to ``False``.
            apply_squeeze_excitation (:obj:`bool`, optional): A flag for including
                a :class:`SqueezeExcitation` layer after ``norm_2`` when
                ``True``.  Defaults to ``False``.
            squeeze_excitation_reduced_dim (:obj:`int`, optional): The reduced dimension
                for squeeze excitation.  If ``None``, this defaults to
                ``ceil(hidden_dim / 16)``.
            squeeze_excitation_bias (:obj:`bool`, optional): The bias option for the
                squeeze-excitation layer.  Defaults to ``False``.
            squeeze_excitation_activation (:obj:`str`, optional): The gated activation
                type for the squeeze-excitation layer.  Defaults to ``"glu"``.

        Returns:
            The newly created :obj:`LayerBuilder`.
        """

        # pylint: disable=too-many-locals

        if hidden_dim is None:
            hidden_dim = input_dim
        if output_dim is None:
            output_dim = input_dim

        builder_kwargs = {}

        for idx in range(3):
            out_channels = output_dim if idx == 2 else hidden_dim

            conv = Conv2d.Builder(
                in_channels=input_dim if idx == 0 else hidden_dim,
                out_channels=out_channels,
                kernel_size=1,
                bias=bias,
            )
            if idx == 1:
                conv.kernel_size = kernel_size
                conv.stride = stride
                conv.padding = padding
                conv.groups = groups
            builder_kwargs[f"convolution_{idx}"] = conv

            norm_builder = _norm.create_norm_builder(
                (out_channels,),
                norm,
                dim=1,
                eps=norm_eps,
                bias=norm_bias,
            )
            builder_kwargs[f"norm_{idx}"] = norm_builder

            if idx != 2:
                builder_kwargs[f"activation_{idx}"] = activation

        if apply_squeeze_excitation:
            builder_kwargs["squeeze_excitation_2"] = SqueezeExcitation.create_builder(
                input_dim=hidden_dim,
                reduced_dim=squeeze_excitation_reduced_dim,
                bias=squeeze_excitation_bias,
                activation=activation,
                gated_activation=squeeze_excitation_activation,
            )

        if stride != 1 or input_dim != output_dim:
            # downsample
            shortcut_layers = {
                "convolution": Conv2d.Builder(
                    in_channels=input_dim,
                    out_channels=output_dim,
                    kernel_size=1,
                    stride=stride,
                    bias=bias,
                ),
                "norm": _norm.create_norm_builder(
                    (out_channels,),
                    norm,
                    dim=1,
                    eps=norm_eps,
                    bias=norm_bias,
                ),
            }
            shortcut = _sequential.Sequential.Builder(shortcut_layers)
        else:
            shortcut = None
        residual_connection = _residual.ShortcutAddActResidualConnection.Builder(
            shortcut=shortcut,
            activation=activation,
        )

        return cls.Builder(**builder_kwargs, residual_connection=residual_connection)


class ResNetStage(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    A sequence of :obj:`ResNetBlock` layers.

    Args:
        blocks (:obj:`list`): A list of builders for ResNet blocks.
    """

    # pylint: disable=too-many-locals

    def __init__(self, blocks: _List[_ModuleOrBuilder]):
        named_layers = {f"block_{idx}": block for idx, block in enumerate(blocks)}
        super().__init__(named_layers)

    @classmethod
    def create_basic_builder(  # pylint: disable=arguments-differ
        cls,
        *,
        input_dim: int,
        hidden_dim: _Optional[int] = None,
        output_dim: _Optional[int] = None,
        num_blocks: int = 1,
        kernel_size: _Union[int, _Tuple[int, int]] = 3,
        stride: _Union[int, _Tuple[int, int]] = 1,
        padding: _Union[int, _Tuple[int, int]] = 1,
        dim_per_group: _Optional[int] = None,
        activation: str = "relu",
        norm: str = "rms_norm",
        norm_eps: float = 1e-5,
        norm_bias: bool = False,
        bias: bool = False,
        apply_squeeze_excitation: bool = False,
        squeeze_excitation_reduced_dim: _Optional[int] = None,
        squeeze_excitation_bias: bool = False,
        squeeze_excitation_activation: str = "glu",
    ) -> _layers_common.LayerBuilder:
        """
        Creates a :obj:`.LayerBuilder` for a :obj:`.ResNetStage` with bottleneck blocks.

        Args:
            num_blocks (:obj:`int`, optional): The number of blocks in the stage.
                Defaults to ``1``.
            dim_per_group (:obj:`int`, optional): The ``input_dim`` of each block
                divided by the number of convolution groups in the block's
                ``convolution_1``.  Defaults to ``None``, in which case each block uses
                only one convolution group.

        Please see :meth:`.ResNetBlock.create_builder` for a description of the
        remaining arguments.

        Returns:
            The newly created :obj:`LayerBuilder`.
        """
        blocks = []
        for _ in range(num_blocks):
            if dim_per_group is None:
                groups = 1
            else:
                groups = input_dim // dim_per_group

            block = ResNetBlock.create_builder(
                input_dim=input_dim,
                hidden_dim=hidden_dim,
                output_dim=output_dim,
                kernel_size=kernel_size,
                stride=stride,
                padding=padding,
                groups=groups,
                activation=activation,
                norm=norm,
                norm_eps=norm_eps,
                norm_bias=norm_bias,
                bias=bias,
                apply_squeeze_excitation=apply_squeeze_excitation,
                squeeze_excitation_reduced_dim=squeeze_excitation_reduced_dim,
                squeeze_excitation_bias=squeeze_excitation_bias,
                squeeze_excitation_activation=squeeze_excitation_activation,
            )
            blocks.append(block)
            input_dim = output_dim
            stride = 1
        return cls.Builder(blocks)

    @classmethod
    def create_regnet_builder(cls, **kwargs) -> _layers_common.LayerBuilder:
        """
        Creates a builder for a `RegNet <https://arxiv.org/abs/2003.13678>`__ stage
        with bottleneck layers.  Following ``timm``, this is the same as a ResNet stage
        layer except we set ``apply_squeeze_excitation=True`` by default and the
        :class:`.SqueezeExcitation` layers lies between ``activation_1`` and
        ``convolution_2`` within each block.  The defaults for ``hidden_dim`` and
        ``squeeze_excitation_reduced_dim`` may also differ from ``timm``, so it is
        recommended to pass these values explicitly.

        Args:
            **kwargs: Keyword arguments to :meth:`.ResNetStage.create_builder`.
        """

        builder = cls.create_builder(apply_squeeze_excitation=True, **kwargs)
        for block_builder in builder.blocks:
            block_builder.squeeze_excitation_1 = block_builder.squeeze_excitation_2
            block_builder.squeeze_excitation_2 = None
        return builder


class SqueezeExcitation(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    A `Squeeze-and-Excitation <https://arxiv.org/abs/1709.01507>`__ block.  This is
    a gated activation layer with gate inputs resulting from a ``squeeze``,
    ``reduce_transform``, ``activation``, and ``expand_transform`` layer sequence.
    This layer expects NCHW image tensor inputs.
    """

    def __init__(
        self,
        *,
        gated_activation: _activation.ActivationSpecType,
        squeeze: _ModuleOrBuilder,
        reduce_transform: _ModuleOrBuilder,
        activation: _activation.ActivationSpecType,
        expand_transform: _ModuleOrBuilder,
    ):
        layers = {
            "squeeze": squeeze,
            "reduce_transform": reduce_transform,
            "activation": _activation.create_activation_layer(activation),
            "expand_transform": expand_transform,
        }
        residual_connection = _residual.GatedActivationResidualConnection(
            gated_activation
        )
        super().__init__(layers, residual_connection=residual_connection)

    @classmethod
    def create_basic_builder(  # pylint: disable=arguments-differ
        cls,
        *,
        input_dim: int,
        reduced_dim: _Optional[int] = None,
        bias: bool = False,
        activation: str = "relu",
        gated_activation: str = "glu",
    ) -> _layers_common.LayerBuilder:
        """
        Creates a builder for squeeze-and-excitation layers.

        Args:
            input_dim (:obj:`int`): The number of input channels.
            reduced_dim (:obj:`int`, optional): The reduced dimension for excitation.
                If ``None``, this defaults to ``ceil(input_dim / 16)``.
            bias (:obj:`bool`, optional): A flag for including ``bias`` parameters in
                convolution layers.  Defaults to ``False``.
            activation (:obj:`str`, optional): The activation type.  Defaults to
                ``"relu"`` for excitation.
            gated_activation (:obj:`str`, optional): The gated activation type.
                Defaults to ``"glu"``.

        Returns:
            The newly created :obj:`LayerBuilder`.
        """

        if reduced_dim is None:
            reduced_dim = _math.ceil(input_dim / 16)
        conv_kwargs = {"kernel_size": 1, "bias": bias}

        reduce_transform = Conv2d.Builder(
            in_channels=input_dim, out_channels=reduced_dim, **conv_kwargs
        )
        expand_transform = Conv2d.Builder(
            in_channels=reduced_dim, out_channels=input_dim, **conv_kwargs
        )

        return cls.Builder(
            squeeze=_basic.Mean.Builder(dim=(2, 3), keepdim=True),
            reduce_transform=reduce_transform,
            activation=activation,
            expand_transform=expand_transform,
            gated_activation=gated_activation,
        )
