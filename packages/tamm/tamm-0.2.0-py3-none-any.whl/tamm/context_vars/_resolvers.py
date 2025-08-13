from typing import Optional, Union

import torch as _torch

from tamm.context_vars._freeze_params import get_default_freeze_params_flag
from tamm.context_vars._pretrained import get_default_pretrained_flag
from tamm.utils._torch_compatibility import _get_default_device
from tamm.utils.optional_bool import OptionalBool


def resolve_pretrained_flag(pretrained_hint=OptionalBool.NOTSET) -> "OptionalBool":
    """
    Determine ``pretrained`` flag based on the environment.
    """
    pretrained_hint = OptionalBool(pretrained_hint)
    if pretrained_hint != OptionalBool.NOTSET:
        return pretrained_hint
    return get_default_pretrained_flag()


def resolve_freeze_params(hint=OptionalBool.NOTSET) -> "OptionalBool":
    """
    Determine ``freeze_params`` flag based on the environment.
    """
    hint = OptionalBool(hint)
    if hint != OptionalBool.NOTSET:
        return hint
    return get_default_freeze_params_flag()


def resolve_device(
    device_hint: Optional[Union[str, "_torch.device"]] = None
) -> _torch.device:
    """
    Determine an explicit ``torch.device`` based on the environment.

    Args:
        device_hint: an explicit device hint

    Returns: torch.device

    """
    if isinstance(device_hint, str):
        device_hint = _torch.device(device_hint)

    if device_hint is not None:
        return device_hint
    return _get_default_device()
