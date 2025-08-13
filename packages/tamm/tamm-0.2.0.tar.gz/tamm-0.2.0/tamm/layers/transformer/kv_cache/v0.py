from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch

from tamm.layers.transformer.kv_cache import common as _common


class V0KVCache(_common.BaseKVCache):
    """
    A :class:`KVCache` that is backward compatible with early versions of |tamm|.
    """

    def __init__(
        self,
        layers: int,
        batch: int,
        init_seq: int,
        dim: int,
        offsets: _Union[_List[int], _torch.Tensor],
        device=None,
        dtype=None,
    ):
        self.cache = _torch.empty(
            layers, 2, batch, init_seq, dim, device=device, dtype=dtype
        )
        if not isinstance(offsets, _torch.Tensor):
            offsets = _torch.tensor(offsets, device=device, dtype=_torch.int32)

        self.offsets = offsets

    @property
    def length(self) -> int:
        return self.cache.size(3)

    def up_to_index(self, index: int) -> "V0KVCacheView":
        return V0KVCacheView(cache=self.cache[:, :, :, :index], offsets=self.offsets)

    def resize(self, new_length: int = None, *, new_seq: int = None):
        if new_seq is None:
            new_seq = new_length

        layers, two, batch, old_seq, dim = self.cache.shape
        new_cache = _torch.empty(
            layers,
            two,
            batch,
            new_seq,
            dim,
            device=self.cache.device,
            dtype=self.cache.dtype,
        )
        new_cache[:, :, :, :old_seq, :] = self.cache
        self.cache = new_cache

    def to(self, *args, **kwargs):  # pylint: disable=invalid-name
        self.cache = self.cache.to(*args, **kwargs)
        self.offsets = self.offsets.to(device=self.cache.device)
        return self


class V0KVCacheView(_common.BaseKVCacheView):
    """
    A :class:`BaseKVCacheView` that is backward compatible with early versions of
    |tamm|.  This cache requires the user to specify the amount of left padding for
    each sequence using the :attr:`offsets` tensor.

    Args:
        cache (:obj: `torch.Tensor): A tensor with shape layers x 2 x batch x seq x dim
        offsets (:obj: `torch.Tensor): An integer tensor with shape batch
    """

    def __init__(self, cache, offsets):
        self.cache = cache
        self.offsets = offsets

    @property
    def length(self) -> int:
        return self.cache.size(3)

    @property
    def num_layers(self) -> int:
        return self.cache.size(0)

    @property
    def dtype(self) -> _torch.dtype:
        return self.cache.dtype

    @property
    def device(self) -> _torch.device:
        return self.cache.device

    def at_layer(
        self, layer_idx: _Optional[int] = None, *, layer: _Optional[int] = None
    ) -> _common.KVCacheLayerView:
        if layer is None:
            layer = layer_idx
        return super().at_layer(layer)

    def write_to_tail(
        self, key: _torch.Tensor, value: _torch.Tensor, *, layer_idx: int
    ) -> None:
        self.cache[layer_idx, 0, :, -key.size(1) :, :] = key
        self.cache[layer_idx, 1, :, -value.size(1) :, :] = value

    def write_to_tail_vectorized(
        self, keys: _torch.Tensor, values: _torch.Tensor, *, layer_indices: _List[int]
    ) -> None:
        # Vectorized implementation of write_to_tail
        keys = keys.transpose(0, 1)
        values = values.transpose(0, 1)

        if len(layer_indices) != keys.shape[0] or len(layer_indices) != values.shape[0]:
            raise ValueError("Mismatched V0KVCacheLayersView vectorize dimension")

        # Vectorized write
        self.cache[layer_indices, 0, :, -keys.size(2) :, :] = keys.reshape(
            (len(layer_indices), keys.size(1), keys.size(2), keys.size(3))
        )
        self.cache[layer_indices, 1, :, -values.size(2) :, :] = values.reshape(
            (len(layer_indices), keys.size(1), values.size(2), values.size(3))
        )

    def write_segment_ids_to_tail(self, segment_ids: _torch.Tensor) -> None:
        pass

    def write_positions_to_tail(self, positions: _torch.Tensor) -> None:
        pass

    def read(self, layer_idx: int) -> _Tuple[_torch.Tensor, _torch.Tensor]:
        return self.cache[layer_idx, 0], self.cache[layer_idx, 1]

    def read_vectorized(
        self, layer_indices: _List[int]
    ) -> _Tuple[_torch.Tensor, _torch.Tensor]:
        # Vectorized implementation of read_multi
        qs = self.cache[layer_indices, 0]
        vs = self.cache[layer_indices, 1]

        # Swap axes -> ( batch, track, ...)
        qs = qs.transpose(0, 1)
        vs = vs.transpose(0, 1)

        return qs, vs

    def read_segment_ids(self) -> _torch.Tensor:
        kv_positions = _torch.arange(self.length, device=self.device)
        return self.offsets[:, None] <= kv_positions[None, :]

    def read_positions(self) -> _torch.Tensor:
        kv_positions = _torch.arange(self.length, device=self.device)

        batch_size = self.cache.size(2)
        kv_positions = kv_positions[None, :].tile(batch_size, 1)

        return _torch.where(
            kv_positions < self.offsets[..., None],
            kv_positions,
            kv_positions - self.offsets[..., None],
            # For each sequence, the first offsets[idx] tokens are padding, so we
            # subtract this value to ensure that the non-padding positions start form 0.
            # We treat the paddings like another segment with positions 0, 1, 2, ...
        )
