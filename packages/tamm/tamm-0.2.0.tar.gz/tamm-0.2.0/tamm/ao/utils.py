import contextlib
from typing import List as _List
from typing import Type as _Type
from typing import Union as _Union

from torch import nn as _nn

from tamm.ao.layers import FakeQuantize


def get_fake_quantize_layers(
    model: _nn.Module, parent_modules: _Union[None, _Type, _List[_Type]] = None
):
    """
    This method compiles all `FakeQuantize` layers which have a parent module in
    `model` in `parent_modules`, returning a dictionary of module names to
    `FakeQuantize` layers. If `parent_modules` is `None`, all `FakeQuantize` layers
    are returned.

    Args:
        model (:obj:`_nn.Module`): The model to get `FakeQuantize` layers from.
        parent_modules: (:obj:`Type` | `List[Type]`): Parent module class(es) to look
            for `FakeQuantize` layers in.  For example, if set to `TransformerAttention`,
            only `FakeQuantize` layers in `TransformerAttention` modules are returned.
            Defaults to `None` which does not perform any filtering.
    """
    layers = {}
    if isinstance(parent_modules, list):
        parent_modules = tuple(parent_modules)
    for name, module in model.named_modules():
        if parent_modules is None and isinstance(module, FakeQuantize):
            layers[name] = module
        elif parent_modules is not None and isinstance(module, parent_modules):
            layers_from_child = get_fake_quantize_layers(module, parent_modules=None)
            for child_name, child_module in layers_from_child.items():
                new_name = name
                if len(child_name) > 0:
                    new_name = f"{new_name}.{child_name}"
                layers[new_name] = child_module
    return layers


def set_fake_quantize_enabled(
    model: _nn.Module,
    value: bool,
    parent_modules: _Union[None, _Type, _List[_Type]] = None,
):
    """
    This method sets all `FakeQuantize.is_fake_quant_enabled` to `value` if a parent
    module in `model` is in `parent_modules`. If `parent_modules` is `None`, this is
    applied to all `FakeQuantize` layers.

    Args:
        model (:obj:`_nn.Module`): Model to set `FakeQuantize.is_fake_quant_enabled`.
        parent_modules: (:obj:`Type` | `List[Type]`): Parent module class(es) to set
            `FakeQuantize.is_fake_quant_enabled` layers in. For example, if set to
            `TransformerAttention`, only `FakeQuantize` layers in `TransformerAttention`
            modules are accessed. Defaults to `None` which does not filter.
    """
    layers = get_fake_quantize_layers(model, parent_modules=parent_modules)
    for fq in layers.values():
        fq.is_fake_quant_enabled = value


@contextlib.contextmanager
def fake_quantize_disabled_context(
    model: _nn.Module, parent_modules: _Union[None, _Type, _List[_Type]] = None
):
    """
    This context disables the quantize and dequantization steps in all `FakeQuantize`
    layers in `model` i.e. sets `FakeQuantize.is_fake_quant_enabled` to `False`. This
    does not affect `FakeQuantize.activation_post_process`, so quantization parameters
    may still update if enabled.

    Args:
        model (:obj:`_nn.Module`): The model to disable `FakeQuantize` layers for.
        parent_modules: (:obj:`Type` | `List[Type]`): Parent module class(es) to set
            `FakeQuantize.is_fake_quant_enabled` layers in. For example, if set to
            `TransformerAttention`, only `FakeQuantize` layers in `TransformerAttention`
            modules are accessed. Defaults to `None` which does not filter.
    """
    fake_quantize_layers = get_fake_quantize_layers(
        model, parent_modules=parent_modules
    )
    previous_settings = {}
    for k, fq in fake_quantize_layers.items():
        previous_settings[k] = fq.is_fake_quant_enabled
        fq.is_fake_quant_enabled = False
    try:
        yield None
    finally:
        for k, fq in fake_quantize_layers.items():
            fq.is_fake_quant_enabled = previous_settings[k]
