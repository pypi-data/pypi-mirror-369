from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional

import torch as _torch

from tamm.layers import functional as _tamm_F
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.transformer import kv_cache as _kv_cache
from tamm.layers.transformer.token_metadata import common as _common
from tamm.typing import OptionalTensor as _OptionalTensor


class VanillaTokenMetadataLogic(_common.TokenMetadataLogic, _LayerMixin):
    """
    This :class:`TokenMetadataLogic` subclass defines the default positions
    as the number of times a token's segment ID has previously occurred in
    ``segment_ids``.  The layer also reads and writes segment ids from the
    ``kv_cache``.
    """

    def _from_q_values(
        self,
        segment_ids: _OptionalTensor = None,
        default_segment_ids: _OptionalTensor = None,
        positions: _OptionalTensor = None,
        token_types: _OptionalTensor = None,
        aux_metadata: _Optional[_Dict[str, _Any]] = None,
    ) -> _common.TokenMetadata:
        """
        Factory method for creating segments and positions without a KV cache.  In this
        case q and kv tensors have the same length.  If positions is None, this defaults
        to 0, 1, 2, ... for each segment of each sequence.
        """
        if positions is None:
            if segment_ids is None:
                batch_size, q_length = default_segment_ids.shape
                positions = _torch.arange(
                    q_length, device=default_segment_ids.device, dtype=_torch.int64
                )
                positions = _tamm_F.expand_dim(
                    positions, batch_size, dim=0, unsqueeze=True
                )
            else:
                positions = self._compute_default_q_positions(
                    q_segment_ids=segment_ids, kv_segment_ids=segment_ids
                )
        if segment_ids is None:
            segment_ids = default_segment_ids
        return _common.TokenMetadata(
            q_segment_ids=segment_ids,
            kv_segment_ids=segment_ids,
            q_positions=positions,
            kv_positions=positions,
            q_token_types=token_types,
            kv_token_types=token_types,
            aux_metadata=aux_metadata,
        )

    def _from_kv_cache(
        self,
        kv_cache: _Optional[_kv_cache.BaseKVCacheView],
        *,
        segment_ids: _OptionalTensor = None,
        default_segment_ids: _OptionalTensor = None,
        positions: _OptionalTensor = None,
        token_types: _OptionalTensor = None,
        aux_metadata: _Optional[_Dict[str, _Any]] = None,
    ) -> _common.TokenMetadata:
        """
        Factory method for creating segments and positions with a KV cache.  In this
        case kv tensors may have a longer length than k tensors.
        """
        if segment_ids is None:
            segment_ids = default_segment_ids

        q_length = segment_ids.size(-1)

        kv_cache.write_segment_ids_to_tail(segment_ids)
        kv_segment_ids = kv_cache.read_segment_ids()

        if positions is None:
            positions = self._compute_default_q_positions(
                q_segment_ids=segment_ids, kv_segment_ids=kv_segment_ids
            )
        kv_cache.write_positions_to_tail(positions)
        kv_positions = kv_cache.read_positions()

        if token_types is not None:
            kv_cache.write_token_types_to_tail(token_types)
            kv_token_types = kv_cache.read_token_types()
            q_token_types = kv_token_types[:, -q_length:]
        else:
            q_token_types = kv_token_types = None

        return _common.TokenMetadata(
            q_segment_ids=kv_segment_ids[..., -q_length:],
            kv_segment_ids=kv_segment_ids,
            q_positions=kv_positions[..., -q_length:],
            kv_positions=kv_positions,
            q_token_types=q_token_types,
            kv_token_types=kv_token_types,
            aux_metadata=aux_metadata,
        )

    # pylint: disable=too-many-locals
    @staticmethod
    def _compute_default_q_positions(
        *, q_segment_ids: _torch.Tensor, kv_segment_ids: _torch.Tensor
    ):
        """
        Computes default positions corresponding to q_segment_ids.  The tail values of
        kv_segment_ids should be the same as q_segment_ids.  Each position value of the
        result equals the number of times the corresponding segment ID has previously
        occurred in kv_segment_ids.

        Example:

            q_segment_ids: [[2, 1, 1, 0]]
            kv_segment_ids: [[0, 0, 0, 0, 0, 1, 1, 2, 1, 1, 0]]
            result: [[0, 2, 3, 5]]
        """
        device = q_segment_ids.device

        if (
            kv_segment_ids.device.type in ("cuda", "mps")
            and kv_segment_ids.dtype is _torch.bool
        ):
            kv_segment_ids = kv_segment_ids.type(
                _torch.uint8
                # older torch versions (2.1) do not support sort with cuda and bool
            )

        sorted_kv_segment_ids, order = kv_segment_ids.sort(dim=-1, stable=True)
        sorted_indices = _torch.arange(kv_segment_ids.size(-1), device=device)

        # find indices where segment id changes in the sorted segment ids
        if device.type == "mps":
            # mps does not support cummax as of torch 2.3
            segment_id_change_idx = _torch.searchsorted(
                sorted_kv_segment_ids, sorted_kv_segment_ids, right=False
            )
        else:
            is_different_segment_id = (
                sorted_kv_segment_ids != sorted_kv_segment_ids.roll(shifts=1, dims=-1)
            )
            segment_id_change_idx = sorted_indices * is_different_segment_id
            segment_id_change_idx, _ = segment_id_change_idx.cummax(dim=-1)

        # subtract the change index from sorted positions to make sure each segment id group begins from 0
        positions_sorted = sorted_indices - segment_id_change_idx
        result = positions_sorted.scatter(-1, order, positions_sorted)
        return result[..., -q_segment_ids.size(-1) :]
