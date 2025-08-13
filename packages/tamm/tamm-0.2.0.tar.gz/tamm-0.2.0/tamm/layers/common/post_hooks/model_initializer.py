import logging as _logging
from typing import Set as _Set

import torch.nn as _nn

from tamm.context_vars import get_model_build_device as _get_model_build_device
from tamm.context_vars import resolve_pretrained_flag as _resolve_pretrained_flag
from tamm.layers.common._marker import get_marker, update_marker
from tamm.layers.common.pretrained_loader import PretrainedLoader
from tamm.utils import OptionalBool

_logger = _logging.getLogger(__name__)


class ModelInitializerPostHook:
    """
    Applies pretrained context if explicitly provided in
    ``create_builder(pretrained=[True|False])`` calls.
    """

    def __init__(self, path: str):
        self.path = path

    def __call__(self, model: _nn.Module) -> None:
        if _resolve_pretrained_flag() == OptionalBool.TRUE and self.path is None:
            return

        if _resolve_pretrained_flag() == OptionalBool.FALSE:
            # Users specify to random initialize the current module.
            update_marker(model, weights_initialized=True)
            return

        target_keys = self._get_target_keys(model)
        PretrainedLoader(
            path=self.path,
            target_device=_get_model_build_device(disable_meta_init_trick=True),
            keys=target_keys,
        ).load(model)
        update_marker(model, weights_initialized=True)

    @classmethod
    def _get_target_keys(
        cls, module, target_keys: _Set[str] = None, prefix: str = ""
    ) -> _Set[str]:
        if target_keys is None:
            target_keys = set()

        # Store buffers
        target_keys = target_keys.union(
            # pylint: disable=protected-access
            {
                prefix + ("." if prefix else "") + name
                for name, _ in module.named_buffers(recurse=False)
                if name not in module._non_persistent_buffers_set
            }
        )

        # Store parameters
        target_keys = target_keys.union(
            {
                prefix + ("." if prefix else "") + name
                for name, _ in module.named_parameters(recurse=False)
            }
        )

        # Loop through all submodules
        for name, sub_module in module.named_children():
            if get_marker(sub_module).weights_initialized:
                continue
            submodule_prefix = prefix + ("." if prefix else "") + name
            target_keys = target_keys.union(
                cls._get_target_keys(sub_module, target_keys, submodule_prefix)
            )
        return target_keys
