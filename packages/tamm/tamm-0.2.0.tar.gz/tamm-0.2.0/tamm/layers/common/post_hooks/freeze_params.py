from torch import nn as _nn

from tamm import context_vars as _context_vars
from tamm.layers.common._marker import get_marker, update_marker
from tamm.utils import OptionalBool as _OptionalBool


def _should_update_requires_grad(model: "_nn.Module") -> bool:
    """
    Check ._tamm_marker of a Module to determine whether to actually
    freeze the parameter. If .tamm_metadata is set to an explicit
    ``freeze_params_hook_applied`` value (either True or False),
    skip this post hook.
    """
    try:
        if get_marker(model).freeze_params_hook_applied != _OptionalBool.NOTSET:
            return False
    except AttributeError:
        return True
    return True


def require_explicit_freeze_params(func):
    """ "
    Decorate a function with this to raise an error when freeze_params is NOTSET.
    """

    def wrapper(module: "_nn.Module", freeze_params=_OptionalBool.NOTSET):
        if freeze_params == _OptionalBool.NOTSET:
            raise ValueError("freeze_params must be TRUE or FALSE")
        func(module, freeze_params)

    return wrapper


@require_explicit_freeze_params
def _recursively_freeze_params(
    module: "_nn.Module", freeze_params=_OptionalBool.NOTSET
):
    if not _should_update_requires_grad(module):
        return
    _freeze_direct_params(module, freeze_params=freeze_params)
    for sub_module in module.children():
        _recursively_freeze_params(sub_module, freeze_params=freeze_params)


@require_explicit_freeze_params
def _freeze_direct_params(module: "_nn.Module", freeze_params=_OptionalBool.NOTSET):
    update_marker(module, freeze_params_hook_applied=freeze_params)
    for param in module.parameters(recurse=False):
        param.requires_grad = not bool(freeze_params)


class FreezeParamsPostHook:
    def __call__(self, model: "_nn.Module") -> None:
        resolved = _context_vars.resolve_freeze_params()
        if resolved == _OptionalBool.NOTSET:
            return
        _recursively_freeze_params(model, freeze_params=resolved)

    def __repr__(self):
        return f"{self.__class__.__name__}()"
