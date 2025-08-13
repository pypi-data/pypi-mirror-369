from typing import Optional as _Optional
from typing import Tuple as _Tuple

import torch as _torch
import torch.nn as _nn

from tamm.ao.layers.kv_quantizer import KVQuantizer as _KVQuantizer
from tamm.context_vars import get_first_token_generation_flag
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.decoding import KVCacher as _KVCacher
from tamm.layers.transformer import kv_cache as _kv_cache


class QuantizingKVCacher(_nn.Module, _LayerMixin):
    """
    Enhanced KV cacher with quantization support.

    1. Quantizes the key and value before storing them in the kv_cache.
    2. For the first token only, overwrites the cached quantized values with its original
        unquantized tensors, to maintain high-precision.
    """

    def __init__(
        self,
        key_quantizer,
        value_quantizer,
        kv_cacher: _KVCacher,
        freeze_qparams: _Optional[bool] = False,
    ):
        super().__init__()
        self.kv_cacher = kv_cacher
        self.freeze_qparams = freeze_qparams
        self.quantizer = _KVQuantizer(
            key_quantizer=key_quantizer,
            value_quantizer=value_quantizer,
        )

    def forward(
        self,
        query: _torch.Tensor,
        key: _torch.Tensor,
        value: _torch.Tensor,
        kv_cache: _Optional[_kv_cache.KVCacheLayerView] = None,
    ) -> _Tuple[_torch.Tensor, _torch.Tensor, _torch.Tensor]:
        """
        Applies quantization to keys and values before storing in KV-cache, but overwrites with
            unquantized tensors for the first token only.

        Args:
            query (:obj:`torch.Tensor`): batch x L x dim
            key (:obj:`torch.Tensor`): batch x L x dim
            value (:obj:`torch.Tensor`): batch x L x dim
            kv_cache (:obj: `Optional[torch.Tensor]`): 2 x batch x S x dim, where S >= L

        Returns:
            Tuple of tensors [batch x L x dim, batch x S x dim, batch x S x dim]
        """
        query, quant_key, quant_value = self.quantizer(query, key, value)

        query, full_key, full_value = self.kv_cacher(
            query, quant_key, quant_value, kv_cache
        )

        # For first token only, overwrite with unquantized values
        if kv_cache is not None and get_first_token_generation_flag():
            full_key = self._overwrite_tail_entries(full_key, key)
            full_value = self._overwrite_tail_entries(full_value, value)

        return query, full_key, full_value

    @staticmethod
    def _overwrite_tail_entries(
        original_tensor: _torch.Tensor, new_tensor: _torch.Tensor
    ) -> _torch.Tensor:
        """
        Creates a new tensor by concatenating the head of the original tensor with the new tensor.
            Supports both regular models with shape (batch_size, seq_len, hidden_dim) and
            PTT models with shape (num_tracks, batch_size, seq_len, hidden_dim).

        Args:
            original_tensor (:obj:`_torch.Tensor`): The full cached tensor (... x seq_len x dim).
            new_tensor (:obj:`_torch.Tensor`): The new tensor to overwrite (... x new_seq_len x dim).
                Here, new_seq_len <= seq_len.

        Returns:
            :obj:`_torch.Tensor`: A new tensor combining the head of ``original_tensor``
                with ``new_tensor``, maintaining original sequence length.
        """
        if new_tensor.size(-2) > original_tensor.size(-2):
            raise ValueError(
                f"New key/ value tensor sequence length: {new_tensor.size(-2)} "
                f"exceeds original cache size: {original_tensor.size(-2)}"
            )
        tail_start = original_tensor.size(-2) - new_tensor.size(-2)
        return _torch.cat([original_tensor[..., :tail_start, :], new_tensor], dim=-2)
