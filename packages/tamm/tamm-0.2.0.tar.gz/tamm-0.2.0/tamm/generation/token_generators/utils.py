import random as _random
from enum import Enum as _Enum
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
from torch import nn as _nn

from tamm.layers.transformer.kv_cache import BaseKVCache as _BaseKVCache
from tamm.layers.transformer.kv_cache import SpeculativeKVCache as _SpeculativeKVCache
from tamm.layers.transformer.kv_cache import V0KVCache as _V0KVCache
from tamm.layers.transformer.kv_cache import VanillaKVCache as _VanillaKVCache


def prepare_input_ids(input_ids: _torch.Tensor) -> _torch.Tensor:
    """Prepare and validate input tensor.

    Raises:
        ValueError: If input tensor has invalid dimensions.
    """
    input_ids = input_ids.clone().detach()
    if input_ids.ndim == 1:
        input_ids = input_ids.unsqueeze(0)

    if input_ids.ndim != 2:
        raise ValueError(
            f"Input IDs must be a 2D tensor (batch_size, seq_len). "
            f"Got {input_ids.ndim}D tensor."
        )

    return input_ids


def model_forward_step(
    model: _nn.Module,
    input_ids: _torch.Tensor,
    next_tokens: _Optional[_torch.Tensor],
    pad_id: _torch.Tensor,
    kv_cache: _Optional[_BaseKVCache],
    prompt_len: int,
    token_idx: _Optional[int] = 0,
) -> _torch.Tensor:
    segment_ids = input_ids.ne(pad_id)

    if kv_cache is None:
        return model(input_ids, segment_ids=segment_ids)
    if next_tokens is None:
        if isinstance(kv_cache, _V0KVCache):
            return model(
                input_ids,
                kv_cache=kv_cache.up_to_index(prompt_len),
            )
        return model(
            input_ids,
            segment_ids=segment_ids,
            kv_cache=kv_cache.up_to_index(prompt_len),
        )
    if token_idx is None:
        token_idx = 0
    return model(
        next_tokens,
        kv_cache=kv_cache.up_to_index(prompt_len + token_idx),
    )


def check_eos_endings(
    generated_tokens: _torch.Tensor, eos_token_ids: _List[_torch.Tensor]
) -> _torch.Tensor:
    # todo Do we have any EOS conditions?
    is_terminated = _torch.zeros(
        size=(generated_tokens.shape[0],),
        dtype=_torch.bool,
        device=generated_tokens.device,
    )
    for terminator in eos_token_ids:
        terminator_length = terminator.nelement()
        if generated_tokens.shape[1] >= terminator_length:
            endings = generated_tokens[..., -terminator_length:]
            is_terminated |= _torch.all(endings.eq(terminator), dim=1)
    return is_terminated


def find_eos_index(
    generated_tokens: _torch.Tensor, eos_token_ids: _List[_torch.Tensor]
) -> _torch.Tensor:
    termination_indices = _torch.full(
        size=(generated_tokens.shape[0],),
        dtype=_torch.int64,
        device=generated_tokens.device,
        fill_value=_torch.iinfo(_torch.int32).max,
    )

    for terminator in eos_token_ids:
        terminator_length = terminator.nelement()
        if generated_tokens.shape[1] >= terminator_length:
            windows = generated_tokens.unfold(
                1, terminator_length, 1
            )  # bs x seq_len - eos_len + 1 x eos_len
            matches = (windows == terminator).all(dim=2)  # bs x seq_len - eos_len + 1
            matches_any = matches.any(dim=1)
            first_occurence = matches.to(_torch.int32).argmax(dim=1)
            termination_indices[matches_any] = (
                first_occurence[matches_any] + terminator_length
            )
    return termination_indices


def process_logit(
    logits: _torch.Tensor,
    temperature: _Optional[float] = 1.0,
    top_k: _Optional[int] = None,
    top_p: _Optional[float] = None,
) -> _Tuple[_torch.Tensor, _torch.Tensor]:
    """Process raw logits from a decoder model. Applies temperature scaling, top-k and/or top-p (nucleus) sampling.

    Returns:
        :obj:`_Tuple[_torch.Tensor, _torch.Tensor]`: A tuple containing:
            - processed logits tensor
            - probability distribution vector derived from processed logits

    Raises:
        ValueError: If temperature <= 0, top_k <= 0, or top_p outside (0, 1].
    """
    # reshape to 2d matrix
    logits_shape = logits.shape
    vocab_size = logits_shape[-1]

    logits = logits.contiguous().view(-1, vocab_size)

    # Apply temperature scaling to next-token probability distribution
    if temperature is None:
        temperature = 1.0
    if temperature <= 0:
        raise ValueError(f"Invalid temperature value {temperature}, must be positive")
    logits = logits / temperature
    vocab_size = logits.size(-1)

    # Optionally select top-scoring tokens and ignore the rest
    # using top-K or top-P filtering
    if top_k is not None:
        if top_k <= 0:
            raise ValueError(f"Invalid top_k value {top_k}, must be positive")

        top_k = min(top_k, vocab_size)
        vals, indices_to_keep = _torch.topk(logits, top_k)

        # are we doing an unnecessary large allocation here?
        logits[:] = float("-inf")
        logits = logits.scatter(-1, indices_to_keep, vals)

    # skip top_p filtering if top_p = 1 because it does unnecessary
    # sorting
    probs = _torch.nn.functional.softmax(logits, dim=-1)
    if top_p is not None:
        if top_p <= 0 or top_p > 1.0:
            raise ValueError(f"Invalid top_p value {top_p}, must be between 0 and 1")

        min_tokens_to_keep = min(1, vocab_size)

        # Sort logits and compute (cumulative) probabilities
        sorted_probs, sorted_idxs = _torch.sort(probs, descending=False)
        cumulative_probs = sorted_probs.cumsum(dim=-1)

        # Remove tokens with cumulative probability exceeding threshold
        sorted_idxs_to_remove = cumulative_probs <= (1 - top_p)

        # Keep a minimum number of tokens
        sorted_idxs_to_remove[..., -min_tokens_to_keep:] = 0

        # Determine indices of unsorted tokens to keep
        idxs_to_remove = sorted_idxs_to_remove.scatter(
            -1, sorted_idxs, sorted_idxs_to_remove
        )

        # Over-write logits for tokens to filter out
        logits = logits.masked_fill(idxs_to_remove, -float("Inf"))

        # we zero-out the non-nucleus probabilities and re-normalize
        probs = probs.masked_fill(idxs_to_remove, 0.0)
        probs /= probs.sum(dim=-1, keepdim=True)

    # reshape back to 3d
    probs = probs.reshape(logits_shape)
    logits = logits.reshape(logits_shape)
    return logits, probs


