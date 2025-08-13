"""
transformer.attention_mask
^^^^^^^^^^^^^^^^^^^^^^^^^^

This module implements attention mask layers.

.. autoclass:: AttentionMask
    :members: forward
"""

from typing import Any as _Any
from typing import Dict as _Dict
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

from tamm import _helpers
from tamm.layers import flash_attention as _flash
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.transformer import token_metadata as _token_metadata


class AttentionMask(_nn.Module, _LayerMixin):
    """
    A layer that maps segment IDs and positions into an attention mask for restricting
    attention between tokens.

    Args:
        is_causal (:obj:`bool`, optional):  A flag that specifies a causal mask pattern
            when ``True`` (i.e., a query token only attends to a key if the query
            position is at least as large as the key position).  If ``False``, the
            mask does not depend on the token positions.  Defaults to ``False``.
        flash_attention_mode (:obj:`str` or :obj:`.FlashAttentionMode`, optional): An
            enum for controlling the integration with FlashAttention.  Defaults to
            ``auto``.
    """

    def __init__(
        self,
        is_causal: bool = False,
        flash_attention_mode: _Union[str, _flash.FlashAttentionMode] = "auto",
    ):
        super().__init__()
        self.is_causal = is_causal

        if flash_attention_mode is None:
            flash_attention_mode = _flash.FlashAttentionMode.NONE
        self.flash_attention_mode = _helpers.get_enum_member_from_name(
            _flash.FlashAttentionMode, flash_attention_mode
        )
        _flash.is_flash_attention_available()

    def forward(
        self,
        token_metadata: _token_metadata.TokenMetadata,
        *,
        compute_dtype: _torch.dtype = _torch.float32,
    ) -> _Dict[str, _Any]:
        """
        Args:
            token_metadata (:obj:`.TokenMetadata`): The segment IDs, positions, and
                types of tokens for self attention.
            compute_dtype (:obj:`torch.dtype`, optional): The dtype for attention
                computation in the SDPA layer.  This option is only important if using
                FlashAttention.

        Returns:
            A :obj:`dict` with an ``"attention_mask"`` entry, which is a boolean tensor
            value of shape ``(batch size, seq_len, kv_seq_len)``.  A ``False`` value
            in the mask prevents corresponding tokens from attending to one another.
            The result also includes a ``"flash_attention_options"`` entry, which may
            have value ``None`` if FlashAttention is unavailable or disabled.
        """

        tm = token_metadata

        self._validate_positions(positions=tm.q_positions, kv_positions=tm.kv_positions)

        segment_mask = tm.q_segment_ids[..., None] == tm.kv_segment_ids[:, None, :]
        if self.is_causal:
            attention_mask = tm.q_positions[..., None] >= tm.kv_positions[:, None, :]
            attention_mask = _torch.logical_and(attention_mask, segment_mask)
        else:
            attention_mask = segment_mask

        # pylint: disable-next=assignment-from-none
        flash_options = _flash.compute_flash_attention_options(
            segment_ids=tm.q_segment_ids,
            kv_segment_ids=tm.kv_segment_ids,
            attention_mask=attention_mask,
            segment_mask=segment_mask,
            is_causal=self.is_causal,
            compute_dtype=compute_dtype,
            mode=self.flash_attention_mode,
        )

        return {
            "attention_mask": attention_mask,
            "flash_attention_options": flash_options,
        }

    def _validate_positions(self, *, positions, kv_positions):
        if not self.is_causal:
            return  # positions only used for causal masks
        if not _torch.is_tensor(positions):
            raise ValueError(
                "AttentionMask requires a positions tensor arg when is_causal=True"
            )
        if not _torch.is_tensor(kv_positions):
            raise ValueError(
                "AttentionMask requires a kv_positions tensor arg when is_causal=True"
            )

    def extra_repr(self) -> str:
        flash_mode = self.flash_attention_mode.name.lower()
        return f"is_causal={self.is_causal}, " f"flash_attention_mode='{flash_mode}'"
