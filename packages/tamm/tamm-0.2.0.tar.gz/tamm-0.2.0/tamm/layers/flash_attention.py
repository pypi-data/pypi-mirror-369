"""
layers.flash_attention
^^^^^^^^^^^^^^^^^^^^^^

This submodule contains helper functions for using
`FlashAttention <https://github.com/Dao-AILab/flash-attention>`__ with |tamm| layers.

.. autoclass:: tamm.layers.flash_attention.FlashAttentionMode
    :members:

.. autofunction:: tamm.layers.flash_attention.compute_flash_attention_options
"""

import enum as _enum
import warnings as _warnings
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Tuple as _Tuple

import torch as _torch
from packaging.version import parse

from tamm import _helpers
from tamm._helpers import case_insensitive_lookup
from tamm.runtime_configuration import rc as _rc

# This is to allow full-graph compilation
_IS_FLASH_ATTENTION_INITIALIZED = False
_IS_FLASH_ATTENTION_AVAILABLE = False

# torch.exp(torch.tensor(-1e4, device="cuda", dtype=torch.float16)) -> 0
# torch.exp(torch.tensor(-1e4, device="cuda", dtype=torch.bfloat16)) -> 0
# torch.exp(torch.tensor(-1e4, device="cuda", dtype=torch.float32)) -> 0
SMALL_NEGATIVE_VALUE = -1e4

FLASH_SUPPORTED_DTYPES = (_torch.float16, _torch.bfloat16)


def is_flash_attention_available() -> bool:
    # pylint:disable=global-statement
    global _IS_FLASH_ATTENTION_INITIALIZED
    global _IS_FLASH_ATTENTION_AVAILABLE

    if not _IS_FLASH_ATTENTION_INITIALIZED:
        _IS_FLASH_ATTENTION_INITIALIZED = True

        # Don't even try if hardware or CUDA do not support it
        if (
            # if we are not running on GPUs
            not _torch.cuda.is_available()
            # or GPU is too old
            or _torch.cuda.get_device_capability()[0] < 8
            # or CUDA is too old
            or (
                _torch.version.cuda is not None
                and parse(_torch.version.cuda) <= parse("11.6")
            )
        ):
            return False

        try:
            # pylint:disable=import-outside-toplevel,unused-import
            import flash_attn  # noqa=F401

            # Need >= 2.4.0 for ALiBi support
            flash_version = parse(flash_attn.__version__)
            if flash_version < parse("2.4.0"):
                _warnings.warn(
                    "Flash attention version is too old,"
                    f" expecting >= 2.4.0, got {flash_version}"
                )
            else:
                _IS_FLASH_ATTENTION_AVAILABLE = True

        except ModuleNotFoundError as e:
            _helpers.log_exception(e, "importing flash_attn")
            _warnings.warn(
                "Failed to import flash-attn for Flash attention. Using "
                "flash attention may lead to significantly faster training. "
                "Please refer to tamm-scripts/install_flash_attn.sh for instructions."
            )

    return _IS_FLASH_ATTENTION_AVAILABLE


_MAX_NUM_SEGMENTS = int(_rc.flash_attn_max_num_segments)
if _MAX_NUM_SEGMENTS % 8 != 0:
    raise ValueError(
        "`TAMM_FLASH_ATTN_MAX_NUM_SEGMENTS` has to be a multiple of 8,"
        f" got {_MAX_NUM_SEGMENTS}"
    )


def compute_flash_attention_biases(
    *,
    segment_ids: _torch.Tensor,
    kv_segment_ids: _torch.Tensor,
    biases_dtype: _torch.dtype,
) -> _Tuple[_torch.Tensor, _torch.Tensor]:
    """
    Returns low rank Q, K biases for Flash attention.
    """
    # In the following lines of code, we adopt a method to add custom
    # padding (encoded in the segment_ids) without building a high-rank bias
    # matrix and adding that to the attention score matrix.
    # We add 8 extra values in the hidden dimension of the Q, K instead.
    # We needed to add 8 instead of 1 because of flash_attn_func's constraint
    # requiring the hidden dimension to be divisible by 8. For each segment,
    # we add one value, so there can't be more than 8 segments.
    # Detail below:
    #
    # Let Q, K, V : seqlen x dim matrices.
    # Consider the following table:
    #                                              Target bias term value
    # padding row in Q,     padding col in K            -inf
    # padding row in Q,     non-padding col in K        -inf
    # non-padding row in Q, padding col in K            -inf
    # non-padding row in Q, non-padding col in K          0
    #
    # In order to make the above happen, we create biases as follows:
    # For every padding row in Q, add a 2 bias term
    # For every padding row in K, add a -inf bias term
    # For every non-padding row in Q, add a 0 bias term
    # For every non-padding row in K, add a 0 bias term
    #
    # Note that in practice, because 0 * inf = nan, we use the smallest
    # possible negative value as -smallest_value. 2 * (-smallest_value) = -inf.

    if not segment_ids.ndim == kv_segment_ids.ndim == 2:
        raise ValueError("This function only supports 2-dimensional segment ids")

    range_n = _torch.arange(
        _MAX_NUM_SEGMENTS, device=segment_ids.device, dtype=_torch.int32
    )
    mask_query = range_n[None, :] == segment_ids[:, :, None]
    mask_key = range_n[None, :] == kv_segment_ids[:, :, None]

    zero = _torch.zeros(1, dtype=biases_dtype, device=segment_ids.device)
    low_rank_mask_query = _torch.where(mask_query, 1.0, zero)
    low_rank_mask_key = _torch.where(mask_key, zero, SMALL_NEGATIVE_VALUE)

    low_rank_mask_query = low_rank_mask_query[:, :, None]  # add heads dimension
    low_rank_mask_key = low_rank_mask_key[:, :, None]

    return low_rank_mask_query, low_rank_mask_key


