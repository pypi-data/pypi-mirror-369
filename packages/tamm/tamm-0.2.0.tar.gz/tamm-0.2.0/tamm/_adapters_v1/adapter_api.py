"""
.. _adapter_api:

adapters.adapter_api
====================

.. autofunction:: tamm.adapters.init

.. autofunction:: tamm.adapters.is_adapter_initialized

.. autofunction:: tamm.adapters.has_adapter

.. autofunction:: tamm.adapters.delete_adapter

.. autofunction:: tamm.adapters.freeze_adapter

.. autofunction:: tamm.adapters.unfreeze_adapter

.. autofunction:: tamm.adapters.set_active_adapter

.. autofunction:: tamm.adapters.unset_active_adapter

.. autofunction:: tamm.adapters.merge_adapter

.. autofunction:: tamm.adapters.get_all_adapter_ids

.. autofunction:: tamm.adapters.get_all_active_adapter_ids

.. autofunction:: tamm.adapters.map_state_dict

.. autofunction:: tamm.adapters.load_state_dict

.. autoclass:: tamm.adapters.AdaptedModelStateDictFormat
"""

import enum as _enum
import logging as _logging
import warnings as _warnings
from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Set as _Set

import torch.nn as _nn
from torch.nn.modules.module import _IncompatibleKeys

from tamm import _helpers
from tamm._adapters_v1.adapted_layer import AdaptedLayer as _AdaptedLayer
from tamm._adapters_v1.layer_adapters.common import (
    AdapterWithExtraInputs as _AdapterWithExtraInputs,
)
from tamm._adapters_v1.layer_annotations import (
    is_adaptable_layer as _is_adaptable_layer,
)
from tamm._adapters_v1.shared_context import SharedContext as _SharedContext
from tamm._adapters_v1.utils import is_v0_lora_state_dict as _is_v0_lora_state_dict
from tamm._adapters_v1.utils import maybe_rekey_state_dict as _maybe_rekey_state_dict
from tamm._adapters_v1.utils import maybe_rekey_v0_key as _maybe_rekey_v0_key
from tamm._helpers import case_insensitive_lookup

_logger = _logging.getLogger(__name__)

__all__ = [
    "AdaptedModelStateDictFormat",
    "init",
    "is_adapter_initialized",
    "has_adapter",
    "delete_adapter",
    "freeze_adapter",
    "unfreeze_adapter",
    "set_active_adapter",
    "unset_active_adapter",
    "merge_adapter",
    "get_all_adapter_ids",
    "get_all_active_adapter_ids",
    "map_state_dict",
    "load_state_dict",
]


class AdaptedModelStateDictFormat(str, _enum.Enum):
    """
    An enum for controlling the :meth:`state_dict` behavior of :py:class:`AdaptedModel`

    FULL - load/get state_dict corresponding to the wrapped model and all adapters
    BASE - load/get state_dict corresponding to only the wrapped model
    ADAPTER - load/get state_dict corresponding to only the adapters
    """

    FULL = "FULL"
    BASE = "BASE"
    ADAPTER = "ADAPTER"

    @classmethod
    def _missing_(cls, value):
        return case_insensitive_lookup(cls, value)


def init(model: _nn.Module) -> _nn.Module:
    """
    Prepares model for adaptation.

    Args:
        model (:py:class:`_nn.Module`): Top level model which is adapted.

    Returns:
        :py:class:`_nn.Module` where adaptable layers are wrapped with :py:class:`_AdaptedLayer`
        wrappers.
    """
    adapted_map = {}
    children_to_wrap = []

    for parent in model.modules():
        for name, child in _helpers.get_all_named_children(parent):
            if _is_adaptable_layer(child) and not isinstance(child, _AdaptedLayer):
                if child not in adapted_map:
                    adapted_map[child] = _AdaptedLayer(child)
                children_to_wrap.append((parent, name, adapted_map[child]))

    for parent, name, new_child in children_to_wrap:
        parent.add_module(name, new_child)

    if _is_adaptable_layer(model):
        model = _AdaptedLayer(model)

    return model


def _verify_no_adapters(module: _AdaptedLayer, force: bool = False):
    if len(module.adapters) > 0:
        adapter_ids = list(module.adapters.keys())
        if force:
            _warnings.warn(
                f"Removing adapters with ids: {adapter_ids} from layer. If this is not "
                f"the intended outcome, consider merging the adapters before removing them."
            )
        else:
            raise RuntimeError(
                f"Trying to remove adapters with ids: {adapter_ids} from layer. "
                f"Merge them or pass force=True to force remove."
            )


