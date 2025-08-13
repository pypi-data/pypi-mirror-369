r"""Bottleneck adapter module."""

# pylint: disable=not-callable, disable=protected-access

import math as _math
from typing import Any as _Any
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn
from torch.nn import functional as _F
from torch.nn import init as _torch_init

from tamm._adapters_v1.layer_adapters.common import LayerAdapter as _LayerAdapter
from tamm._adapters_v1.layer_adapters.common import (
    attach_config_class as _attach_config_class,
)
from tamm.layers import activation as _activation
from tamm.layers import dropout as _dropout
from tamm.layers import norm as _norm


def _init_weight_value(weight: _nn.Parameter):
    """Initialize the weight parameter's value."""
    _torch_init.kaiming_uniform_(weight, a=_math.sqrt(5))


def init_weight_params(
    output_dim: int,
    input_dim: int,
    device: _Optional[_Union[_torch.device, str]] = None,
    dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
):
    r"""Initialize weight parameters."""
    weight = _nn.Parameter(
        _torch.empty(output_dim, input_dim, device=device, dtype=dtype)
    )
    _init_weight_value(weight)
    return weight


def _init_bias_value(bias: _nn.Parameter, weight: _Optional[_nn.Parameter] = None):
    """Initialize the bias parameter's value."""
    if weight is not None:
        fan_in, _ = _torch_init._calculate_fan_in_and_fan_out(weight)
        bound = 1 / _math.sqrt(fan_in) if fan_in > 0 else 0
        _torch_init.uniform_(bias, -bound, bound)


def init_bias_params(
    dim: int,
    weight: _Optional[_nn.Parameter] = None,
    device: _Optional[_Union[_torch.device, str]] = None,
    dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
):
    r"""Initialize bias parameters."""
    bias = _nn.Parameter(_torch.empty(dim, device=device, dtype=dtype))
    _init_bias_value(bias, weight)
    return bias


@_attach_config_class
class Bottleneck(_LayerAdapter):
    """
    Bottleneck layer adapter.

    Args:
        input_dim: Layer input dim.
        output_dim: Layer output dim.
        hidden_dim: Layer hidden dim.
        activation: Layer activation.
        dropout_p: Dropout rate.
        layer_norm_eps: Layer norm eps.
        layer_norm_bias: Layer norm bias.
        input_normalize: Apply layer norm to inputs.
        device: Torch device type.
        dtype: Tensor dtype.
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        hidden_dim: int = 16,
        a_weights: _Optional[_nn.Module] = None,
        a_bias: _Optional[_nn.Module] = None,
        b_weights: _Optional[_nn.Module] = None,
        b_bias: _Optional[_nn.Module] = None,
        activation: _nn.Module = _activation.ReLU(),
        dropout_p: float = 0.2,
        layer_norm_eps: float = 1e-5,
        layer_norm_bias: bool = True,
        input_normalize: bool = True,
        device: _Optional[_Union[_torch.device, str]] = None,
        dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
    ):
        super().__init__()

        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_dim = hidden_dim
        self.a_weights = a_weights
        self.a_bias = a_bias
        self.b_weights = b_weights
        self.b_bias = b_bias
        self.dropout_p = dropout_p
        self.activation = activation
        self.device = device
        self.dtype = dtype

        self.dropout = _dropout.Dropout(p=self.dropout_p)
        self._init_adapter_params()

        self.input_normalize = input_normalize
        if self.input_normalize:
            self.norm = _norm.LayerNorm(
                [self.input_dim],
                eps=layer_norm_eps,
                bias=layer_norm_bias,
                device=device,
                dtype=dtype,
            )

    def _init_adapter_params(self):
        if self.a_weights is None:
            self.a_weights = init_weight_params(
                self.hidden_dim, self.input_dim, device=self.device, dtype=self.dtype
            )

        if self.a_bias is None:
            self.a_bias = init_bias_params(
                self.hidden_dim, self.a_weights, device=self.device, dtype=self.dtype
            )

        if self.b_weights is None:
            self.b_weights = init_weight_params(
                self.output_dim, self.hidden_dim, device=self.device, dtype=self.dtype
            )

        if self.b_bias is None:
            self.b_bias = init_bias_params(
                self.output_dim, self.b_weights, device=self.device, dtype=self.dtype
            )

    def reset_parameters(self):
        super().reset_parameters()
        _init_weight_value(self.a_weights)
        _init_bias_value(self.a_bias, self.a_weights)
        _init_weight_value(self.b_weights)
        _init_bias_value(self.b_bias, self.b_weights)

    def _transform_outputs(
        self,
        *,
        args: _Any,
        kwargs: _Any,
        transformed_args: _Any,
        transformed_kwargs: _Any,
        outputs: _torch.Tensor,
    ):
        residual = outputs
        if self.input_normalize:
            outputs = self.norm(outputs)
        outputs = _F.linear(outputs, self.a_weights, self.a_bias)
        outputs = self.dropout(self.activation(outputs))
        outputs = _F.linear(outputs, self.b_weights, self.b_bias)
        return outputs + residual

    def extra_repr(self) -> str:
        return (
            f"out_features={self.output_dim}, "
            f"in_features={self.input_dim}, "
            f"hidden_dim={self.hidden_dim}, "
            f"dropout_p={self.dropout_p}, "
            f"input_normalize={self.input_normalize}"
        )
