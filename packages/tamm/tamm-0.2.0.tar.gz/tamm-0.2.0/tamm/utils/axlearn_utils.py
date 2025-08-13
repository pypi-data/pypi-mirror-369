"""
utils.axlearn_utils
===================

This module contains functions for loading and saving AXLearn model checkpoints.

.. autofunction:: tamm.utils.axlearn_utils.load_axlearn_state_dict

.. autofunction:: tamm.utils.axlearn_utils.save_axlearn_state_dict
"""

import collections as _collections
import json as _json
import logging as _logging
import os as _os
import re as _re

import torch as _torch

from tamm import _helpers
from tamm.typing import PathLike as _PathLike
from tamm.typing import StateDictType as _StateDictType

_logger = _logging.getLogger(__name__)

PRNG_KEY = "prng_key"


def load_axlearn_state_dict(
    checkpoint_dir: _PathLike, unstack_repeat_params: bool = True
) -> _StateDictType:
    """
    Loads model state from an AXLearn checkpoint directory.

    Args:
        checkpoint_dir (:obj:`str` or :obj:`PathLike`): The path to the AXLearn checkpoint.
            This should contain an ``index`` JSON file as well as a ``gda`` directory
            that contains parameter values.
        unstack_repeat_params (:obj:`bool`): Flag that when ``True``, transforms the
            result by mapping each parameter with ``"/repeat/"`` in its name to many
            new parameters. This happens by unstacking the parameter along its first
            dimension and by replacing ``"/repeat/"`` in the parameter name with
            ``f"/repeat_{idx}>/"``.

    Returns:
        The loaded model state as a :obj:`dict` that maps parameter names to PyTorch
        tensors.
    """
    _logger.debug("Loading axlearn state dict from %s", checkpoint_dir)
    checkpoint_dir = _get_last_step_dir(checkpoint_dir)
    index_path = _os.path.join(str(checkpoint_dir), "index")
    with open(index_path, "r", encoding="utf-8") as f:
        index = _json.load(f)
    param_paths = [el[0] for el in index if el[0].startswith("model")]
    state_dict = {}
    for param_path in param_paths:
        full_param_path = _os.path.join(str(checkpoint_dir), "gda", param_path)
        ts_tensor = _load_single_axlearn_param(full_param_path)
        tensor = _ts_tensor_to_torch_tensor(ts_tensor)
        state_dict[param_path] = tensor
    if unstack_repeat_params:
        state_dict = _unstack_repeat_params(state_dict)
    _logger.debug("Load complete")
    return state_dict


def _get_last_step_dir(checkpoint_dir):
    """
    AXLearn checkpoint dirs are structured like

    checkpoint_dir/step_00000000/index
    checkpoint_dir/step_00000000/gda/...
    checkpoint_dir/step_00000100/index
    checkpoint_dir/step_00000100/gda/...

    This function infers the path of the step dir with the largest index and returns it
    ("checkpoint_dir/step_100" in the example above).

    If checkpoint_dir already contains index and gda, the function assumes
    checkpoint_dir is the step dir and returns it.
    """
    contents = _os.listdir(checkpoint_dir)
    if "index" in contents and "gda" in contents:
        return checkpoint_dir

    step_indices_and_names = [
        (_get_step_idx_from_basename(name, default=-1), name) for name in contents
    ]
    max_step_idx, max_step_name = max(step_indices_and_names)
    if max_step_idx == -1:
        raise ValueError(
            f"{checkpoint_dir} not recognized as an axlearn checkpoint dir.  Expected it "
            "to contain either (1) a 'step_<step_idx>' subdir or (2) an 'index' file "
            "and 'gda' subdir."
        )
    return _os.path.join(checkpoint_dir, max_step_name)


def _get_step_idx_from_basename(basename: str, default=-1) -> int:
    """
    If basename is of the form "step_{idx}" for an int idx, this returns the idx (as
    an int). Otherwise, this returns ``default``.
    """
    step_idx_regex = _get_step_idx_regex()
    match = step_idx_regex.fullmatch(basename)
    if match is None:
        return default
    return int(match.group(1))


@_helpers.cache
def _get_step_idx_regex():
    return _re.compile(r"step_([\d]+)")


def save_axlearn_state_dict(
    state_dict: _StateDictType,
    checkpoint_dir: _PathLike,
    stack_repeat_params: bool = True,
) -> None:
    """
    Saves a model checkpoint in AXLearn format.

    Args:
        state_dict: A :obj:`dict` that maps parameter names to PyTorch tensors.  The
            names should be relative paths from the ``"gda"`` directory for saving
            each parameter.
        checkpoint_dir (:obj:`str` or :obj:`PathLike`): The path for saving the AXLearn
            checkpoint.
        stack_repeat_params (:obj:`bool`): Flag that when ``True``, transforms the
            result by consolidating parameters with identical names other than the
            layer index in ``"/repeat_<idx>/"``.  The consolidation stacks these
            parameters together and replaces ``"/repeat_<idx>/"`` with ``"/repeat/"``
            in the resulting parameter name.
    """
    _logger.debug("Saving axlearn state dict to %s", checkpoint_dir)
    _os.makedirs(checkpoint_dir, exist_ok=True)
    if stack_repeat_params:
        state_dict = _stack_repeat_params(state_dict)
    checkpoint_dir = _os.path.join(
        str(checkpoint_dir),
        f"step_{0:08d}",
        # Axlearn assumes 8 digits:
        # https://github.com/apple/axlearn/blob/main/axlearn/common/checkpointer.py#L60
    )
    index = [("step", 0)]
    for key, param in _get_state_dict_items(state_dict):
        if _torch.is_tensor(param):  # prng_key is already a numpy array
            param = _torch_tensor_to_ts_tensor(param)
        path = _os.path.join(checkpoint_dir, "gda", key)
        _save_single_axlearn_param(param, path)
        index.append((key, {"dtype": str(param.dtype.name), "shape": str(param.shape)}))
    index_path = _os.path.join(checkpoint_dir, "index")
    with open(index_path, "w", encoding="utf-8") as f:
        _json.dump(index, f)
    _logger.debug("Save complete")


