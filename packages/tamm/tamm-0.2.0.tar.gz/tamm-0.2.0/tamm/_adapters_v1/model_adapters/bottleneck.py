"""
_adapters_v1.model_adapters.bottleneck
================================

.. autoclass:: tamm._adapters_v1.model_adapters.bottleneck.BottleneckModelAdapter
    :show-inheritance:
    :members:
"""

import logging as _logging
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

from tamm._adapters_v1 import layer_annotations as _layer_annotations
from tamm._adapters_v1.adapted_layer import AdaptedLayer as _AdaptedLayer
from tamm._adapters_v1.layer_adapters.bottleneck import Bottleneck as _Bottleneck
from tamm._adapters_v1.layer_adapters.bottleneck import (
    init_bias_params as _init_bias_params,
)
from tamm._adapters_v1.layer_adapters.bottleneck import (
    init_weight_params as _init_weight_params,
)
from tamm._adapters_v1.layer_adapters.common import LayerAdapter as _LayerAdapter
from tamm._adapters_v1.layer_annotations import LayerAnnotation as _LayerAnnotation
from tamm._adapters_v1.layer_annotations import LinearProjection as _LinearProjection
from tamm._adapters_v1.layer_annotations import (
    get_layer_annotations as _get_layer_annotations,
)
from tamm._adapters_v1.model_adapters.model_adapter import AdapterSpec as _AdapterSpec
from tamm._adapters_v1.model_adapters.model_adapter import ModelAdapter as _ModelAdapter
from tamm.layers import activation as _activation

_logger = _logging.getLogger(__name__)