def _qkv_flash_attention_compatible(
    query: _torch.Tensor, key: _torch.Tensor, value: _torch.Tensor
) -> bool:
    return all(
        _.device.type == "cuda" and _.dtype in FLASH_SUPPORTED_DTYPES
        for _ in [query, key, value]
    )


def _maybe_pad_qkv(
    *,
    query: _torch.Tensor,
    key: _torch.Tensor,
    value: _torch.Tensor,
    query_bias: _torch.Tensor,
    key_bias: _torch.Tensor,
    value_padding: _torch.Tensor,
) -> _Tuple[bool, _torch.Tensor, _torch.Tensor, _torch.Tensor]:
    is_padded = False

    if query_bias is not None or key_bias is not None or value_padding is not None:
        is_padded = True

        # All paddings are in shape
        # (batch_size, seq_len, num_heads, max_num_segments)
        query_bias = query_bias.expand(*query.shape[:-1], -1)
        query = _torch.cat([query, query_bias], dim=-1)

        key_bias = key_bias.expand(*key.shape[:-1], -1)
        key = _torch.cat([key, key_bias], dim=-1)

        value_padding = value_padding.expand(*value.shape[:-1], -1)
        value = _torch.cat([value, value_padding], dim=-1)

    return is_padded, query, key, value


def _flash_attn_func(*args, **kwargs):
    # pylint:disable=import-error,import-outside-toplevel
    from flash_attn import flash_attn_func

    return flash_attn_func(*args, **kwargs)


def flash_attn_func_with_low_rank_mask(
    *,
    query: _torch.Tensor,
    key: _torch.Tensor,
    value: _torch.Tensor,
    dropout_p: _Optional[float] = 0.0,
    scale: _Optional[float] = None,
    segment_ids: _Optional[_torch.Tensor] = None,
    alibi_slopes: _Optional[_torch.Tensor] = None,
    window_size=(-1, -1),
    query_bias: _Optional[_torch.Tensor] = None,
    key_bias: _Optional[_torch.Tensor] = None,
    value_padding: _Optional[_torch.Tensor] = None,
    is_causal: bool = False,
) -> _torch.Tensor:
    if query.dtype != key.dtype != value.dtype:
        raise TypeError(
            "Flash attention requires Q, K, V to have the same dtype"
            " -- torch.float16 or torch.bfloat16."
        )

    # pylint:disable=protected-access
    if segment_ids.device.type != "mps":
        _torch._assert_async(segment_ids.max() < _MAX_NUM_SEGMENTS)

    dim_per_head = key.shape[-1]
    if scale is None:
        scale = dim_per_head**-0.5

    is_padded, query, key, value = _maybe_pad_qkv(
        query=query,
        key=key,
        value=value,
        query_bias=query_bias,
        key_bias=key_bias,
        value_padding=value_padding,
    )

    if alibi_slopes is not None:
        alibi_slopes = alibi_slopes.type(_torch.float32)  # flash requires alibi in fp32

    output = _flash_attn_func(
        q=query,
        k=key,
        v=value,
        dropout_p=dropout_p,
        softmax_scale=scale,
        window_size=window_size,
        causal=is_causal,
        alibi_slopes=alibi_slopes,
    )

    if is_padded:
        return output[..., :dim_per_head]

    return output


class FlashAttentionMode(str, _enum.Enum):
    """An :class:`Enum` for controlling the FlashAttention integration."""

    #: Let |tamm| determine the mode.
    AUTO = "AUTO"

    #: Turn off the integration with FlashAttention.
    NONE = "NONE"

    @classmethod
    def _missing_(cls, value):
        return case_insensitive_lookup(cls, value)


def compute_flash_attention_options(
    *,
    mode: FlashAttentionMode,
    segment_ids: _torch.Tensor,
    kv_segment_ids: _torch.Tensor,
    compute_dtype: _torch.dtype,
    is_causal: bool = False,
    attention_mask: _Optional[_torch.Tensor] = None,
    segment_mask: _Optional[_torch.Tensor] = None,
) -> _Dict[str, _Any]:
    # pylint: disable=unused-argument

    if not is_flash_attention_available():
        return None

    if mode is FlashAttentionMode.NONE:
        return None

    query_bias, key_bias = compute_flash_attention_biases(
        segment_ids=segment_ids,
        kv_segment_ids=kv_segment_ids,
        biases_dtype=compute_dtype,
    )

    return {
        "segment_ids": kv_segment_ids,
        "query_bias": query_bias,
        "key_bias": key_bias,
        "value_padding": _torch.zeros_like(key_bias),
        "is_causal": is_causal,
    }
