import abc as _abc
import dataclasses as _dataclasses
import textwrap as _textwrap
from typing import Optional as _Optional
from typing import Set as _Set

import torch as _torch
import torch.nn as _nn

from tamm import _helpers
from tamm.context_vars import resolve_pretrained_flag as _resolve_pretrained_flag
from tamm.layers.common import PretrainedLoader as _PretrainedLoader
from tamm.typing import LenientOptionalBool
from tamm.typing import OptionalDeviceOrString as _OptionalDeviceOrString
from tamm.utils import OptionalBool as _OptionalBool
from tamm.utils.json import JSONSerializableABCMixin

# pylint: disable=no-member  # pylint does not pick up some dataclass fields
# pylint: disable=duplicate-code  # probably should refactor with ModelAdapter


class ArchOptimizer(JSONSerializableABCMixin, json_namespace="ao"):
    """
    A base class for objects that apply optimizations to |tamm| models.
    """

    # pylint: disable=signature-differs
    def __init_subclass__(cls):
        cls._inject_common_fields_and_make_dataclass()

    @classmethod
    def _inject_common_fields_and_make_dataclass(cls):
        _helpers.set_annotated_class_attr(cls, "pretrained_path", None, _Optional[str])
        _helpers.set_annotated_class_attr(cls, "device", None, _OptionalDeviceOrString)
        _dataclasses.dataclass(cls, repr=False)

    def optimize(
        self,
        model: _nn.Module,
        *,
        pretrained: "LenientOptionalBool" = _OptionalBool.NOTSET,
    ) -> None:
        """
        Applies optimizations to a model.

        Args:
            model (:obj:`torch.nn.Module`): The model to optimize.
            pretrained (:obj:`LenientOptionalBool`): A flag for loading pretrained
                state. If ``OptionalBool.TRUE``, then the method loads the state dict
                from ``pretrained_path`` into newly created layers. Python ``True``,
                and ``False`` are also accepted.
        """
        resolved_pretrained_flag = _resolve_pretrained_flag(pretrained)
        should_load_pretrained = (
            resolved_pretrained_flag == _OptionalBool.TRUE
            and self.pretrained_path is not None
        )
        target_device = self.device
        if should_load_pretrained:
            target_device = "meta"

        prior_state = set(_helpers.get_all_params_and_buffers(model))

        with _helpers.get_device_context(target_device):
            self._optimize_impl(model, pretrained=resolved_pretrained_flag)

        if should_load_pretrained:
            self._load_pretrained(model=model, prior_state=prior_state)

    def _load_pretrained(
        self, *, model: _nn.Module, prior_state: _Set[_torch.Tensor]
    ) -> None:
        if self.pretrained_path is None:
            return

        new_keys = {
            name
            for name, tensor in model.state_dict(keep_vars=True).items()
            if tensor not in prior_state
        }
        loader = _PretrainedLoader(
            path=self.pretrained_path,
            keys=new_keys,
            target_device=self.device,
        )
        loader.load(model)

    @_abc.abstractmethod
    def _optimize_impl(
        self,
        model: _nn.Module,
        *,
        pretrained: "_OptionalBool" = _OptionalBool.NOTSET,
    ) -> None:
        """Applies optimizations to a model."""

    def _to_json_dict_impl(self):
        return _helpers.dataclass_to_dict(
            self, omit_defaults=True  # only non-defaults for forward compatibility
        )

    def __repr__(self):
        args_dict = _helpers.dataclass_to_dict(self)
        args_reprs = [f"{key}={repr(value)}," for key, value in args_dict.items()]
        joined_args = "\n".join(args_reprs)
        intended_args = _textwrap.indent(joined_args, prefix=" " * 4)
        return f"{self.__class__.__name__}(\n{intended_args}\n)"
