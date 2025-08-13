"""
adapters.model_adapters
=======================

.. autoclass:: tamm.adapters.ModelAdapter
    :show-inheritance:
    :members:
"""

# pylint: disable=no-member, cyclic-import

import dataclasses as _dataclasses
import logging as _logging
from typing import Dict as _Dict
from typing import Optional as _Optional

import torch as _torch

from tamm import _helpers
from tamm._adapters_v1.adapter_api import init as _init
from tamm._adapters_v1.adapter_api import (
    is_adapter_initialized as _is_adapter_initialized,
)
from tamm._adapters_v1.layer_adapters.common import LayerAdapter as _LayerAdapter
from tamm._adapters_v1.utils import create_v1_state_dict, is_v0_lora_state_dict
from tamm.context_vars import resolve_device
from tamm.context_vars import resolve_pretrained_flag as _resolve_pretrained_flag
from tamm.utils import OptionalBool as _OptionalBool
from tamm.utils._pretrained import fetch_checkpoint as _fetch_checkpoint
from tamm.utils.json import JSONSerializableABCMixin as _JSONSerializableABCMixin

_logger = _logging.getLogger(__name__)


@_dataclasses.dataclass
class AdapterSpec:
    layer_adapters: _Optional[_Dict[str, _LayerAdapter]]


class ModelAdapter(_JSONSerializableABCMixin, json_namespace="adapters"):
    """
    Base class for model adapters.
    """

    # pylint: disable=signature-differs
    def __init_subclass__(cls):
        cls._inject_common_fields()
        _dataclasses.dataclass(cls)

    @classmethod
    def _inject_common_fields(cls):
        _helpers.set_annotated_class_attr(
            cls, "pretrained", _OptionalBool.NOTSET, _OptionalBool
        )
        _helpers.set_annotated_class_attr(cls, "pretrained_path", None, _Optional[str])
        _helpers.set_annotated_class_attr(cls, "device", None, _Optional[_torch.device])
        _helpers.set_annotated_class_attr(
            cls, "dtype", _torch.float32, _Optional[_torch.dtype]
        )
        _helpers.set_annotated_class_attr(cls, "freeze_params", False, bool)

    def create_adapters(self, model: _torch.nn.Module) -> AdapterSpec:
        """
        Create :py:class:`_LayerAdapter` for layers in model which are adapted
        by this model adapter.

        Args:
            model (:py:class:`torch.nn.Module`): Model to be adapted.

        Returns:
            An :py:class:`AdapterSpec` object which containts a dictionary
            mapping layer names to adapters used for adapting them.
        """
        with resolve_device(self.device):
            adapter_spec = self._create_adapters_impl(model)
        self._maybe_load_pretrained(adapter_spec)
        self._maybe_freeze_adapters(adapter_spec)
        return adapter_spec

    def adapt_model(self, model: _torch.nn.Module, adapter_id: str):
        """
        Adapt model with this model adapter using the specified ``adapter_id``.

        Args:
            model (:py:class:`_nn.Module`): Top level model to which adapters are to be added.
            adapter_id (:obj:`str`): A unique identifier for the adapters being added.
        """
        if not _is_adapter_initialized(model):
            model = _init(model)
        adapter_spec = self.create_adapters(model)
        for layer_name, layer_adapter in adapter_spec.layer_adapters.items():
            submodule = model.get_submodule(layer_name)
            submodule.add_adapter(adapter_id, layer_adapter)

    def _create_adapters_impl(self, model: _torch.nn.Module) -> AdapterSpec:
        """
        Implementation of create_adapters method.

        Create :py:class:`_LayerAdapter` for layers in model which are adapted
        by this model adapter.

        Args:
            model (:py:class:`torch.nn.Module`): Model to be adapted.

        Returns:
            An :py:class:`AdapterSpec` object which containts a dictionary
            mapping layer names to adapters used for adapting them.
        """
        raise NotImplementedError(
            "This method is not implemented by the base ModelAdapter class. "
        )

    @staticmethod
    def _transform_key(key: str, layer_name: str) -> str:
        """
        Remove adapter_id from layer_name to enable state dict loading.
        """
        layer_prefix = f"{layer_name}.adapters."
        return key[len(layer_prefix) :].split(".", 1)[1]

    def _maybe_load_pretrained(self, adapter_spec: AdapterSpec) -> None:
        """
        Load pretrained adapter weights if possible.
        """
        if self.pretrained_path is None:
            return
        resolved_pretrained_flag = _resolve_pretrained_flag(self.pretrained)
        if resolved_pretrained_flag != _OptionalBool.TRUE:
            return

        state_dict = _fetch_checkpoint(self.pretrained_path)
        if is_v0_lora_state_dict(state_dict):
            state_dict = create_v1_state_dict(state_dict, "V1_ADAPTER_ID_PLACE_HOLDER")

        for name, adapter in adapter_spec.layer_adapters.items():
            adapter_sd = {
                self._transform_key(k, layer_name=name): v
                for k, v in state_dict.items()
                if k.startswith(name)
            }
            adapter.load_state_dict(adapter_sd)

    def _maybe_freeze_adapters(self, adapter_spec: AdapterSpec) -> None:
        """
        Make adapters un-trainable if requested.
        """
        if not self.freeze_params:
            return
        for adapter in adapter_spec.layer_adapters.values():
            adapter.freeze()

    def _to_json_dict_impl(self):
        result = _helpers.dataclass_to_dict(
            self, omit_defaults=True  # only non-defaults for forward compatibility
        )
        return result

    @classmethod
    def _from_json_dict_impl(cls, **raw_dict: dict):
        raw_dict = _helpers.maybe_get_enum_member_for_all_str_enums(raw_dict, cls)
        return super()._from_json_dict_impl(**raw_dict)
