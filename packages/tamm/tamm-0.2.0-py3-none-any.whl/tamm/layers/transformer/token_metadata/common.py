import abc as _abc
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional

import torch as _torch

from tamm.layers.transformer import kv_cache as _kv_cache
from tamm.typing import OptionalTensor as _OptionalTensor
from tamm.utils import torch_utils as _torch_utils


@_torch_utils.torch_exportable_dataclass
class TokenMetadata:
    """
    A dataclass that holds segment ids and positions for transformer tokens.  The
    tensors for keys and values may have longer sequence lengths than for
    those for queries (if using a KV cache).
    """

    q_segment_ids: _torch.Tensor = None
    """
    Segment IDs for self-attention query tokens.  Tokens only attend to each other when
    the q segment ID matches the kv segment ID.
    """

    kv_segment_ids: _torch.Tensor = None
    """Segment IDs for self-attention key and value tokens."""

    q_positions: _torch.Tensor = None
    """Positions for self-attention query tokens."""

    kv_positions: _torch.Tensor = None
    """Positions for self-attention key and value tokens."""

    q_token_types: _torch.Tensor = None
    """Types for self-attention query tokens (this can be arbitrary metadata)."""

    kv_token_types: _torch.Tensor = None
    """Types for self-attention key and value tokens."""

    aux_metadata: _Dict[str, _Any] = None
    """Auxiliary metadata for extending model behavior."""

    def __post_init__(self):
        if self.q_segment_ids is not None:
            if not _torch.is_tensor(self.q_segment_ids) or self.q_segment_ids.ndim != 2:
                raise ValueError("q_segment_ids must be a 2d tensor")
        if self.kv_segment_ids is not None:
            if (
                not _torch.is_tensor(self.kv_segment_ids)
                or self.kv_segment_ids.ndim != 2
            ):
                raise ValueError("kv_segment_ids must be a 2d tensor")
        if self.q_positions is not None:
            if not _torch.is_tensor(self.q_positions) or self.q_positions.ndim != 2:
                raise ValueError("q_positions must be a 2d tensor")
        if self.kv_positions is not None:
            if not _torch.is_tensor(self.kv_positions) or self.kv_positions.ndim != 2:
                raise ValueError("kv_positions must be a 2d tensor")

        if self.aux_metadata is None:
            self.aux_metadata = {}
        if not isinstance(self.aux_metadata, dict):
            raise ValueError("aux_metadata must be a dictionary")


class TokenMetadataLogic(_torch.nn.Module, _abc.ABC):
    """
    A base class for layers that determine the token metadata (segment ids, positions,
    token types) in a :obj:`TransformerStack`.
    """

    def __init__(self):
        super().__init__()

    def forward(
        self,
        *,
        embeddings: _torch.Tensor,
        segment_ids: _OptionalTensor = None,
        positions: _OptionalTensor = None,
        token_types: _OptionalTensor = None,
        kv_cache: _Optional[_kv_cache.BaseKVCacheView] = None,
        aux_metadata: _Optional[_Dict[str, _Any]] = None,
    ) -> TokenMetadata:
        """
        Populates a :obj:`TokenMetadata` from :class:`TransformerStack` inputs.
        The layer computes default segment IDs, positions, and token types as needed.
        It also reads cached segment ids and positions from the cache when ``kv_cache``
        is not ``None``.

        Args:
            embeddings (:obj:`torch.Tensor`): The embeddings input to the :class:`TransformerStack`.
            segment_ids (:obj:`torch.Tensor`): An integer tensor with shape
                ``(batch_size, seq_len)`` that controls the attention mask for
                self attention layers.  For sequence ``i``, if
                ``segment_ids[i, j] != segment_ids[i, k]``, then tokens ``j`` and
                ``k`` do not attend to each other.
            positions (:obj:`torch.Tensor`, optional): An optional integer tensor with
                shape ``(batch_size, seq_len)`` that specifies the position of each
                token.  Defaults to ``None``.
            token_types (:obj:`torch.Tensor`, optional): An optional integer tensor with shape
                ``(batch_size, seq_len)`` that specifies the type of each token.  Defaults to
                ``None``.
            kv_cache (:obj:`BaseKVCacheView`, optional): An optional KV cache view
                with cached keys and values, etc.
            aux_metadata (:obj:`dict`): A dictionary of optional auxiliary inputs for
                extending model behavior.

        Returns:
            The newly created :obj:`TokenMetadata`.
        """
        default_segment_ids = None
        if segment_ids is None:
            default_segment_ids = _torch.ones(
                embeddings.shape[:-1], device=embeddings.device, dtype=_torch.int64
            )

        if kv_cache is not None:
            return self._from_kv_cache(
                kv_cache=kv_cache,
                segment_ids=segment_ids,
                default_segment_ids=default_segment_ids,
                positions=positions,
                token_types=token_types,
                aux_metadata=aux_metadata,
            )

        return self._from_q_values(
            segment_ids=segment_ids,
            default_segment_ids=default_segment_ids,
            positions=positions,
            token_types=token_types,
            aux_metadata=aux_metadata,
        )

    @_abc.abstractmethod
    def _from_q_values(
        self,
        segment_ids: _OptionalTensor = None,
        default_segment_ids: _OptionalTensor = None,
        positions: _OptionalTensor = None,
        token_types: _OptionalTensor = None,
        aux_metadata: _Optional[_Dict[str, _Any]] = None,
    ) -> TokenMetadata:
        """
        Factory method for creating segments and positions without a KV cache.  In this
        case q and kv tensors have the same length.  If positions is None, this defaults
        to 0, 1, 2, ... for each segment of each sequence.
        """

    @_abc.abstractmethod
    def _from_kv_cache(
        self,
        kv_cache: _Optional[_kv_cache.BaseKVCacheView],
        *,
        segment_ids: _OptionalTensor = None,
        default_segment_ids: _OptionalTensor = None,
        positions: _OptionalTensor = None,
        token_types: _OptionalTensor = None,
        aux_metadata: _Optional[_Dict[str, _Any]] = None,
    ) -> TokenMetadata:
        """
        Factory method for creating segments and positions with a KV cache.  In this
        case kv tensors may have a longer length than k tensors.
        """
