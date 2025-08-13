# pylint: disable=cyclic-import

import re as _re
import warnings as _warnings
from collections import OrderedDict as _OrderedDict
from copy import copy as _copy
from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List
from typing import Mapping as _Mapping

import torch.nn as _nn

from tamm._adapters_v1.adapted_layer import AdaptedLayer as _AdaptedLayer
from tamm._adapters_v1.layer_adapters.common import LayerAdapter as _LayerAdapter
from tamm._adapters_v1.layer_adapters.lora import LoRA as _LoRA
from tamm._adapters_v1.layer_adapters.lora import (
    LoRAFusedMultiOutputLinear as _LoRAFusedMultiOutputLinear,
)
from tamm.runtime_configuration import rc as _rc
from tamm.typing import StateDictType as _StateDictType
from tamm.utils import torch_utils as _torch_utils

_TORCH_CHECKPOINT_ACTIVATION_KEY = "._checkpoint_wrapped_module"


def is_v0_lora_state_dict(state_dict: _Mapping[str, _Any]) -> bool:
    """
    Returns True if the state_dict corresponds to a Tamm v0 state dict.
    """
    pattern = _re.compile(r"\.adapter\.(lora_W(q|k|v)\.)?[ab]_transpose$")
    any_adapter_key = any("adapter" in key for key in state_dict)
    if not any_adapter_key:
        return False
    return all(
        _re.search(pattern, key) is not None for key in state_dict if "adapter" in key
    )


def _find_matched_v0_adapter_key(
    v1_key: str, v1_state_dict: _Mapping[str, _Any]
) -> str:
    # pylint:disable=line-too-long,unused-argument
    """
    Utility function to map v1 adapter keys to v0 style.
    Example 1 (Single LoRA):
        v0: layers.layer_0.attention.qkv_transform.adapter.lora_Wq.a_transpose
        v1: layers.layer_0.attention.qkv_transform.adapters.my_lora.lora_0.a_transpose
    Example 2 (Multiple/Composite LoRA):
        v0: layers.layer_0.attention.qkv_transform.adapter.lora_Wq.a_transpose
        v1: layers.layer_0.attention.qkv_transform.adapters.<parent_adapter_id>.<child_adapter_id>.lora_0.a_transpose
    Example 3 (Multiple/Composite LoRA):
        v0: layers.layer_0.attention.qkv_transform._wrapped.adapter.lora_Wk.a_transpose
        v1: layers.layer_0.attention.qkv_transform.adapters.<parent_adapter_id>.<child_adapter_id>.lora_1.a_transpose
    """
    v0_key = v1_key[: v1_key.find(".adapters.")]
    match = _re.search(r".adapters\.(\w+)\.([0-9]+)", v1_key)
    if match:
        depth = int(match.groups()[1]) + 1
        v0_key += "._wrapped" * (depth - 1)
    v0_key += ".adapter"
    if ".lora_" in v1_key:
        # LoRAFusedMultiOutputLinear adapter presents
        v0_key += ".lora_Wq." if ".lora_0." in v1_key else ""
        v0_key += ".lora_Wk." if ".lora_1." in v1_key else ""
        v0_key += ".lora_Wv." if ".lora_2." in v1_key else ""
    else:
        v0_key += "."
    return v0_key + v1_key.split(".")[-1]


def _find_adapter_names(v1_key: str, v1_state_dict: _Mapping[str, _Any]) -> _List[str]:
    """
    Helper function which finds all adapters in the state_dict
    which are applied to the same layer as v1_key.
    """
    layer_prefix = (
        v1_key[: v1_key.find(".wrapped.")]
        if ".wrapped." in v1_key
        else v1_key[: v1_key.find(".adapters.")]
    )
    adapter_key_prefix = layer_prefix + ".adapters."
    adapter_names = set()
    for key in v1_state_dict:
        if adapter_key_prefix in key:
            modified_key = key[len(adapter_key_prefix) :]
            # check LoRALinear
            pattern = _re.compile(r"\.[ab]_transpose")
            match = _re.search(pattern, modified_key)
            if match:
                adapter_names.add(modified_key[: match.start()])
                continue
            # check LoRAFusedMultiOutputLinear
            pattern = _re.compile(r"\.lora_([0-2])\.[ab]_transpose")
            match = _re.search(pattern, modified_key)
            if match:
                adapter_names.add(modified_key[: match.start()])
                continue
    return sorted(list(adapter_names))


