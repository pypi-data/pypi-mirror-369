import contextlib as _contextlib
from contextvars import ContextVar

import torch

from tamm.context_vars._resolvers import _get_default_device
from tamm.typing import OptionalDeviceOrString

BUILD_DEVICE_NO_META_TRICK: ContextVar[OptionalDeviceOrString] = ContextVar(
    "build_device_no_meta_trick", default=None
)


def get_model_build_device(
    disable_meta_init_trick: bool = False,
) -> OptionalDeviceOrString:
    """
    A helper function for querying the current build device when using
    :func:`model_build_device_context`.

    Args:
        disable_meta_init_trick (:obj:`bool`): A flag for ignoring parent/ancestor
            usages of :func:`model_build_device_context` with
            ``enable_meta_init_trick=True``.  If ``False``, the function behaves
            as if these meta init contexts were never entered.
    """

    if disable_meta_init_trick:
        result = BUILD_DEVICE_NO_META_TRICK.get()
        if result is not None:
            return result

    return _get_default_device()


@_contextlib.contextmanager
def model_build_device_context(
    *,
    device: OptionalDeviceOrString = None,
    enable_meta_init_trick: bool = False,
    disable_meta_init_trick: bool = False,
):
    """
    A context manager similar to ``with torch.device(device)`` but with extra
    functionality for managing the "meta init trick".  (The meta init trick is
    when we build a pretrained model first on the torch meta device to avoid
    the cost of random initialization.  We then replace the meta parameters with
    real tensors that we load from a checkpoint.)

    Args:
        device (:obj:`str`, optional): The new value for the ``torch`` default
            device.  If ``None``, then we use the value of
            ``get_model_build_device(disable_meta_init_trick=disable_meta_init_trick)``,
            essentially keeping the value unchanged except for when the meta
            init trick is applied and we want to disable it. If
            ``enable_meta_init_trick`` is ``True``, then we force the device to "meta".
        enable_meta_init_trick (:obj:`bool`): Whether the purpose of the new
            context is specifically to apply the meta init trick.
        disable_meta_init_trick (:obj:`bool`): Whether to undo ancestor/parent
            applications of the context with ``enable_meta_init_trick=True``.  In
            this case, the default ``device`` becomes the value of
            ``get_model_build_device(disable_meta_init_trick=True)``.
    """

    if enable_meta_init_trick and disable_meta_init_trick:
        raise ValueError(
            "enable_meta_init_trick and disable_meta_init_trick cannot both be True"
        )

    if enable_meta_init_trick:
        device = "meta"
    if device is None:
        device = get_model_build_device(disable_meta_init_trick=disable_meta_init_trick)

    new_build_device_no_meta_trick = (
        get_model_build_device(disable_meta_init_trick=True)
        if enable_meta_init_trick
        else device
    )

    build_device_no_meta_trick_token = BUILD_DEVICE_NO_META_TRICK.set(
        new_build_device_no_meta_trick
    )

    try:
        with torch.device(device):
            yield
    finally:
        BUILD_DEVICE_NO_META_TRICK.reset(build_device_no_meta_trick_token)
