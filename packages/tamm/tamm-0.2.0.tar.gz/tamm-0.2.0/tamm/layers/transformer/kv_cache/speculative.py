from typing import List as _List
from typing import Tuple as _Tuple

import torch as _torch

from tamm.layers.transformer.kv_cache.vanilla import VanillaKVCache as _VanillaKVCache
from tamm.layers.transformer.kv_cache.vanilla import (
    VanillaKVCacheView as _VanillaKVCacheView,
)


class SpeculativeKVCache(_VanillaKVCache):
    """
    An implementation of :class:`.BaseKVCache`, which handles speculative decoding
    scenarios.
    """

    def __init__(
        self,
        num_layers: int,
        batch_size: int,
        length: int,
        hidden_dim: int,
        *,
        device=None,
        dtype=None,
    ):
        super().__init__(
            num_layers, batch_size, length, hidden_dim, device=device, dtype=dtype
        )
        self.temporary_cache_view = None

    def create_temporary_cache_view(self, speculation_length: int):
        cache = _VanillaKVCache(
            self.num_layers,
            self.batch_size,
            speculation_length,
            self.hidden_dim,
            device=self.device,
            dtype=self.dtype,
        )
        self.temporary_cache_view = cache.up_to_index(speculation_length)

    def up_to_index(self, index: int) -> "SpeculativeKVCacheView":
        return SpeculativeKVCacheView(self, length=index)

    def to(self, *args, **kwargs) -> "SpeculativeKVCache":
        super().to(*args, **kwargs)
        self.temporary_cache_view.cache.to(*args, **kwargs)
        return self

    def merge(
        self, merge_length: _torch.Tensor, max_merge_length: int, previous_length: int
    ):
        if previous_length + max_merge_length > self.length:
            self.resize(self.length + self.length // 2)
        new_keys_and_values = self.temporary_cache_view.cache.keys_and_values[
            :, :, :max_merge_length
        ]

        segment_ids = self.temporary_cache_view.cache.segment_ids
        device = segment_ids.device
        # align sequences across batch dimension
        segment_ids[
            _torch.arange(segment_ids.shape[0], device=device)[:, None] >= merge_length
        ] = 0
        new_segment_ids = segment_ids[:max_merge_length]

        new_positions = self.temporary_cache_view.cache.positions[:max_merge_length]
        new_token_types = self.temporary_cache_view.cache.token_types[:max_merge_length]

        self.keys_and_values[
            :, :, previous_length : previous_length + max_merge_length
        ] = new_keys_and_values
        self.segment_ids[
            previous_length : previous_length + max_merge_length
        ] = new_segment_ids
        self.positions[
            previous_length : previous_length + max_merge_length
        ] = new_positions
        self.token_types[
            previous_length : previous_length + max_merge_length
        ] = new_token_types
        self.temporary_cache_view = None


class SpeculativeKVCacheView(_VanillaKVCacheView):
    """
    An implementation of :class:`._common.BaseKVCacheView`, which handles speculative
    decoding scenarios.

    Args:
        cache (:obj:`.SpeculativeKVCache`): A KV cache.
        length (:obj:`int`): The sequence length of the cache view.
    """

    def __init__(self, cache: SpeculativeKVCache, *, length: int):
        super().__init__(cache, length=length)
        self.cache: SpeculativeKVCache = cache

    def write_to_tail(
        self, key: _torch.Tensor, value: _torch.Tensor, *, layer_idx: int
    ) -> None:
        if self.cache.temporary_cache_view:
            self.cache.temporary_cache_view.write_to_tail(
                key, value, layer_idx=layer_idx
            )
        else:
            super().write_to_tail(key, value, layer_idx=layer_idx)

    def write_to_tail_vectorized(
        self, keys: _torch.Tensor, values: _torch.Tensor, *, layer_indices: _List[int]
    ) -> None:
        if self.cache.temporary_cache_view:
            self.cache.temporary_cache_view.write_to_tail_vectorized(
                keys, values, layer_indices=layer_indices
            )
        else:
            super().write_to_tail_vectorized(keys, values, layer_indices=layer_indices)

    def write_segment_ids_to_tail(self, segment_ids: _torch.Tensor) -> None:
        if self.cache.temporary_cache_view:
            self.cache.temporary_cache_view.write_segment_ids_to_tail(segment_ids)
        else:
            super().write_segment_ids_to_tail(segment_ids)

    def write_positions_to_tail(self, positions: _torch.Tensor) -> None:
        if self.cache.temporary_cache_view:
            self.cache.temporary_cache_view.write_positions_to_tail(positions)
        else:
            super().write_positions_to_tail(positions)

    def write_token_types_to_tail(self, token_types: _torch.Tensor) -> None:
        if self.cache.temporary_cache_view:
            self.cache.temporary_cache_view.write_token_types_to_tail(token_types)
        else:
            super().write_token_types_to_tail(token_types)

    def read(self, layer_idx: int) -> _Tuple[_torch.Tensor, _torch.Tensor]:
        if self.cache.temporary_cache_view:
            orig_keys, orig_values = super().read(layer_idx)
            temp_keys, temp_values = self.cache.temporary_cache_view.read(layer_idx)
            keys = _torch.cat([orig_keys, temp_keys], dim=1)
            values = _torch.cat([orig_values, temp_values], dim=1)
            return keys, values
        return super().read(layer_idx)

    def read_vectorized(
        self, layer_indices: _List[int]
    ) -> _Tuple[_torch.Tensor, _torch.Tensor]:
        if self.cache.temporary_cache_view:
            orig_ks, orig_vs = super().read_vectorized(layer_indices)
            temp_ks, temp_vs = self.cache.temporary_cache_view.read_vectorized(
                layer_indices
            )
            keys = _torch.cat([orig_ks, temp_ks], dim=1)
            values = _torch.cat([orig_vs, temp_vs], dim=1)
            return keys, values
        return super().read_vectorized(layer_indices)

    def read_segment_ids(self) -> _torch.Tensor:
        if self.cache.temporary_cache_view:
            orig_segment_ids = super().read_segment_ids()
            temp_segment_ids = self.cache.temporary_cache_view.read_segment_ids()
            return _torch.cat([orig_segment_ids, temp_segment_ids], dim=-1)
        return super().read_segment_ids()

    def read_positions(self) -> _torch.Tensor:
        if self.cache.temporary_cache_view:
            orig_positions = super().read_positions()
            temp_positions = self.cache.temporary_cache_view.read_positions()
            return _torch.cat([orig_positions, temp_positions], dim=-1)
        return super().read_positions()

    def read_token_types(self) -> _torch.Tensor:
        if self.cache.temporary_cache_view:
            orig_token_types = super().read_token_types()
            temp_token_types = self.cache.temporary_cache_view.read_token_types()
            return _torch.cat([orig_token_types, temp_token_types], dim=-1)
        return super().read_token_types()