class KVCacheType(_Enum):
    V0 = 1
    VANILLA = 2
    SPECULATIVE = 3


def setup_kv_cache(
    model: _nn.Module,
    batch_size: int,
    cache_len: int,
    input_ids: _torch.Tensor,
    pad_id: _Union[int, _torch.Tensor],
    cache_type: _Optional[KVCacheType] = None,
    cache_dtype: _Optional[_torch.dtype] = None,
) -> _Optional[_BaseKVCache]:
    """Setup KV cache for the model.

    Args:
        model (:obj:`nn.Module`): The model instance.
        batch_size (:obj:`int`): Batch size.
        cache_len (:obj:`int`): Cache length.
        input_ids (:obj:`torch.Tensor`): Input tensor.
        pad_id (:obj:`Union[int, torch.Tensor]`): Padding token ID.
        cache_type (:obj:`Optional[KVCacheType]`): Type of KV cache.
        cache_dtype (:obj:`Optional[torch.dtype]`): Data type for cache.

    Returns:
        :obj:`Optional[BaseKVCache]`: KV cache if enabled, None otherwise.
    """
    if cache_type is None:
        return None

    num_cache_layers = model.config.num_layers * getattr(model.config, "num_tracks", 1)

    try:
        kv_dim = model.kv_dim
    except AttributeError:
        kv_dim = (
            model.config.hidden_dim
            * model.config.num_kv_heads
            // model.config.num_heads
        )

    if isinstance(pad_id, _torch.Tensor):
        assert pad_id.dim() == 1
        pad_id = int(pad_id.flatten()[0].item())

    if cache_type == KVCacheType.V0:
        return _V0KVCache(
            layers=num_cache_layers,
            dim=kv_dim,
            batch=batch_size,
            init_seq=cache_len,
            offsets=_torch.argmax((input_ids != pad_id).int(), dim=-1),
            device=input_ids.device,
            dtype=cache_dtype,
        )
    if cache_type == KVCacheType.VANILLA:
        return _VanillaKVCache(
            num_layers=num_cache_layers,
            batch_size=batch_size,
            length=cache_len,
            hidden_dim=kv_dim,
            device=input_ids.device,
            dtype=cache_dtype,
        )
    if cache_type == KVCacheType.SPECULATIVE:
        return _SpeculativeKVCache(
            num_layers=num_cache_layers,
            batch_size=batch_size,
            length=cache_len,
            hidden_dim=kv_dim,
            device=input_ids.device,
            dtype=cache_dtype,
        )
    raise ValueError(f"Unrecognized cache type {cache_type}.")


def create_random_number_generator(
    device: _Union[str, _torch.device], seed: _Optional[int] = None
):
    """
    Create :py:class:`torch.Generator` on a specified device with a specified seed.
    """
    if seed is None:
        seed = _random.randint(0, 1_000_000)
    return _torch.Generator(device=device).manual_seed(seed)


def post_process_token_ids(
    token_ids: _torch.Tensor,
    max_new_tokens: _Union[int, _List[int]],
    pad_id: _Union[int, _torch.Tensor],
) -> _torch.Tensor:
    """
    Move all padding to the end of the sequence for all sequences in the batch and
    discard all extra tokens generated beyond max_new_tokens by setting them to pad
    """
    # cast mask to int because cuda cannot sort boolean tensor
    _, indices = _torch.sort((token_ids == pad_id).to(_torch.int32), dim=1, stable=True)
    token_ids = token_ids.gather(1, indices)
    if isinstance(max_new_tokens, list):
        max_max_new_tokens = max(max_new_tokens)
        max_new_tokens = (
            _torch.Tensor(max_new_tokens).unsqueeze(1).to(token_ids.device)
        )  # r x 1
        col_idx = _torch.arange(token_ids.shape[1], device=token_ids.device).unsqueeze(
            0
        )  # 1 x c
        mask = col_idx < max_new_tokens  # r x c
        token_ids = _torch.where(mask, token_ids, pad_id * _torch.ones_like(token_ids))
        token_ids = token_ids[:, :max_max_new_tokens]
    else:
        token_ids = token_ids[:, :max_new_tokens]
    return token_ids


def pad_after_termination(
    token_ids: _torch.Tensor,
    pad_id: _Union[int, _torch.Tensor],
    eos_token_ids: _List[_torch.Tensor],
):
    """
    Convert all token_ids greater than termination index to pad_id.
    """
    termination_indices = find_eos_index(token_ids, eos_token_ids)
    col_idx = _torch.arange(token_ids.shape[1], device=token_ids.device)
    mask = col_idx >= termination_indices[:, None]
    token_ids[mask] = pad_id
    return token_ids
