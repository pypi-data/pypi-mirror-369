"""
This module provides classes that help with decoding, such as a KVCache handler
"""

import logging as _logging
from typing import Optional as _Optional
from typing import Tuple as _Tuple

import torch as _torch
import torch.nn as _nn

from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.transformer import kv_cache as _kv_cache

_logger = _logging.getLogger(__name__)


class KVCacher(_nn.Module, _LayerMixin):
    """
    Reads from and updates a KV cache.

    The KVCache is expected to be a tensor with shape 2 x batch x S x dim,
    where S is > than the sequence dimension of query/key/value.

    The values in the new key and value tensors are stored in the tail of the
    cache, then the full cache is returned.
    """

    def __init__(self):
        super().__init__()

    def forward(
        self,
        query: _torch.Tensor,
        key: _torch.Tensor,
        value: _torch.Tensor,
        kv_cache: _Optional[_kv_cache.KVCacheLayerView] = None,
    ) -> _Tuple[_torch.Tensor, _torch.Tensor, _torch.Tensor]:
        """If kv_cache is not None, write key and value to the tail of the cache,
        and return the full cache for key and value.

        Args:
            query (:obj:`torch.Tensor`): batch x L x dim
            key (:obj:`torch.Tensor`): batch x L x dim
            value (:obj:`torch.Tensor`): batch x L x dim
            kv_cache (:obj: `Optional[torch.Tensor]`): 2 x batch x S x dim, where S >= L

        Returns:
            if kv_cache is none, Tuple of 3 tensors all batch x L x dim
            else Tuple of tensors [batch x L x dim, batch x S x dim, batch x S x dim]

        """
        if kv_cache is not None:
            kv_cache.write_to_tail(key, value)
            return query, *kv_cache.read()
        return query, key, value