def uninit(model: _nn.Module, force: bool = False) -> _nn.Module:
    """
    Removes adapters and adapted layer from the model.

    Args:
        model (:py:class:`_nn.Module`): Top level adapted model.
        force (:obj:`bool`): If force is ``True``, adapted layers are
            removed even if some layers have unmerged adapters, otherwise
            unmerged adapters lead to ``RuntimeError``.

    Returns:
    """
    adapted_map = {}
    children_to_unwrap = []

    for parent in model.modules():
        for name, child in _helpers.get_all_named_children(parent):
            if isinstance(child, _AdaptedLayer):
                _verify_no_adapters(child, force=force)
                if child not in adapted_map:
                    adapted_map[child] = child.wrapped
                children_to_unwrap.append((parent, name, adapted_map[child]))

    for parent, name, new_child in children_to_unwrap:
        parent.add_module(name, new_child)

    if isinstance(model, _AdaptedLayer):
        _verify_no_adapters(model, force=force)
        model = model.wrapped

    return model


def is_adapter_initialized(model: _nn.Module) -> bool:
    """
    Returns ``True`` if the model has been prepared for adaptation by wrapping with :py:func:`init`.
    """
    for _, module in model.named_modules(remove_duplicate=True):
        if isinstance(module, _AdaptedLayer):
            return True
    return False


def has_adapter(model: _nn.Module, adapter_id: str):
    """
    Returns ``True`` if the model has an adapter with ``adapter_id``.

    Args:
        model (:py:class:`_nn.Module`): Top level model with adapters.
        adapter_id (:obj:`str`): The unique identifier for the adapter(s)
    """
    for _, module in model.named_modules(remove_duplicate=True):
        if isinstance(module, _AdaptedLayer) and module.has_adapter(adapter_id):
            return True
    return False


def _get_adapted_layers(model):
    return [layer for layer in model.modules() if isinstance(layer, _AdaptedLayer)]


def _apply_to_submodules(
    model: _nn.Module, apply_fn: str, adapter_id: _Optional[str] = None, **kwargs: _Any
):
    """
    Apply the function ``apply_fn`` to all submodules which are wrapped with
    :py:class:`_AdaptedLayer` wrappers.
    """
    if not has_adapter(model, adapter_id):
        raise RuntimeError(f"Model does not have adapter: {adapter_id}")

    for mod in _get_adapted_layers(model):
        if adapter_id and mod.has_adapter(adapter_id):
            getattr(mod, apply_fn)(adapter_id, **kwargs)
        elif adapter_id is None:
            getattr(mod, apply_fn)()


def delete_adapter(model: _nn.Module, adapter_id: str):
    """
    Deletes adapters identified by ``adapter_id``, if they exist.

    Args:
        model (:py:class:`_nn.Module`): Top level model, which has been prepared for
            adaptation with a call to :py:func:`init`, from which adapters are to be deleted.
        adapter_id (:obj:`str`): The unique identifier for the adapter(s) being
          deleted.
    """
    _apply_to_submodules(model, "delete_adapter", adapter_id)


def freeze_adapter(model: _nn.Module, adapter_id: str):
    """
    Freeze the parameters of the adapter(s) identified by ``adapter_id``.

    Args:
        model (:py:class:`_nn.Module`): Top level model with adapters to be frozen.
        adapter_id (:obj:`str`): The unique identifier for the
          adapter(s) being frozen.
    """
    _apply_to_submodules(model, "freeze_adapter", adapter_id)


def unfreeze_adapter(model: _nn.Module, adapter_id: str):
    """
    Make the parameters of the adapter(s) identified by ``adapter_id`` trainable.

    Args:
        model (:py:class:`_nn.Module`): Top level model with adapters to be un-frozen.
        adapter_id (:obj:`str`): The unique identifier for the adapter(s)
          being made trainable.
    """
    _apply_to_submodules(model, "unfreeze_adapter", adapter_id)


def set_active_adapter(model: _nn.Module, adapter_id: str):
    """
    Set the adapter already added to the layers as active adapter.
    All other adapters besides these are inactive and won't be used during
    model's forward pass.

    Args:
        model (:py:class:`_nn.Module`): Top level model with adapters to activated.
        adapter_id (:obj:`str`): The unique identifier for the adapter(s)
          to be activated.
    """
    # call layer API with replace False so that we can catch instances where multiple
    # adapters are being activated for the same layer.
    _apply_to_submodules(model, "set_active_adapter", adapter_id, replace=False)


