from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch

from tamm.layers.transformer.kv_cache import BaseKVCacheView as _BaseKVCacheView


class HFStyleKVCacheView(_BaseKVCacheView):
    def __init__(
        self,
        past_key_values: _Tuple[_Tuple[_torch.Tensor]],
        segment_ids: _torch.Tensor,
        positions: _torch.Tensor,
    ):
        self._past_key_values = list(past_key_values)
        self._segment_ids = segment_ids
        self._positions = positions

    @classmethod
    def create_empty_cache(cls, *, num_layers, segment_ids, positions):
        past_key_values = tuple(tuple() for _ in range(num_layers))
        return cls(past_key_values, segment_ids=segment_ids, positions=positions)

    @property
    def past_key_values(self):
        return self._past_key_values

    @property
    def _is_empty(self):
        if len(self._past_key_values) == 0:
            return True
        return len(self._past_key_values[0]) == 0

    @property
    def _first_tensor(self):
        """
        Returns the first tensor in the cache.  Raises an :obj:`IndexError`
        if the cache is empty.
        """
        return self._past_key_values[0][0]

    @property
    def num_layers(self) -> int:
        return len(self._past_key_values)

    @property
    def length(self) -> int:
        if self._is_empty:
            return 0
        return self._first_tensor.size(2)

    @property
    def dtype(self) -> _Union[_torch.dtype, None]:
        if self._is_empty:
            return None
        return self._first_tensor.dtype

    @property
    def device(self) -> _torch.device:
        return self._segment_ids.device

    def write_to_tail(
        self, key: _torch.Tensor, value: _torch.Tensor, *, layer_idx: int
    ) -> None:
        past_kv = self._past_key_values[layer_idx]
        if len(past_kv) == 0:
            new_key = key
            new_value = value
        else:
            past_key, past_value = past_kv
            new_key = _torch.cat([past_key, key], dim=1)
            new_value = _torch.cat([past_value, value], dim=1)
        self._past_key_values[layer_idx] = (new_key, new_value)

    def write_segment_ids_to_tail(self, segment_ids: _torch.Tensor) -> None:
        """
        This class assumes all segment ids are defined during __init__(),
        so we ignore the segment IDs the that the tamm model passes during
        forward() (they should be redundant).
        """

    def write_positions_to_tail(self, positions: _torch.Tensor) -> None:
        """
        This class assumes all positions are defined during __init__(),
        so we ignore the positions that the tamm model passes during
        forward() (they should be redundant).
        """

    def read(self, layer_idx: int) -> _Tuple[_torch.Tensor, _torch.Tensor]:
        return self._past_key_values[layer_idx]

    def read_segment_ids(self) -> _torch.Tensor:
        return self._segment_ids

    def read_positions(self) -> _torch.Tensor:
        return self._positions
