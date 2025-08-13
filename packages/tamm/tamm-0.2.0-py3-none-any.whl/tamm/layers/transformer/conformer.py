"""
transformer.conformer
^^^^^^^^^^^^^^^^^^^^^

This module implements building blocks for conformer models.

.. autoclass:: tamm.layers.transformer.ConformerLayerConfig
    :members:
    :exclude-members: create_basic_builder

.. autoclass:: tamm.layers.transformer.ConformerConvolutionConfig
    :members:
    :exclude-members: create_basic_builder
"""

from typing import Optional as _Optional
from typing import Union as _Union

from tamm.layers import activation as _activation
from tamm.layers import common as _layers_common
from tamm.layers import convolution as _convolution
from tamm.layers import dropout as _dropout
from tamm.layers import linear as _linear
from tamm.layers import norm as _norm
from tamm.layers import residual as _residual
from tamm.layers import sequential as _sequential
from tamm.layers.common.typing import LayerBuilderOrConfig as _LayerBuilderOrConfig


class ConformerLayerConfig(_layers_common.ModuleConfig):
    """
    A :class:`.ModuleConfig` for conformer blocks (see figure 1 of the
    `conformer paper <https://arxiv.org/abs/2005.08100>`__), which are sequences of:

    * ``feed_forward_0``
    * ``attention``
    * ``convolution``
    * ``feed_forward_1``
    * ``output_norm``

    The :meth:`forward` method of conformer layers typically expects hidden states with
    shape ``(batch_size, seq_len, hidden_dim)`` as input.  It also takes an
    ``attention_side_inputs`` keyword argument that contains a dictionary of kwargs for
    the ``attention`` layer.  It outputs hidden states with the same shape as the input.
    """

    feed_forward_0: _layers_common.typing.LayerBuilderOrConfig
    """Builder or config for the first feed-forward layer."""

    attention: _layers_common.typing.LayerBuilderOrConfig
    """Builder or config for the self-attention layer."""

    convolution: _layers_common.typing.LayerBuilderOrConfig
    """Builder or config for the conformer convolution layer."""

    feed_forward_1: _layers_common.typing.LayerBuilderOrConfig
    """Builder or config for the second feed-forward layer."""

    output_norm: _layers_common.typing.LayerBuilderOrConfig
    """Builder or config for the final norm layer."""

    def create_basic_builder(self) -> _layers_common.LayerBuilder:
        layers = {
            "feed_forward_0": self.feed_forward_0,
            "attention": self.attention,
            "convolution": self.convolution,
            "feed_forward_1": self.feed_forward_1,
            "output_norm": self.output_norm,
        }
        side_input_keys = {
            "attention": [("attention_side_inputs", "**kwargs")],
        }
        layers = _layers_common.map_configs_to_builders(layers)
        return _sequential.Sequential.Builder(layers, side_input_keys=side_input_keys)


class ConformerConvolutionConfig(_layers_common.ModuleConfig):
    """
    A :class:`.ModuleConfig` for convolution layers in a conformer stack.
    Following figure 2 of the `conformer paper <https://arxiv.org/abs/2005.08100>`__,
    this class configures the following sequence of layers:

    * ``norm_0`` (defaults to layer norm)
    * ``linear_0`` (a.k.a. pointwise convolution)
    * ``activation_0`` (defaults to GLU)
    * ``convolution`` (depthwise convolution across the sequence dimension)
    * ``norm_1`` (defaults to layer norm)
    * ``activation_1`` (defaults to SiLU)
    * ``linear_1`` (a.k.a. pointwise convolution)
    * ``dropout``
    * ``residual_add`` (residual add)

    Note that in the conformer paper, ``activation_1`` defaults to batch norm,
    but here we default to layer norm (in order to discourage usage of batch norm).

    The :meth:`forward` method of conformer convolution layers expects inputs with
    shape ``(batch_size, seq_len, hidden_dim)``, and it returns outputs with the same
    shape.
    """

    input_dim: int
    """Input features dim."""

    kernel_size: int
    """Length of the convolution kernel."""

    activation_0: _Optional[str] = "glu"
    """Spec for the first activation layer."""

    activation_1: _Optional[str] = "silu"
    """Spec for the second activation layer."""

    norm_0: _Union[str, _LayerBuilderOrConfig] = "layer_norm"
    """Spec for the first norm layer."""

    norm_1: _Union[str, _LayerBuilderOrConfig] = "layer_norm"
    """Spec for the second norm layer."""

    norm_0_bias: bool = False
    """Flag for including a bias in the first norm layer."""

    norm_1_bias: bool = False
    """Flag for including a bias in the second layer."""

    linear_0_bias: bool = False
    """Flag for including a bias in the first linear layer."""

    linear_1_bias: bool = False
    """Flag for including a bias in the second linear layer."""

    convolution_bias: bool = False
    """Flag for including a bias in the convolution layer."""

    output_dropout_p: float = 0.0
    """Dropout probability for the dropout layer."""

    def create_basic_builder(self) -> _layers_common.LayerBuilder:
        layers = {
            "norm_0": _norm.create_norm_builder(
                (self.input_dim,), spec=self.norm_0, bias=self.norm_0_bias
            )
        }

        if _activation.is_activation_gated(self.activation_0):
            linear_0 = _linear.MultiOutputLinear.Builder(
                self.input_dim, 2 * [self.input_dim], bias=self.linear_0_bias
            )
        else:
            linear_0 = _linear.Linear.Builder(
                self.input_dim, self.input_dim, bias=self.linear_0_bias
            )
        layers["linear_0"] = linear_0

        layers["activation_0"] = _activation.create_activation_layer(self.activation_0)

        layers["convolution"] = _convolution.CausalConv1d.Builder(
            self.input_dim,
            self.input_dim,
            channels_dim=-1,
            kernel_size=self.kernel_size,
            groups=self.input_dim,
            bias=self.convolution_bias,
        )

        layers["norm_1"] = _norm.create_norm_builder(
            (self.input_dim,), spec=self.norm_1, bias=self.norm_1_bias
        )

        layers["activation_1"] = _activation.create_activation_layer(self.activation_1)

        layers["linear_1"] = _linear.Linear.Builder(
            self.input_dim, self.input_dim, bias=self.linear_1_bias
        )

        layers["output_dropout"] = _dropout.Dropout.Builder(p=self.output_dropout_p)

        layers = _layers_common.map_configs_to_builders(layers)

        return _sequential.Sequential.Builder(
            layers,
            residual_connection=_residual.ResidualAdd.Builder(),
            unpack_tuple_inputs=True,
        )