class BottleneckModelAdapter(_ModelAdapter):
    """
    A model adapter which inserts :class:`_BottleneckLayerAdapter`.
    Two adapter variants supported are:

    * Bottleneck adapter: See Neil Houlsby, et al. (2019), Parameter-Efficient
    Transfer Learning for NLP for details. Here the adapter is attached after
    the feed-forward layer within the transformer block. More details are
    available in https://arxiv.org/pdf/1902.00751.
    * Residual adapter: See Katrin Tomanek, et al. (2021), Residual Adapters
    for Parameter-Efficient ASR Adaptation to Atypical and Accented Speech.
    Here the adapter contains layer norm added to the bottleneck layer.
    More details are available in https://arxiv.org/pdf/2109.06952.

    Args:
        input_dim: Layer input dim.
        output_dim: Layer output dim.
        hidden_dim: Layer hidden dim.
        activation: Layer activation.
        share_adapter_weights: Enable weight sharing.
        share_adapter_bias: Enable bias sharing.
        dropout_p: Dropout rate.
        layer_norm_eps: Layer norm eps.
        layer_norm_bias: Layer norm bias.
        input_normalize: Apply layer norm to inputs.
    """

    def __init__(
        self,
        hidden_dim: int = 128,
        activation: _activation.ActivationSpecType = ("relu",),
        adapt_feed_forward_hidden_states: bool = True,
        adapt_feed_forward_outputs: bool = True,
        share_adapter_weights: bool = False,
        share_adapter_bias: bool = False,
        dropout_p: float = 0,
        layer_norm_eps: float = 1e-5,
        layer_norm_bias: bool = True,
        input_normalize: bool = True,
        device: _Optional[_Union[_torch.device, str]] = None,
        dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.activation = activation
        self.adapt_feed_forward_hidden_states = adapt_feed_forward_hidden_states
        self.adapt_feed_forward_outputs = adapt_feed_forward_outputs
        self.share_adapter_weights = share_adapter_weights
        self.share_adapter_bias = share_adapter_bias
        self.dropout_p = dropout_p
        self.layer_norm_eps = layer_norm_eps
        self.layer_norm_bias = layer_norm_bias
        self.input_normalize = input_normalize
        self.device = device
        self.dtype = dtype

        # adapter shareable parameters
        self._hidden_states_a_weights: _Optional[_nn.Parameter] = None
        self._hidden_states_a_bias: _Optional[_nn.Parameter] = None
        self._hidden_states_b_weights: _Optional[_nn.Parameter] = None
        self._hidden_states_b_bias: _Optional[_nn.Parameter] = None
        self._outputs_a_weights: _Optional[_nn.Parameter] = None
        self._outputs_a_bias: _Optional[_nn.Parameter] = None
        self._outputs_b_weights: _Optional[_nn.Parameter] = None
        self._outputs_b_bias: _Optional[_nn.Parameter] = None

    def _get_bottlenck_layer_type(
        self, layer_type: _List[_LayerAnnotation]
    ) -> _Optional[_LinearProjection]:
        for lt in layer_type:
            matching_type = (
                self.adapt_feed_forward_hidden_states
                and isinstance(lt, _layer_annotations.FeedForwardHiddenTransform)
            ) or (
                self.adapt_feed_forward_outputs
                and isinstance(lt, _layer_annotations.FeedForwardOutputTransform)
            )
            if matching_type:
                return lt
        return None

    def _create_adapters_impl(self, model: _nn.Module) -> _AdapterSpec:
        layer_adapters = {}
        for name, submodule in model.named_modules(remove_duplicate=True):
            if isinstance(submodule, _AdaptedLayer):
                adapter = self._create_adapter_for_submodule(submodule)
                if adapter is not None:
                    layer_adapters[name] = adapter
        return _AdapterSpec(layer_adapters=layer_adapters)

    def _get_hidden_states_params(self, dim: int):
        if self.share_adapter_weights:
            if self._hidden_states_a_weights is None:
                self._hidden_states_a_weights = _init_weight_params(
                    self.hidden_dim, dim, device=self.device, dtype=self.dtype
                )
            if self._hidden_states_b_weights is None:
                self._hidden_states_b_weights = _init_weight_params(
                    dim, self.hidden_dim, device=self.device, dtype=self.dtype
                )

        if self.share_adapter_bias:
            if self._hidden_states_a_bias is None:
                self._hidden_states_a_bias = _init_bias_params(
                    self.hidden_dim,
                    self._hidden_states_a_weights,
                    device=self.device,
                    dtype=self.dtype,
                )
            if self._hidden_states_b_bias is None:
                self._hidden_states_b_bias = _init_bias_params(
                    dim,
                    self._hidden_states_b_weights,
                    device=self.device,
                    dtype=self.dtype,
                )

        return (
            self._hidden_states_a_weights,
            self._hidden_states_a_bias,
            self._hidden_states_b_weights,
            self._hidden_states_b_bias,
        )

    def _get_outputs_params(self, dim: int):
        if self.share_adapter_weights:
            if self._outputs_a_weights is None:
                self._outputs_a_weights = _init_weight_params(
                    self.hidden_dim, dim, device=self.device, dtype=self.dtype
                )
            if self._outputs_b_weights is None:
                self._outputs_b_weights = _init_weight_params(
                    dim, self.hidden_dim, device=self.device, dtype=self.dtype
                )

        if self.share_adapter_bias:
            if self._outputs_a_bias is None:
                self._outputs_a_bias = _init_bias_params(
                    self.hidden_dim,
                    self._outputs_a_weights,
                    device=self.device,
                    dtype=self.dtype,
                )
            if self._outputs_b_bias is None:
                self._outputs_b_bias = _init_bias_params(
                    dim, self._outputs_b_weights, device=self.device, dtype=self.dtype
                )

        return (
            self._outputs_a_weights,
            self._outputs_a_bias,
            self._outputs_b_weights,
            self._outputs_b_bias,
        )

    def _get_shared_params(self, layer_type: _LayerAnnotation, input_dim: int):
        if isinstance(layer_type, _layer_annotations.FeedForwardHiddenTransform):
            return self._get_hidden_states_params(input_dim)
        if isinstance(layer_type, _layer_annotations.FeedForwardOutputTransform):
            return self._get_outputs_params(input_dim)
        return (None, None, None, None)

    def _create_adapter_for_submodule(
        self, submodule: _nn.Module
    ) -> _Optional[_LayerAdapter]:
        wrapped_module = submodule.unwrap()
        layer_type = _get_layer_annotations(wrapped_module)
        bn_layer_type = self._get_bottlenck_layer_type(layer_type)
        if bn_layer_type:
            input_dim = getattr(wrapped_module, bn_layer_type.output_dim_field)
            a_weights, a_bias, b_weights, b_bias = self._get_shared_params(
                bn_layer_type, input_dim
            )

            return _Bottleneck(
                input_dim=input_dim,
                output_dim=input_dim,
                hidden_dim=self.hidden_dim,
                a_weights=a_weights,
                a_bias=a_bias,
                b_weights=b_weights,
                b_bias=b_bias,
                activation=_activation.create_activation_layer(self.activation),
                dropout_p=self.dropout_p,
                layer_norm_eps=self.layer_norm_eps,
                layer_norm_bias=self.layer_norm_bias,
                input_normalize=self.input_normalize,
                device=self.device,
                dtype=self.dtype,
            )
        return None
