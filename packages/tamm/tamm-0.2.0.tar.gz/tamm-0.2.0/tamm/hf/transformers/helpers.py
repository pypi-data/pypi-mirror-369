from typing import TYPE_CHECKING, Optional, Tuple, Union

import torch

if TYPE_CHECKING:
    import transformers


def is_cache_empty(
    cache: Optional[Union["transformers.Cache", Tuple[Tuple[torch.Tensor]]]]
) -> bool:
    """Checks if a KV cache (past_key_values) is empty.

    Determines whether the provided cache is empty by checking if it's None,
    has zero sequence length (for transformers.Cache objects), or has zero length
    (for tuple-based caches).

    Args:
        cache: The cache to check. Can be a transformers.Cache object,
              a tuple of tuples containing tensors, or None.

    Returns:
        bool: True if the cache is empty or None, False otherwise.
    """
    if cache is None:
        return True

    try:
        return cache.get_seq_length() == 0
    except AttributeError:
        pass

    return len(cache) == 0
