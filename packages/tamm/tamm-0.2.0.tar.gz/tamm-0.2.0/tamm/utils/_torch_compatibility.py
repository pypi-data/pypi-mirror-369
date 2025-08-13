"""
Compatibility helpers to support older versions of Pytorch
"""
import logging as _logging
from typing import Optional, Union

import torch as _torch

_logger = _logging.getLogger(__name__)


def _get_default_device() -> _torch.device:
    """
    This API resolves both
    1) PyTorch default device (`torch.get_default_device()`) and
    2) device context (i.e., `with torch.device(...)`)
    """

    return _torch.tensor([]).device


def _is_same_device_type(
    device1: Optional[Union[str, "_torch.device"]],
    device2: Optional[Union[str, "_torch.device"]],
) -> bool:
    """
    equality checks with a torch.device are a little confusing because they also have an
    index which can sometimes falsify the equality check unexpectedly.
    Whenever we want to condition on the device type, use the .type attribute
    (such as device.type == "meta")
    """
    if isinstance(device1, str):
        device1 = _torch.device(device1)
    if isinstance(device2, str):
        device2 = _torch.device(device2)
    return device1.type == device2.type


def _pytree_average(*trees, weights=None):
    from torch.utils import _pytree  # pylint: disable=import-outside-toplevel

    if len(trees) == 0:
        raise ValueError("pytree_average requires at least one tree")

    if weights is not None:
        if len(weights) != len(trees):
            raise ValueError(
                "pytree_average received a different number of weights than trees"
            )
        scale = len(weights) / sum(weights)
        weights = [x * scale for x in weights]

    flattened_trees = [_pytree.tree_flatten(tree) for tree in trees]
    leaves_list, specs_list = zip(*flattened_trees)

    result_leaves = leaves_list[0].copy()

    if not all(len(leaves) == len(result_leaves) for leaves in leaves_list):
        raise ValueError(
            "pytree_average received trees with differing numbers of leaves"
        )

    for idx, leaf in enumerate(result_leaves):
        if not _torch.is_tensor(leaf) or not leaf.is_floating_point():
            continue
        idx_group = [leaves[idx] for leaves in leaves_list]
        if weights is not None:
            idx_group = [weight * x for weight, x in zip(weights, idx_group)]
        stack = _torch.stack(idx_group)
        result_leaves[idx] = stack.mean(dim=0)

    result_spec = specs_list[0]
    return _pytree.tree_unflatten(result_leaves, result_spec)


def get_autocast_dtype(device_type: str) -> _torch.dtype:
    """
    Equivalent to torch.get_autocast_dtype as of torch 2.4, with fallback for
    older torch versions.
    """
    if hasattr(_torch, "get_autocast_dtype"):  # introduced in torch 2.4
        return _torch.get_autocast_dtype(device_type)

    if _torch.cuda.is_available() and device_type == "cuda":
        return _torch.get_autocast_gpu_dtype()
    if device_type == "cpu" and _torch.is_autocast_cpu_enabled():
        return _torch.get_autocast_cpu_dtype()
    return _torch.float16


def is_autocast_enabled(device_type: str) -> bool:
    """
    Equivalent to torch.is_autocast_enabled as of torch 2.4, with fallback for
    older torch versions.
    """
    from tamm._helpers import (  # pylint: disable=import-outside-toplevel
        is_torch_base_version_less_than,
    )

    # pylint: disable=too-many-function-args
    if device_type == "mps" and is_torch_base_version_less_than("2.5"):
        return False  # mps is not supported as of torch 2.4
    if hasattr(_torch, "get_autocast_dtype"):  # introduced in torch 2.4
        return _torch.is_autocast_enabled(device_type)  # device_type arg new in 2.4
    if device_type == "cpu":
        return _torch.is_autocast_cpu_enabled()
    return _torch.is_autocast_enabled()


def rms_norm(tensor, normalized_shape, weight=None, eps=None):
    if hasattr(_torch.nn.functional, "rms_norm"):  # introduced in torch 2.4
        return _torch.nn.functional.rms_norm(
            tensor, normalized_shape=normalized_shape, weight=weight, eps=eps
        )

    mean_dims = tuple(range(-len(normalized_shape), 0))
    second_moment = tensor.square().mean(dim=mean_dims, keepdim=True)
    if eps is not None:
        second_moment = second_moment + eps
    inv_norm = _torch.rsqrt(second_moment)
    if weight is None:
        return tensor * inv_norm
    return tensor * inv_norm * weight