def _torch_tensor_to_ts_tensor(tensor: _torch.Tensor):
    """
    Helper function to convert torch tensors to tensorstore arrays.  To do this, we
    first convert to numpy.  Since numpy does not support some low-precision dtypes, we
    first cast to fp64 and then later back to the original dtype.
    """
    import tensorstore  # pylint: disable=import-outside-toplevel,import-error

    dtype = _helpers.get_str_from_maybe_dtype(tensor.dtype)

    if _torch.is_floating_point(tensor):
        if "mps" in str(tensor.device):
            # Move to CPU because MPS doesn't support double
            tensor = tensor.cpu()
        tensor = tensor.double()
    np_tensor = tensor.numpy(force=True)

    return tensorstore.array(np_tensor).astype(getattr(tensorstore, dtype))


def _ts_tensor_to_torch_tensor(store) -> _torch.Tensor:
    """
    Helper function to convert tensorstores to torch tensors.  We go through numpy, but
    since numpy does not support some low-precision dtypes, we first cast to fp64 and
    later back to the original dtype.
    """
    dtype = store.dtype.name
    torch_dtype = _helpers.get_dtype_from_maybe_string(dtype)
    if "float" in dtype:
        store = store.astype("float64")
    np_tensor = store.read().result()
    return _torch.tensor(np_tensor, dtype=torch_dtype)


def _get_state_dict_items(state_dict):
    """
    Returns an iterable of state dict keys and values.  If prng_key is not already in
    the state_dict, the first item is a prng_key.
    """
    if PRNG_KEY not in state_dict:
        items = [(PRNG_KEY, _create_prng_key_value())]
        items.extend(state_dict.items())
        return items
    return state_dict.items()


def _create_prng_key_value():
    try:
        import numpy as np  # pylint: disable=import-outside-toplevel
    except ImportError:
        _logging.error(
            "Loading axlearn checkpoints requires numpy, but tamm could not import "
            "this package.  Please check your numpy installation."
        )
        raise

    return np.array(
        [1770346568, 1894082449, 1770346568, 1894082449],
        dtype=np.uint32,
        # arbitrary numbers that come from a prior axlearn checkpoint
    )


def _load_single_axlearn_param(path):
    _logger.debug("Loading axlearn param from %s", path)
    return _open_tensorstore(path)


def _save_single_axlearn_param(param, path):
    _logger.debug("Saving axlearn param to %s", path)
    store = _open_tensorstore(path, create=True, dtype=param.dtype, shape=param.shape)
    return store.write(param).result()


def _open_tensorstore(path, **kwargs):
    try:
        import tensorstore  # pylint: disable=import-outside-toplevel
    except ImportError:
        _logging.error(
            "Loading axlearn checkpoints requires tensorstore, but tamm could not import "
            "this package.  Please install tensorstore or check your tensorstore "
            "installation."
        )
        raise

    path = _helpers.get_expanded_abspath(path)  # required by tensorstore
    tensor_store_config = {
        "driver": "zarr",
        "kvstore": {"driver": "file", "path": str(path)},
    }
    return tensorstore.open(tensor_store_config, **kwargs).result()


def _unstack_repeat_params(axlearn_state_dict):
    result = {}
    for key, param in axlearn_state_dict.items():
        if "/repeat/" not in key:
            result[key] = param
            continue
        for idx, new_param in enumerate(param.unbind()):
            new_key = key.replace("/repeat/", f"/repeat_{idx}/")
            result[new_key] = new_param
    return result


def _stack_repeat_params(axlearn_state_dict):
    repeat_id_regex = _get_repeat_id_regex()
    key_to_layer_indices_and_params = _collections.defaultdict(list)
    result = {}
    for key, param in axlearn_state_dict.items():
        match = repeat_id_regex.search(key)
        if match is None:
            result[key] = param
            continue
        new_key = key.replace(match.group(), "/repeat/")
        layer_idx = int(match.group(1))
        key_to_layer_indices_and_params[new_key].append((layer_idx, param))
    for key, value in key_to_layer_indices_and_params.items():
        value.sort()
        indices, params = zip(*value)
        if indices != tuple(range(len(indices))):
            raise ValueError(
                "To stack repeat params, "
                f"expected indices of range({len(indices)}), but indices is {indices}"
            )

        params = [param for _, param in value]
        param = _torch.stack(params)
        result[key] = param
    return result


@_helpers.cache
def _get_repeat_id_regex():
    return _re.compile(r"/repeat_([\d]+)/")
