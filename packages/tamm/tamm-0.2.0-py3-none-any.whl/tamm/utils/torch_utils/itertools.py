from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import Iterable as _Iterable
from typing import Tuple as _Tuple

import torch as _torch


def iter_named_parameters_and_buffers_with_layers(
    module: _torch.nn.Module,
) -> _Iterable[_Tuple[str, _torch.Tensor, _torch.nn.Module]]:
    """
    Generates ``(name, tensor, layer)`` tuples for all parameters and
    buffers in a :obj:`torch.nn.Module`.  Here ``tensor`` is the param or buffer,
    ``name`` is its full name in the module's state dict, and ``layer``
    is the :obj:`nn.Module` that owns ``tensor``.

    Args:
        module (:obj:`nn.Module`): The model or layer.
    """
    for layer_name, layer in module.named_modules():
        params = layer.named_parameters(
            recurse=False, remove_duplicate=False, prefix=layer_name
        )
        for name, param in list(params):
            yield name, param, layer

        buffers = layer.named_buffers(
            recurse=False, remove_duplicate=False, prefix=layer_name
        )
        for name, buffer in list(buffers):
            yield name, buffer, layer


def iter_named_parameters_and_buffers(
    module: _torch.nn.Module,
) -> _Iterable[_Tuple[str, _torch.Tensor]]:
    """
    Similar to :func:`iter_named_parameters_and_buffers_with_layers`
    but only yields names and parameters/buffers from ``module`` (so no layers).

    Args:
        module (:obj:`nn.Module`): The model or layer.
    """
    for name, tensor, _ in iter_named_parameters_and_buffers_with_layers(module):
        yield name, tensor


@_torch.no_grad()
def map_named_parameters_and_buffers(
    func: _Callable[[str, _torch.Tensor], _torch.Tensor],
    module: _torch.nn.Module,
    use_new_requires_grad_values: bool = False,
) -> _torch.nn.Module:
    """
    Overwrites all parameters and buffers in :obj:`torch.nn.Module` with the
    result of a map function, ``func``.

    Args:
        func (:obj:`callable`): A function that accepts two positional arguments,
            ``name`` and ``tensor``, and returns a new :obj:`torch.Tensor`.
            The ``tensor`` arg is a parameter or buffer from ``module``, and
            ``name`` is its full name in ``module``.  The return value is the new
            value for the parameter or buffer.
        module (:obj:`torch.nn.Module`): The model or layer with parameters/buffers
            to map.
        use_new_requires_grad_values (:obj:`bool`, optional): A flag that results
            in parameters taking the ``requires_grad`` value of the mapped tensor.
            Defaults to ``False``, in which case the ``requires_grad`` values
            do not change, regardless of the ``requires_grad`` attributes of tensors
            returned by ``func``.
    """
    cache: _Dict[int, _torch.Tensor] = {}
    for name, tensor, layer in iter_named_parameters_and_buffers_with_layers(module):
        cache_key = id(tensor)
        if cache_key in cache:
            new_tensor = cache[cache_key]  # important so that tied params stay tied
        else:
            new_tensor = func(name, tensor)
            if new_tensor is not tensor and isinstance(tensor, _torch.nn.Parameter):
                if use_new_requires_grad_values:
                    requires_grad_value = new_tensor.requires_grad
                else:
                    requires_grad_value = tensor.requires_grad
                new_tensor = _torch.nn.Parameter(
                    new_tensor, requires_grad=requires_grad_value
                )
            cache[cache_key] = new_tensor

        short_name = name.rsplit(".", maxsplit=1)[-1]
        if isinstance(new_tensor, _torch.nn.Parameter):
            delattr(layer, short_name)
            layer.register_parameter(short_name, new_tensor)
        else:
            persistent = short_name in layer.state_dict(keep_vars=True)
            delattr(layer, short_name)
            layer.register_buffer(short_name, new_tensor, persistent=persistent)
    return module
