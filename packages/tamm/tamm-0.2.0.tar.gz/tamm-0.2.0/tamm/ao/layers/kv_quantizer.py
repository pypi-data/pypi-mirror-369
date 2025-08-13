from typing import Tuple as _Tuple

import torch as _torch
import torch.ao.quantization as _torchq
import torch.nn as _nn


class KVQuantizer(_nn.Module):
    """
    A layer for simulating the affect of KV cache quantization.

    Args:
        key_quantizer (:obj:`~.ao.layers.FakeQuantize`): A layer for quantizing
            attention keys.
        value_quantizer (:obj:`~.ao.layers.FakeQuantize`): A layer for quantizing
            attention values.
    """

    def __init__(
        self,
        *,
        key_quantizer: _torchq.FakeQuantizeBase,
        value_quantizer: _torchq.FakeQuantizeBase,
    ):
        super().__init__()
        self.key_quantizer = key_quantizer
        self.value_quantizer = value_quantizer

    def forward(
        self,
        query: _torch.Tensor,
        key: _torch.Tensor,
        value: _torch.Tensor,
    ) -> _Tuple[_torch.Tensor, _torch.Tensor, _torch.Tensor]:
        """
        Applies quantization to keys and values.

        Args:
            query: Queries for multi-headed attention (MHA).
            key: Keys for MHA.
            value: Values for MHA.

        Returns:
            A tuple ``(query, quantized_key, quantized_value)``, where ``quantized_key``
            and ``quantized_value`` are the result of calling ``key_quantizer`` and
            ``value_quantizer`` with the keys and values.
        """
        key = self.key_quantizer(key)
        value = self.value_quantizer(value)
        return query, key, value
