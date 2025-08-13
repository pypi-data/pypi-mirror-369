import logging as _logging
from typing import Union as _Union

from torch import nn as _nn

from tamm._adapters_v1 import ModelAdapter as _ModelAdapterV1
from tamm._adapters_v1.adapter_api import get_all_adapter_ids as _get_all_adapter_ids
from tamm._adapters_v1.adapter_api import set_active_adapter as _set_active_adapter
from tamm.layers.common.post_hooks.common import CompositePostHook, IdentityPostHook

_logger = _logging.getLogger(__name__)


class ModelAdapterPostHook:
    def __init__(
        self,
        model_adapter: "_ModelAdapterV1",
        *,
        adapter_id: str,
    ):
        self.model_adapter = model_adapter
        self.adapter_id = adapter_id

    def __call__(self, model: _nn.Module) -> _nn.Module:
        self.model_adapter.adapt_model(
            model,
            adapter_id=self.adapter_id,
        )
        return model


class ActivateAdapterPostHook:
    def __init__(
        self,
        active_adapter: _Union[int, str] = 0,
    ):
        self.active_adapter = active_adapter

    def __call__(self, model: _nn.Module) -> _nn.Module:
        if isinstance(self.active_adapter, int):
            model_adapters = _get_all_adapter_ids(model)
            if self.active_adapter >= len(model_adapters):
                raise IndexError(
                    "Not enough adapters present in the model. "
                    f"Trying to activate adapter with index {self.active_adapter} "
                    f"while only {len(model_adapters)} adapters "
                    "present in the model."
                )
            self.active_adapter = model_adapters[self.active_adapter]
        _set_active_adapter(model, self.active_adapter)
        return model


def get_model_adapters_post_hook(
    adapters: dict,
    active_adapter: _Union[int, str] = 0,
):
    if adapters is None:
        return IdentityPostHook()

    hooks = [
        ModelAdapterPostHook(model_adapter, adapter_id=adapter_id)
        for adapter_id, model_adapter in adapters.items()
    ]
    hooks.append(ActivateAdapterPostHook(active_adapter=active_adapter))

    return CompositePostHook(*hooks)