def unset_active_adapter(model: _nn.Module, adapter_id: str):
    """
    Unset the active adapter with the given adapter_id from the adapted layers.

    Args:
        model (:py:class:`_nn.Module`): Top level model with adapters to activated.
        adapter_id (:obj:`str`): The unique identifier for the adapter(s)
          to be de-activated.
    """
    for mod in _get_adapted_layers(model):
        if mod.has_adapter(adapter_id):
            getattr(mod, "unset_active_adapter")()


def merge_adapter(model: _nn.Module, adapter_id: str):
    """
    Merge weights of adapter(s) with adapter_id into the model,
    if the adapter supports merging.

    Args:
        model (:py:class:`_nn.Module`): Top level model with adapters to merged.
        adapter_id (:obj:`str`): The unique identifier for the adapter(s)
          to be merged.
    """
    _apply_to_submodules(model, "_merge_adapter", adapter_id)


def get_all_adapter_ids(model: _nn.Module) -> _List[str]:
    """
    Returns list of adapter ids of all unique adapters added to the model.

    Args:
        model (:py:class:`_nn.Module`): Top level model with adapters.
    """
    adapter_ids = set()
    for _, module in model.named_modules(remove_duplicate=True):
        if isinstance(module, _AdaptedLayer):
            adapter_ids.update(module.adapters.keys())
    return sorted(list(adapter_ids))


def get_all_active_adapter_ids(model: _nn.Module) -> _List[str]:
    """
    Returns list of adapter ids of all unique adapters added to the model,
    which are active.

    Args:
        model (:py:class:`_nn.Module`): Top level model with adapters.
    """
    adapter_ids = set()
    for _, module in model.named_modules(remove_duplicate=True):
        if isinstance(module, _AdaptedLayer) and module.active_adapter_id is not None:
            adapter_ids.add(module.active_adapter_id)
    return sorted(list(adapter_ids))


# pylint: disable=protected-access
def setup_adapter_extra_input_forwarding(
    model: _nn.Module, adapter_id: str, adapter_extra_inputs: _List[str]
):
    """
    Uses :py:class:`SharedContext` to enable extra inputs passed to this
    :py:class:`AdaptedModel` to be forwarded to adapters which consume
    these extra inputs.

    Args:
        model (:py:class:`_nn.Module`): Top level model with adapters.
        adapter_id (:obj:`str`): The unique identifier for the adapter
            for which input forwarding is established
        adapter_extra_inputs (:obj:`list` of :obj:`str`): A
            list of names of extra inputs passed to this :py:class:`AdaptedModel`
            which are forwarded to adapters which consume these extra inputs.
    """
    # remove any handles registered for previous active adapter
    if hasattr(model, "_adapter_extra_input_forwarding_handles"):
        for handle in model._adapter_input_forwarding_handles:
            handle.remove()

    context = _SharedContext()

    creation_handle = context.register_context_creation_hook(model)
    population_handle = context.register_context_population_hook(
        model, context.get_input_forwarding_hook(*adapter_extra_inputs)
    )
    deletion_handle = context.register_context_deletion_hook(model)
    model._adapter_extra_input_forwarding_handles = [
        creation_handle,
        population_handle,
        deletion_handle,
    ]

    for mod in _get_adapted_layers(model):
        if mod.has_adapter(adapter_id):
            adapter = mod.get_adapter(adapter_id)
            if isinstance(adapter, _AdapterWithExtraInputs):
                context.register_context_retrieval_hook(
                    adapter, *adapter.extra_input_names
                )


def _normalize_wrapped_key(key: str):
    ignore_key_substrs = [
        "._checkpoint_wrapped_module",
        "_fsdp_wrapped_module.",
        "._fsdp_wrapped_module",
        "_fsdp_module.",
    ]
    for ignore_substr in ignore_key_substrs:
        if ignore_substr in key:
            key = key.replace(ignore_substr, "")
    return key