def _find_matched_v0_wrapped_key(
    v1_key: str, v1_state_dict: _Mapping[str, _Any]
) -> str:
    """
    Utility function to map v1 wrapped layer keys to v0 style.
    Example 1 (Single LoRA):
        v0: layers.layer_0.attention.qkv_transform._wrapped.fused_linear.weight
        v1: layers.layer_0.attention.qkv_transform.wrapped.fused_linear.weight
    Example 2 (Multiple/Composite LoRA):
        v0: layers.layer_0.attention.qkv_transform._wrapped._wrapped.fused_linear.weight
        v1: layers.layer_0.attention.qkv_transform.wrapped.fused_linear.weight
    """
    adapter_names = _find_adapter_names(v1_key, v1_state_dict)
    adapter_names = set(_re.sub(r"lora_([0-9]+)", "X", name) for name in adapter_names)
    num_adapters = max(1, len(adapter_names))
    return (
        v1_key[: v1_key.find(".wrapped.")]
        + "._wrapped" * num_adapters
        + v1_key[v1_key.find(".wrapped.") + len(".wrapped") :]
    )


def _find_matched_v0_key(v1_key: str, v1_state_dict: _Mapping[str, _Any]) -> str:
    if ".adapters." in v1_key:
        return _find_matched_v0_adapter_key(v1_key, v1_state_dict)
    if ".wrapped." in v1_key:
        return _find_matched_v0_wrapped_key(v1_key, v1_state_dict)
    return v1_key


def _find_matched_v1_key(
    v0_key: str, v1_adapter_id: str, use_parallel_stack_composition: bool
) -> str:
    if ".adapter." in v0_key:
        v1_key = v0_key[: v0_key.find(".adapter.")]
        if use_parallel_stack_composition:
            v1_adapter_idx = v0_key.count("._wrapped")
            v1_key = v1_key.replace("._wrapped", "")
            v1_key += f".adapters.{v1_adapter_id}.{v1_adapter_idx}"
        else:
            v1_key += f".adapters.{v1_adapter_id}"
        if ".lora_W" in v0_key:
            # LoRAFusedMultiOutputLinear adapter presents
            v1_key += ".lora_0." if ".lora_Wq." in v0_key else ""
            v1_key += ".lora_1." if ".lora_Wk." in v0_key else ""
            v1_key += ".lora_2." if ".lora_Wv." in v0_key else ""
        else:
            v1_key += "."
        return v1_key + v0_key.split(".")[-1]
    if "._wrapped." in v0_key:
        return v0_key.replace("._wrapped", "", v0_key.count("._wrapped") - 1).replace(
            "._wrapped", ".wrapped"
        )
    return v0_key


def create_v1_state_dict(
    v0_state_dict: _Mapping[str, _Any], v1_adapter_id: str
) -> _Mapping[str, _Any]:
    """
    Create a v1 adapted model state_dict from a v0 ``tamm`` model.
    """
    _warnings.warn(
        "This conversion API assumes the v1 adapted model "
        "which loads the converted state_dict will only have one adapter "
        f"with the input adapter_id: {v1_adapter_id}."
    )
    v1_state_dict = _copy(v0_state_dict)
    use_parallel_stack_composition = any(
        "._wrapped.adapter" in v0_key for v0_key in v0_state_dict
    )
    for v0_key in v0_state_dict:
        v1_key = _find_matched_v1_key(
            v0_key, v1_adapter_id, use_parallel_stack_composition
        )
        if v1_key in v1_state_dict:
            continue
        v1_state_dict[v1_key] = v1_state_dict.pop(v0_key)
    return v1_state_dict


