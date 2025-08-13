import importlib as _importlib
from typing import Optional as _Optional

import torch

from tamm.typing import StateDictType as _StateDictType


def _validate_missing_keys(state_dict: _StateDictType, layer_subset: _Optional[set]):
    missing_keys = layer_subset - set(state_dict.keys())
    if missing_keys:
        raise ValueError(
            f"layers '{missing_keys}' are missing in the state dict "
            f"but explicitly specified for checksum computation"
        )


def state_dict_checksum(
    state_dict: _StateDictType,
    layer_subset: _Optional[frozenset] = None,
    dtype=torch.float32,
    standardize_zero=False,
) -> str:
    """
    Computes 32-bit checksum of state dict using `xxhash <http://xxhash.com>`_,
    can optionally compute on a subset of layers

    .. note::

        Enabling standardize_zero may reduce the throughput by 70%

    Args:
        state_dict (:obj:`StateDictType`): Input state dictionary to verify checksum.
        layer_subset (:obj:`set`, optional): A set specifying selected keys (layers)
            in a state dict
        dtype (:obj:`torch.dtype`): torch dtype to compute checksum in
        standardize_zero (:obj:`bool`): normalize IEEE 754 +0/-0 to +0

    Returns:
         (:obj:`str`) Hash hex digest of ``state_dict``

    """
    try:
        xxhash = _importlib.import_module("xxhash")
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError("'xxhash' is required for model checksum.") from e

    hash_alg = xxhash.xxh3_64()
    if layer_subset is not None:
        _validate_missing_keys(state_dict, layer_subset)
        state_dict = {
            layer: v for layer, v in state_dict.items() if layer in layer_subset
        }

    state_dict = dict(sorted(state_dict.items()))

    for v in state_dict.values():
        v = v.to(dtype=dtype)
        if standardize_zero:
            v[v == 0] = 0
        hash_alg.update(v.numpy(force=True).tobytes(order="C"))
    return hash_alg.hexdigest()
