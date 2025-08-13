import warnings as _warnings
from typing import Iterable as _Iterable
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch
from torch import nn as _nn

from tamm.context_vars import resolve_device as _resolve_device
from tamm.layers.common._marker import get_marker as _get_marker
from tamm.layers.common.builder import BuildableMixin as _BuildableMixin
from tamm.typing import OptionalDeviceOrString as _OptionalDeviceOrString
from tamm.typing import StateDictType as _StateDictType
from tamm.utils import _is_same_device_type
from tamm.utils import torch_utils as _torch_utils
from tamm.utils._pretrained import fetch_checkpoint


class PretrainedLoader(_BuildableMixin):
    """
    Fetches and loads pretrained state into models.

    Args:
        path (:obj:`str`): A URI to a pretrained ``torch`` checkpoint (saved with
            :func:`torch.save`).
        target_device: The device to place meta tensors.  If ``None``, meta tensors
            end up on the ``torch`` default device.
        keys (iterable of :obj:`str`): An iterable of expected keys in the state
            dict.  Loading raises a :obj:`RuntimeError` if the keys in the checkpoint
            do not match this set.  Defaults to all keys in the module's state dict.
    """

    def __init__(
        self,
        *,
        path: _Union[str, _List[str], None] = None,
        target_device: _OptionalDeviceOrString = None,
        keys: _Optional[_Iterable[str]] = None,
    ):
        self.path = path
        self.target_device = target_device
        self.keys = set(keys) if keys is not None else None

    def load(self, module: _nn.Module) -> None:
        if self.path is None:
            return
        resolved_device = _resolve_device(self.target_device)
        if resolved_device is not None and _is_same_device_type(
            resolved_device, _torch.device("meta")
        ):
            raise RuntimeError(
                "`PretrainedLoader(...).load()` resolved 'meta' as target device which "
                "cannot be loaded with real `nn.Parameter`s "
                "If torch.get_default_device()=='meta', override "
                "'target_device' with a concrete device "
                "such as torch.device('cpu'); Or use a concrete device context"
            )
        if self.keys is None:
            self.keys = set(module.state_dict().keys())

        self._initialize_non_persistent_buffers(module=module, device=resolved_device)

        state_dict = fetch_checkpoint(self.path, map_location=resolved_device)
        result = self._load_state_dict(module=module, state_dict=state_dict)
        self._validate_keys(result)

    def _initialize_non_persistent_buffers(self, module, device):
        for layer in module.modules():
            if _get_marker(layer).weights_initialized:
                continue
            buffers = dict(layer.named_buffers(recurse=False, remove_duplicate=False))
            non_persistent_buffer_names = list(
                buffers.keys() - layer.state_dict().keys()
            )

            if len(non_persistent_buffer_names) == 0:
                continue

            non_persistent_buffers = {
                name: buffers[name] for name in non_persistent_buffer_names
            }

            if any(
                buffer.device.type == "meta"
                for buffer in non_persistent_buffers.values()
            ):
                layer.to_empty(device=device, recurse=False)
                if not hasattr(layer, "reset_parameters"):
                    raise RuntimeError(
                        f"Could not initialize non-persistent buffer, since {layer} has no "
                        "reset_parameters() method"
                    )
                layer.reset_parameters()
            else:
                layer.to(device=device)

    def _validate_keys(
        self, result: "_torch.nn.modules.module._IncompatibleKeys"
    ) -> None:
        """
        Validates all keys in `self.keys` do not present in result.missing_keys
        and logs extra keys from state_dict.
        """

        missing_keys = (
            [key for key in result.missing_keys if key in self.keys]
            if self.keys is not None
            else result.missing_keys
        )
        if missing_keys:
            raise RuntimeError(
                f"Could not load {self.path} into the model because the following "
                f"keys are missing from this checkpoint: {missing_keys}"
            )

        if result.unexpected_keys:
            _warnings.warn(
                f"The checkpoint {self.path} contains unexpected keys "
                f"that have not been loaded into the model: {result.unexpected_keys}"
            )

    def _load_state_dict(self, *, module: _nn.Module, state_dict: _StateDictType):
        """
        Calls module.load_state_dict(state_dict, assign=True) with extra logic to handle
        self.keys and to prevent the dtype of parameters from changing.

        Important: We sometimes override module.load_state_dict() to rename keys on the
        fly.  Thus, the state_dict keys do not necessarily match the parameter names.
        """

        original_dtypes_and_requires_grads = {
            name: (tensor.dtype, tensor.requires_grad)
            for name, tensor in _torch_utils.iter_named_parameters_and_buffers(module)
        }

        ignored_keys = set(module.state_dict().keys()) - self.keys
        preserved_weights = {
            key: value
            for key, value in module.state_dict().items()
            if key in ignored_keys
        }
        result = module.load_state_dict(state_dict, assign=True, strict=False)
        module.load_state_dict(preserved_weights, assign=True, strict=False)

        def update_tensor(name, tensor):
            dtype, requires_grad = original_dtypes_and_requires_grads[name]
            tensor = tensor.type(dtype)
            tensor = tensor.contiguous()
            tensor.requires_grad_(requires_grad)
            return tensor

        _torch_utils.map_named_parameters_and_buffers(
            update_tensor, module, use_new_requires_grad_values=True
        )

        return result
