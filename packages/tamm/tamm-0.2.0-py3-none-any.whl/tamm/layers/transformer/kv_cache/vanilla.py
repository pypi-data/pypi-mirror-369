from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple

import torch as _torch

from tamm.layers.transformer.kv_cache import common as _common


class VanillaKVCache(_common.BaseKVCache):
    """
    A vanilla implementation of :class:`.BaseKVCache`, which handles basic decoding
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
        self.keys_and_values = None
        self.positions = None
        self.token_types = None
        self.segment_ids = None
        self._init_tensors(
            num_layers=num_layers,
            batch_size=batch_size,
            length=length,
            hidden_dim=hidden_dim,
            device=device,
            dtype=dtype,
        )

    def _init_tensors(self, num_layers, batch_size, length, hidden_dim, device, dtype):
        self.keys_and_values = _torch.empty(
            num_layers, 2, length, batch_size, hidden_dim, device=device, dtype=dtype
        )

        self.segment_ids = _torch.ones(
            length, batch_size, device=device, dtype=_torch.int64
        )

        positions = _torch.arange(length, device=device, dtype=_torch.int64)
        self.positions = positions.tile((batch_size, 1)).T

        self.token_types = _torch.ones_like(self.segment_ids)

    @property
    def dtype(self) -> _torch.dtype:
        """The :obj:`torch.dtype` for keys and values stored in the cache."""
        return self.keys_and_values.dtype

    @property
    def device(self) -> _torch.device:
        """The device for keys and values in the cache."""
        return self.keys_and_values.device

    @property
    def num_layers(self) -> int:
        return self.keys_and_values.size(0)

    @property
    def batch_size(self) -> int:
        """The batch size of the cache contents."""
        return self.keys_and_values.size(3)

    @property
    def length(self) -> int:
        return self.keys_and_values.size(2)

    @property
    def hidden_dim(self) -> int:
        """The dimension of the keys and values in the cache."""
        return self.keys_and_values.size(4)

    def up_to_index(self, index: int) -> "VanillaKVCacheView":
        return VanillaKVCacheView(self, length=index)

    def resize(self, new_length: int):
        num_old_to_copy = min(self.length, new_length)
        old_keys_and_values = self.keys_and_values[:, :, :num_old_to_copy]
        old_segment_ids = self.segment_ids[:num_old_to_copy]
        old_positions = self.positions[:num_old_to_copy]
        old_token_types = self.token_types[:num_old_to_copy]

        self._init_tensors(
            num_layers=self.num_layers,
            batch_size=self.batch_size,
            length=new_length,
            hidden_dim=self.hidden_dim,
            device=self.device,
            dtype=self.dtype,
        )

        self.keys_and_values[:, :, :num_old_to_copy] = old_keys_and_values
        self.segment_ids[:num_old_to_copy] = old_segment_ids
        self.positions[:num_old_to_copy] = old_positions
        self.token_types[:num_old_to_copy] = old_token_types

    def to(self, *args, **kwargs) -> "VanillaKVCache":
        self.keys_and_values = self.keys_and_values.to(*args, **kwargs)
        self.segment_ids = self.segment_ids.to(self.keys_and_values.device)
        self.positions = self.positions.to(self.keys_and_values.device)
        self.token_types = self.token_types.to(self.keys_and_values.device)
        return self


class VanillaKVCacheView(_common.BaseKVCacheView):
    """
    A vanilla implementation of :class:`._common.BaseKVCacheView`, which handles basic
    decoding scenarios.

    Args:
        cache (:obj:`.KVCache`): A KV cache.
        length (:obj:`int`): The sequence length of the cache view.
    """

    def __init__(self, cache: VanillaKVCache, *, length: int):
        self.cache = cache
        self._length = length

    @property
    def length(self) -> int:
        return self._length

    @property
    def num_layers(self):
        return self.cache.num_layers

    @property
    def batch_size(self):
        """The batch size of the cache."""
        return self.cache.batch_size

    @property
    def dtype(self) -> _torch.dtype:
        return self.cache.dtype

    @property
    def device(self) -> _torch.device:
        return self.cache.device

    def write_to_tail(
        self, key: _torch.Tensor, value: _torch.Tensor, *, layer_idx: int
    ) -> None:
        batch_size, num_new_tokens = key.shape[:2]
        self._validate_input_shapes(batch_size=batch_size, length=num_new_tokens)

        key = key.transpose(0, 1)  # swap batch and sequence dims
        value = value.transpose(0, 1)

        seq_slice = slice(self.length - num_new_tokens, self.length)

        self.cache.keys_and_values[layer_idx, 0, seq_slice] = key
        self.cache.keys_and_values[layer_idx, 1, seq_slice] = value

    def write_to_tail_vectorized(
        self, keys: _torch.Tensor, values: _torch.Tensor, *, layer_indices: _List[int]
    ) -> None:
        batch_size, num_new_tokens = keys.size(0), keys.size(2)
        self._validate_input_shapes(batch_size=batch_size, length=num_new_tokens)

        # input keys and values are in shape [batch, layers, seq, dim]
        keys = keys.permute(1, 2, 0, 3)
        values = values.permute(1, 2, 0, 3)

        if len(layer_indices) != keys.shape[0] or len(layer_indices) != values.shape[0]:
            raise ValueError("Mismatched KV Cache vectorize dimension")

        num_new_tokens = keys.size(1)
        seq_slice = slice(self.length - num_new_tokens, self.length)

        # Vectorized write
        self.cache.keys_and_values[layer_indices, 0, seq_slice] = keys
        self.cache.keys_and_values[layer_indices, 1, seq_slice] = values

    def write_segment_ids_to_tail(self, segment_ids: _torch.Tensor) -> None:
        batch_size, num_new_tokens = segment_ids.shape
        self._validate_input_shapes(batch_size=batch_size, length=num_new_tokens)

        seq_slice = slice(self.length - num_new_tokens, self.length)
        self.cache.segment_ids[seq_slice] = segment_ids.transpose(0, 1)

    def write_positions_to_tail(self, positions: _torch.Tensor) -> None:
        batch_size, num_new_tokens = positions.shape
        self._validate_input_shapes(batch_size=batch_size, length=num_new_tokens)

        seq_slice = slice(self.length - num_new_tokens, self.length)
        self.cache.positions[seq_slice] = positions.transpose(0, 1)

    def write_token_types_to_tail(self, token_types: _torch.Tensor) -> None:
        batch_size, num_new_tokens = token_types.shape
        self._validate_input_shapes(batch_size=batch_size, length=num_new_tokens)

        seq_slice = slice(self.length - num_new_tokens, self.length)
        self.cache.token_types[seq_slice] = token_types.transpose(0, 1)

    def _validate_input_shapes(
        self,
        batch_size: _Optional[int] = None,
        length: _Optional[int] = None,
    ):
        if batch_size is not None and batch_size != self.batch_size:
            raise ValueError(
                f"Input batch size ({batch_size}) differs from the KV cache"
                f"batch size ({self.batch_size})"
            )
        if length is not None and length > self.length:
            raise ValueError(
                f"Input length ({length}) exceeds the KV cache length ({self.length})"
            )

    def read(self, layer_idx: int) -> _Tuple[_torch.Tensor, _torch.Tensor]:
        keys_and_values = self.cache.keys_and_values[layer_idx, :, : self.length]
        keys_and_values = keys_and_values.transpose(1, 2)  # swap batch and seq dims
        return keys_and_values.unbind()

    def read_vectorized(
        self, layer_indices: _List[int]
    ) -> _Tuple[_torch.Tensor, _torch.Tensor]:
        ks = self.cache.keys_and_values[layer_indices, 0, : self.length]
        vs = self.cache.keys_and_values[layer_indices, 1, : self.length]

        # Swap axes -> ( batch, track, ...)
        ks = ks.permute(2, 0, 1, 3)
        vs = vs.permute(2, 0, 1, 3)

        return ks, vs

    def read_segment_ids(self) -> _torch.Tensor:
        segment_ids = self.cache.segment_ids[: self.length]
        return segment_ids.transpose(0, 1)

    def read_positions(self) -> _torch.Tensor:
        positions = self.cache.positions[: self.length]
        return positions.transpose(0, 1)

    def read_token_types(self) -> _torch.Tensor:
        token_types = self.cache.token_types[: self.length]
        return token_types.transpose(0, 1)