def maybe_rekey_v0_key(
    v1_state_dict: _Mapping[str, _Any], v0_state_dict: _Mapping[str, _Any]
) -> _Mapping[str, _Any]:
    """
    Load a v0 adapted ``tamm`` model state_dict.
    Only attention and feedforward layers
    adapted with LoRA adapters can be converted.
    """
    remaining_v0_state_dict_keys = set(v0_state_dict.keys())
    new_v1_state_dict = _OrderedDict()

    for v1_key in v1_state_dict:
        v0_key = _find_matched_v0_key(v1_key, v1_state_dict)
        if v0_key in v0_state_dict:
            new_v1_state_dict[v1_key] = v0_state_dict[v0_key]
            remaining_v0_state_dict_keys.remove(v0_key)
    # add the extra keys in v0 which v1 doesn't expect to v1 state dict so it can be handled
    # by strict Flag
    if len(remaining_v0_state_dict_keys) > 0:
        for v0_key in remaining_v0_state_dict_keys:
            new_v1_state_dict[v0_key] = v0_state_dict[v0_key]
    return new_v1_state_dict


def maybe_rekey_state_dict(
    model: _nn.Module, state_dict: _Mapping[str, _Any]
) -> _Mapping[str, _Any]:
    """
    Helper function to align state dict keys with a module's param names
    when one of the module or state dict has adapters but the other does not.
    Returns a copy of the state dict where keys have been updated to
    include or exclude ".wrapped" if this
    aligns the key with a module param name.
    """
    state_dict = _copy(state_dict)
    module_keys = [
        key.replace(_TORCH_CHECKPOINT_ACTIVATION_KEY, "") for key in model.state_dict()
    ]

    for module_name, module in model.named_modules():
        if isinstance(module, _AdaptedLayer):
            for key in module.state_dict().keys():
                stripped_module_name = module_name.replace(
                    _TORCH_CHECKPOINT_ACTIVATION_KEY, ""
                )
                stripped_key = key.replace(_TORCH_CHECKPOINT_ACTIVATION_KEY, "")
                original_key = stripped_module_name + "." + stripped_key
                unwrapped_key = stripped_module_name + stripped_key[len("wrapped") :]
                if (
                    unwrapped_key in state_dict
                    and original_key not in state_dict
                    and unwrapped_key not in module_keys
                ):
                    state_dict[original_key] = state_dict.pop(unwrapped_key)

    def create_unwrapped_keys_helper(splitted_keys, prev_unwrapped_keys) -> _List[str]:
        """
        Helper function to generate unwrapped keys considering
        the possibility of any nested AdaptedLayer existing.
        """
        if not splitted_keys:
            return prev_unwrapped_keys
        cur_unwrapped_keys = []
        for prev_unwrapped_key in prev_unwrapped_keys:
            cur_unwrapped_keys.append(prev_unwrapped_key + splitted_keys[0])
            cur_unwrapped_keys.append(
                prev_unwrapped_key + ".wrapped" + splitted_keys[0]
            )
        return create_unwrapped_keys_helper(splitted_keys[1:], cur_unwrapped_keys)

    for key in list(state_dict.keys()):
        unwrapped_keys = []
        splitted_keys = key.split(".wrapped")
        if len(splitted_keys) == 1:
            unwrapped_keys = [key]
        elif len(splitted_keys) == 2:
            unwrapped_keys = ["".join(splitted_keys)]
        else:
            unwrapped_keys.extend(
                create_unwrapped_keys_helper(splitted_keys[1:], [splitted_keys[0]])
            )

        for unwrapped_key in unwrapped_keys:
            if (
                unwrapped_key in module_keys
                and unwrapped_key not in state_dict
                and key not in module_keys
            ):
                state_dict[unwrapped_key] = state_dict.pop(key)
                break

    return state_dict