def _create_base_module_state_dict(model: _nn.Module) -> _Dict[str, _Any]:
    """
    Helper function for creating state_dict which only contains
    state corresponding to the wrapped model.
    """
    state_dict = model.state_dict()
    for module_name, module in model.named_modules():
        if not isinstance(module, _AdaptedLayer):
            continue
        for key in module.state_dict():
            original_key = f"{module_name}.{key}"
            original_key = _normalize_wrapped_key(original_key)
            # when this is called in FSDP.state_dict_type context, non zero rank
            # processes might have empty dictionaries, hence we need to check for presence of
            # original_key in state_dict
            if key.startswith("adapters") and original_key in state_dict:
                state_dict.pop(original_key)
            else:
                unwrapped_key = module_name + key[len("wrapped") :]
                unwrapped_key = _normalize_wrapped_key(unwrapped_key)
                if original_key in state_dict:
                    state_dict[unwrapped_key] = state_dict.pop(original_key)
    return state_dict


def _create_adapter_only_state_dict(
    model: _nn.Module,
    adapter_ids: _Optional[_List[str]] = None,
) -> _Dict[str, _Any]:
    """
    Helper function for creating state_dict which only contains
    state corresponding to the adapters identified by ``adapter_ids``.
    """

    # remove all keys not corresponding to state of adapter_ids
    keys_to_retain = set()
    if adapter_ids is None:
        adapter_ids = get_all_adapter_ids(model)

    for module_name, module in model.named_modules():
        if not isinstance(module, _AdaptedLayer):
            continue

        for adapter_id in adapter_ids:
            if not module.has_adapter(adapter_id):
                continue
            for key, _ in module.state_dict().items():
                if key.startswith(f"adapters.{adapter_id}"):
                    original_key = f"{module_name}.{key}"
                    # state dict keys don't have checkpoint wrapping baked into them but
                    # module name does, so we need to account for that
                    original_key = _normalize_wrapped_key(original_key)
                    keys_to_retain.add(original_key)

    state_dict = model.state_dict()
    state_dict_keys = list(state_dict.keys())
    for key in state_dict_keys:
        if key not in keys_to_retain:
            state_dict.pop(key)

    return state_dict


def map_state_dict(
    model: _nn.Module,
    fmt=AdaptedModelStateDictFormat.FULL,
    adapter_ids: _Optional[_List[str]] = None,
):
    """
    Return a dictionary containing references to the whole state of the model.
    Provides functionality to retrieve state corresponding to
    just the wrapped model or the adapters.

    .. note::
       When :py:meth:`map_state_dict` is used for creating state dict for a model wrapped with
       :py:class:`torch.distributed.fsdp.FullyShardedDataParallel`, it should be called under the
       following context::

           from torch.distributed.fsdp import StateDictType

           save_policy = FullStateDictConfig(offload_to_cpu=True, rank0_only=True)
           with FullyShardedDataParallel.state_dict_type(
               model, StateDictType.FULL_STATE_DICT, save_policy
           ):
               adapter_sd = map_state_dict(model, fmt="adapter", adapter_ids=[...])
               base_sd = map_state_dict(model, fmt="base")

       It is also recommended to use ``use_orig_params=True`` with ``FullyShardedDataParallel``,
       otherwise, the generated state dicts from :py:meth:`map_state_dict` are not guaranteed to be
       correct.


    Args:
        model (:py:class:`_nn.Module`): Top level model with adapters.
        fmt (:obj:`AdaptedModelStateDictFormat`): Format for state_dict.
            The following values are allowed: 1) "full" - the entire state_dict
            is returned including keys for state of wrapped model and adapters
            2) "base" - only state corresponding to wrapped model is returned
            3) "adapter" - only state corresponding to adapters with
            ``adapter_ids`` is returned. Defaults to "full".
        adapter_ids (:obj:`list` of `str`, optional): Id(s) of adapter(s) whose
            state_dict is being loaded. This argument is requires when fmt is
            "adapter".
    """
    fmt = _helpers.get_enum_member_from_name(AdaptedModelStateDictFormat, fmt)
    if fmt is AdaptedModelStateDictFormat.FULL:
        return model.state_dict()
    if fmt is AdaptedModelStateDictFormat.BASE:
        return _create_base_module_state_dict(model)
    # if fmt is AdaptedModelStateDictFormat.ADAPTER
    return _create_adapter_only_state_dict(model, adapter_ids)


