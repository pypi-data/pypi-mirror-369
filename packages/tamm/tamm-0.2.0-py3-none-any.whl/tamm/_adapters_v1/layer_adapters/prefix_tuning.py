"""
Prefix Tuning Adapter Implementation.
Ref paper: https://arxiv.org/pdf/2101.00190.pdf.
"""

from typing import Any as _Any
from typing import Optional as _Optional
from typing import Tuple
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

from tamm._adapters_v1.layer_adapters.common import LayerAdapter as _LayerAdapter
from tamm._adapters_v1.layer_adapters.common import (
    attach_config_class as _attach_config_class,
)


class MLP(_nn.Sequential):
    """
    MLP class for adjusting prefix dimension.
    Ideally the input prefix dimension should be smaller than embedding dimension.
    Then we use this MLP to project prefix embedding to a higher dimension
    which matches the embedding dimension.
    """

    def __init__(
        self, input_dim, output_dim, hidden_dim=512, dtype=_torch.float32, device=None
    ):
        super().__init__(
            _nn.Linear(input_dim, hidden_dim, bias=True, dtype=dtype, device=device),
            _nn.Tanh(),
            _nn.Linear(hidden_dim, output_dim, bias=True, dtype=dtype, device=device),
        )
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_dim = hidden_dim

    def __repr__(self):
        return (
            f"MLP(input_dim={self.input_dim}, output_dim={self.output_dim}, "
            f"hidden_dim={self.hidden_dim})"
        )


class PrefixTuning(_nn.Module):
    """Class that generates prefix tensors for key and value."""

    def __init__(
        self,
        embedding_dim: int,
        prefix_length: int,
        prefix_dim: int = None,
        prefix_hidden_dim: int = 512,
        dropout_p: float = 0,
        device: _Optional[_Union[_torch.device, str]] = None,
        dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
    ) -> None:
        super().__init__()
        self.embedding_dim = embedding_dim
        self.prefix_length = prefix_length
        self.prefix_dim = prefix_dim if prefix_dim else embedding_dim
        self.prefix_hidden_dim = prefix_hidden_dim
        self.dropout_p = dropout_p
        self.prefix_embedding = _nn.Parameter(
            _torch.empty(
                self.prefix_length,
                self.prefix_dim,
                device=device,
                dtype=dtype,
            )
        )

        self.prefix_k_proj = MLP(
            input_dim=self.prefix_dim,
            output_dim=self.embedding_dim,
            hidden_dim=self.prefix_hidden_dim,
            device=device,
            dtype=dtype,
        )
        self.prefix_v_proj = MLP(
            input_dim=self.prefix_dim,
            output_dim=self.embedding_dim,
            hidden_dim=self.prefix_hidden_dim,
            device=device,
            dtype=dtype,
        )

    def forward(self, x: _torch.Tensor) -> Tuple[_torch.Tensor, ...]:
        predix_k = self.prefix_k_proj(self.prefix_embedding)
        predix_v = self.prefix_v_proj(self.prefix_embedding)
        return _torch.broadcast_to(predix_k, (x.shape[0], -1, -1)), _torch.broadcast_to(
            predix_v, (x.shape[0], -1, -1)
        )

    def extra_repr(self) -> str:
        return (
            f"PrefixTuning(prefix_dim={self.prefix_dim}, "
            f"embedding_dim={self.embedding_dim}, "
            f"prefix_length={self.prefix_length}, "
            f"prefix_hidden_dim={self.prefix_hidden_dim}, "
            f"dropout_p={self.dropout_p})"
        )


@_attach_config_class
class PrefixTuningAttention(_LayerAdapter):
    """PrefixTuning Adapter class which prepend prefix to key and value."""

    @property
    def prefix_length(self) -> int:
        return self._prefix_length

    @property
    def prefix_hidden_dim(self) -> int:
        return self._prefix_hidden_dim

    def __init__(
        self,
        prefix_length: int,
        embedding_dim: int,
        prefix_dim: int = None,
        prefix_hidden_dim: int = 512,
        dropout_p: float = 0,
        device: _Optional[_Union[_torch.device, str]] = None,
        dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
    ) -> None:
        super().__init__()
        self._prefix_length = prefix_length
        self._prefix_hidden_dim = prefix_hidden_dim

        self.prefix_tuning = PrefixTuning(
            embedding_dim=embedding_dim,
            prefix_length=prefix_length,
            prefix_dim=prefix_dim,
            prefix_hidden_dim=prefix_hidden_dim,
            dropout_p=dropout_p,
            device=device,
            dtype=dtype,
        )

    def _transform_inputs(self, *, args, kwargs):
        return args, kwargs

    def _transform_outputs(
        self,
        *,
        args: _Any,
        kwargs: _Any,
        transformed_args: _Any,
        transformed_kwargs: _Any,
        outputs: _torch.Tensor,
    ):
        if not len(args) == 1:
            raise ValueError(
                "Input to PrefixTuning adapter should be single torch tensor object."
            )

        prefix_k, prefix_v = self.prefix_tuning(args[0])
        k_adapted = _torch.concat([prefix_k, outputs[1]], dim=1)
        v_adapted = _torch.concat([prefix_v, outputs[2]], dim=1)
        return outputs[0], k_adapted, v_adapted


@_attach_config_class
class PrefixTuningALiBiMask(_LayerAdapter):
    """Class that generates modified ALiBi mask based on prefix_lengh."""

    def __init__(
        self,
        prefix_length: int,
    ) -> None:
        super().__init__()
        self.prefix_length = prefix_length

    def extra_repr(self) -> str:
        return f"PrefixTuningALiBiMask(prefix_length={self.prefix_length})"

    def _transform_inputs(self, *, args, kwargs):
        """
        In tamm's ALiBi implementation, segment_ids are used to compute causal mask.
        We add the segment_ids based on prefix_length to generate the correct mask.
        For detail ALiBi implementation, please refer to tamm.layers.attention_mask.py.
        """
        if len(args) != 1:
            raise ValueError(
                "Input to PrefixTuning adapter should be single torch tensor"
            )
        inputs = args[0]
        prefix_segment_ids = (
            _torch.ones(inputs.shape[0], self.prefix_length).to(device=inputs.device)
            * inputs[0, 0]
        )
        full_segment_ids = _torch.concat([prefix_segment_ids, inputs], dim=1)
        return full_segment_ids

    def _transform_outputs(
        self,
        *,
        args: _Any,
        kwargs: _Any,
        transformed_args: _Any,
        transformed_kwargs: _Any,
        outputs: _torch.Tensor,
    ):
        return outputs[:, :, self.prefix_length :].contiguous()