def remap_adapter_state_dict_keys(
    model: _nn.Module, state_dict: _Mapping[str, _Any]
) -> _Mapping[str, _Any]:
    if _rc.adapters_implementation == "v1":
        if is_v0_lora_state_dict(state_dict):
            # Convert v0 style state_dict to v1.
            state_dict = maybe_rekey_v0_key(
                v1_state_dict=model.state_dict(), v0_state_dict=state_dict
            )
        # Handling possible extra/missing ".wrapped" in state_dict keys.
        state_dict = maybe_rekey_state_dict(model, state_dict)
    return state_dict


def get_linear_adapter(key: str) -> "_LayerAdapter":
    """
    Backward compatible replacement for :func:`adapters_v0.get_linear_adapter`.
    This method only takes input key as "lora" or "lora-linear".
    Where "lora" maps to `LoRAFusedMultiOutputLinear.Config` and "lora-linear" maps to `LoRA.Config`.
    """
    if key not in {"lora", "lora-linear"}:
        raise RuntimeError(
            "`_adapter_v1.get_linear_adapter` accepts either 'lora' or 'lora-linear'."
        )
    if key == "lora":
        return _LoRAFusedMultiOutputLinear.Config
    return _LoRA.Config


def split_adapted_weights(state_dict: dict) -> _Dict[str, _Dict]:
    """
    Utility function that splits adapter fine-tuned model weights into backbone and
    adapter weights.

    Args:
        state_dict: State dictionary of the complete model (backbone+adapter)

    Returns: dictionary with keys "backbone_state_dict", and "adapter_state_dict"

    """

    def _is_adapter_key(name):
        return "adapters" in name

    def _normalize(name):
        return name.replace(".wrapped", "")

    backbone = {k: v for k, v in state_dict.items() if not _is_adapter_key(k)}
    adapter = {k: v for k, v in state_dict.items() if _is_adapter_key(k)}

    backbone = {_normalize(k): v for k, v in backbone.items()}
    return {
        "backbone_state_dict": backbone,
        "adapter_state_dict": adapter,
    }


def merge_adapters(module, remove=True):
    """
    Merge active adapters into the backbone modules.
    If there's no active adapters in the passed in module,
    this function will become a no-op.

    Args:
        module (:obj:`_nn.Module`): the model with lora adapters.
        remove (:obj:`bool`): Flag to remove the extra adapter post-merge.
    """
    # pylint: disable=import-outside-toplevel
    from tamm._adapters_v1.adapter_api import (
        get_all_active_adapter_ids,
        is_adapter_initialized,
        merge_adapter,
        uninit,
    )

    active_adapter_ids = get_all_active_adapter_ids(module)

    if not is_adapter_initialized(module) or len(active_adapter_ids) == 0:
        _warnings.warn(
            "No active adapters found. Nothing to be merged. This `merge_adapters` will be a NO-OP."
        )

    for adapter_id in active_adapter_ids:
        merge_adapter(module, adapter_id)
    if remove:
        module = uninit(module, force=True)

    return module


def get_num_adapter_params(model: _nn.Module, only_trainable: bool = False):
    """
    Utility function to get the number of adapter parameters in the given model.

    Args:
        model (:obj:`_nn.Module`): The input adapted model.
        only_trainable (:obj:`bool`):
            Flag to indicate if only trainable parameters are counted.
    """
    if only_trainable:
        return sum(
            _torch_utils.get_num_trainable_params(module.adapters)
            for module in model.modules()
            if isinstance(module, _AdaptedLayer)
        )
    return sum(
        _torch_utils.get_num_params(module.adapters)
        for module in model.modules()
        if isinstance(module, _AdaptedLayer)
    )


def find_adapter_ids_from_state_dict(state_dict: _StateDictType) -> _List[str]:
    """
    Finds all possible adapter_ids in the state dict, by finding all keys
    which match *.adapters.<adapter_id>.* pattern.
    """
    adapter_ids = set()
    for key in state_dict:
        pattern = _re.compile(r"(?<=\.adapters\.)[^.]+(?=\.|$)")
        match = _re.search(pattern, key)
        if match:
            adapter_ids.add(match.group())
            continue
    return sorted(list(adapter_ids))
