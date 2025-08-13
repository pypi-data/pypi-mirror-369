from torch import nn as _nn


def get_num_params(module: _nn.Module, *, recurse: bool = True) -> int:
    """
    Returns the total number of parameter elements in a :obj:`torch.nn.Module`.

    Args:
        module (:obj:`nn.Module`): The model or layer.
        recurse (:obj:`bool`, optional): A flag that controls recursion into
            submodules.  When ``False``, the function counts only parameters
            that are direct members of ``module``.  When ``True``, the function
            counts parameters from ``module`` and its submodules.  Defaults to
            ``True``.
    """
    return sum(p.numel() for p in module.parameters(recurse=recurse))


def get_num_trainable_params(module: _nn.Module, *, recurse: bool = True) -> int:
    """
    Returns the number of parameters in a module for which
    ``requires_grad`` is ``True``.

    Args:
        module (:obj:`nn.Module`): The model or layer.
        recurse (:obj:`bool`, optional): A flag that controls recursion into
            submodules.  Defaults to ``True``.
    """
    return sum(p.numel() for p in module.parameters(recurse=recurse) if p.requires_grad)


def get_num_frozen_params(module: _nn.Module, *, recurse: bool = True) -> int:
    """
    Returns the number of parameters in a module for which
    ``requires_grad`` is ``False``.

    Args:
        module (:obj:`nn.Module`): The model or layer.
        recurse (:obj:`bool`, optional): A flag that controls recursion into
            submodules.  Defaults to ``True``.
    """
    return sum(
        p.numel() for p in module.parameters(recurse=recurse) if not p.requires_grad
    )