def _partial_load_state_dict_helper(
    model: _nn.Module,
    args: _Any,
    kwargs: _Any,
    state_dict: _Dict[str, _Any],
    expected_keys: _Set[str],
    strict: bool,
) -> _IncompatibleKeys:
    """
    Helper function for loading a partial state_dict generated
    from :py:meth:`state_dict` which either only contains state
    corresponding to the wrapped model or to one of the adapters.
    """
    error_msgs = []

    kwargs["strict"] = False

    partial_unexpected_keys = [key for key in state_dict if key not in expected_keys]

    # remove unexpected keys from state_dict because they can be adapter or base model
    # keys which would load fine in the model, but we do not want them to be loaded
    filtered_state_dict = {
        key: state_dict[key] for key in expected_keys if key in state_dict
    }

    result = model.load_state_dict(filtered_state_dict, *args, **kwargs)

    missing_keys = set(result.missing_keys)
    missing_keys = {_normalize_wrapped_key(key) for key in missing_keys}
    partial_missing_keys = [key for key in missing_keys if key in expected_keys]

    if strict:
        if len(partial_unexpected_keys) > 0:
            unexpected_keys_str = ", ".join(f'"{k}"' for k in partial_unexpected_keys)
            error_msgs.insert(
                0, f"Unexpected key(s) in state_dict: {unexpected_keys_str}. "
            )
        if len(partial_missing_keys) > 0:
            missing_keys_str = ", ".join(f'"{k}"' for k in partial_missing_keys)
            error_msgs.insert(0, f"Missing key(s) in state_dict: {missing_keys_str}. ")

    if len(error_msgs) > 0:
        raise RuntimeError(
            "Error(s) in loading state_dict for {}:\n\t{}".format(
                model.__class__.__name__, "\n\t".join(error_msgs)
            )
        )
    return _IncompatibleKeys(partial_missing_keys, partial_unexpected_keys)


def load_state_dict(
    model: _nn.Module,
    state_dict,
    *args,
    fmt=AdaptedModelStateDictFormat.FULL,
    adapter_ids: _Optional[_List[str]] = None,
    **kwargs,
):
    """
    Copies parameters from ``state_dict`` into the model. This method supports
    loading state dicts with or without adapters.

    Args:
        model (:py:class:`_nn.Module`): Top level model with adapters.
        state_dict (:obj:`dict`): The state dict to load.
        args: Variable arguments to forward to the base :meth:`load_state_dict`
            method.
        kwargs: Keyword arguments to forward to the base :meth:`load_state_dict`
            method.
        fmt (:obj:`AdaptedModelStateDictFormat`): Format for state_dict being loaded
            The following values are allowed: 1) "full" - state_dict contains
            the entire state of wrapped model and adapters 2) "base" - state_dict
            contains only state corresponding to wrapped model 3) "adapter" -
            state_dict contains only state corresponding to adapters with
            ``adapter_ids``. Defaults to "full". Defaults to "base".
        adapter_ids (:obj:`list` of `str`, optional): Id(s) of adapter(s) whose
            state_dict is being loaded. This argument is required when
            fmt is "adapter".
    """
    strict = kwargs.get("strict", True)
    fmt = _helpers.get_enum_member_from_name(AdaptedModelStateDictFormat, fmt)
    current_state_dict = map_state_dict(model, fmt=fmt, adapter_ids=adapter_ids)

    if _is_v0_lora_state_dict(state_dict):
        _warnings.warn(
            "Found state dict in v0 format. v0 adapters are deprecated, and "
            "support will be removed in a future tamm version.",
            category=DeprecationWarning,
        )
        state_dict = _maybe_rekey_v0_key(
            v1_state_dict=current_state_dict, v0_state_dict=state_dict
        )
    state_dict = _maybe_rekey_state_dict(model, state_dict)

    if fmt is AdaptedModelStateDictFormat.FULL:
        result = model.load_state_dict(state_dict, *args, **kwargs)
    elif fmt is AdaptedModelStateDictFormat.BASE:
        base_state_dict = _maybe_rekey_state_dict(model, current_state_dict)
        result = _partial_load_state_dict_helper(
            model, args, kwargs, state_dict, set(base_state_dict), strict
        )
    else:  # elif fmt is AdaptedModelStateDictFormat.ADAPTER
        if adapter_ids is None:
            raise ValueError(
                "adapter_id cannot be None when state_dict() is in ADAPTER mode"
            )
        for adapter_id in adapter_ids:
            if not has_adapter(model, adapter_id):
                raise RuntimeError(
                    f"Cannot find adapter with id: {adapter_ids}. state_dict "
                    f"cannot be loaded."
                )

        result = _partial_load_state_dict_helper(
            model, args, kwargs, state_dict, set(current_state_dict), strict
        )

    return result
