"""
utils.transformers_utils
========================

This module implements utilities for working with Hugging Face checkpoints.

.. autofunction:: tamm.utils.transformers_utils.load_transformers_state_dict

.. autofunction:: tamm.utils.transformers_utils.save_transformers_state_dict

"""

import glob as _glob
import logging as _logging
import os as _os
import shutil as _shutil
import tempfile as _tempfile
from typing import Generator as _Generator

import torch as _torch

from tamm import _helpers
from tamm.typing import OptionalDeviceOrString as _OptionalDeviceOrString
from tamm.typing import PathLike as _PathLike
from tamm.typing import StateDictType as _StateDictType
from tamm.utils import user_dir_utils as _user_dir_utils

_logger = _logging.getLogger(__name__)


def load_transformers_state_dict(
    checkpoint_dir: _PathLike, *, device: _OptionalDeviceOrString = None
) -> _StateDictType:
    """
    Loads model state saved by :meth:`PreTrainedModel.save_pretrained` from
    ``transformers``.  This only loads the model's state dict, not its config.
    It supports ``torch`` native and ``safetensors`` formats as well as sharded
    checkpoints.

    Args:
        checkpoint_dir (:obj:`PathLike`): The local checkpoint directory containing
            the serialized model state.
        device (:obj:`str` or :obj:`torch.device`, optional): The target device for the
            loaded tensors.

    Returns:
        A :obj:`dict` that maps tensor names to loaded tensors.
    """
    state_dicts = list(_load_transformers_state_dicts(checkpoint_dir, device=device))
    return _helpers.merge_dicts(*state_dicts)


def _load_transformers_state_dicts(
    checkpoint_dir: _PathLike,
    *,
    device: _OptionalDeviceOrString = None,
    weights_only: bool = True,
) -> _Generator[_StateDictType, None, None]:
    """
    Generates a sequence of loaded state dicts from ``checkpoint_dir``, one for each
    shard in the checkpoint.
    """
    checkpoint_dir = _helpers.get_expanded_abspath(checkpoint_dir)
    for path in _get_native_torch_model_paths(checkpoint_dir):
        yield _load_native_torch(path, device=device, weights_only=weights_only)
    for path in _get_safetensors_model_paths(checkpoint_dir):
        yield _load_safetensors(path, device=device)


def _load_native_torch(
    path: _PathLike,
    *,
    device: _OptionalDeviceOrString = None,
    weights_only: bool = True,
) -> _StateDictType:
    _logger.info("Loading %s", path)
    return _torch.load(path, weights_only=weights_only, map_location=device)


def _load_safetensors(
    path: _PathLike, *, device: _OptionalDeviceOrString = None
) -> _StateDictType:
    import safetensors.torch  # pylint: disable=import-outside-toplevel

    _logger.info("Loading %s", path)
    if device is not None:
        device = _torch.device(device).type  # safetensors errors out if not for this
    return safetensors.torch.load_file(path, device=device)


def _get_native_torch_model_paths(checkpoint_dir):
    pattern = _os.path.join(checkpoint_dir, "pytorch_model*.bin")
    return _glob.glob(pattern)


def _get_safetensors_model_paths(checkpoint_dir):
    pattern = _os.path.join(checkpoint_dir, "model*.safetensors")
    return _glob.glob(pattern)


def _get_all_model_paths(checkpoint_dir):
    paths1 = _get_native_torch_model_paths(checkpoint_dir)
    paths2 = _get_safetensors_model_paths(checkpoint_dir)

    pattern = _os.path.join(checkpoint_dir, "*model*.index.json")
    paths3 = _glob.glob(pattern)

    return paths1 + paths2 + paths3


def save_transformers_state_dict(
    state_dict: _StateDictType,
    checkpoint_dir: _PathLike,
    max_shard_size="5GB",
    **kwargs,
) -> None:
    """
    Saves a model's state dict in Hugging Face format.  This only saves the state dict,
    not the model's config, tokenizer, etc.

    Args:
        state_dict (:obj:`dict`): A state dictionary returned by
            :meth:`nn.Module.state_dict`.
        checkpoint_dir (:obj:`PathLike`): The target directory for saving the state.
        max_shard_size (:obj:`str`, optional): The ``max_shard_size`` argument for
            :meth:`PreTrainedModel.save_pretrained` from ``transformers``.  Defaults to
            ``"5GB"``.
        **kwargs: Additional keyword arguments for
            :meth:`PreTrainedModel.save_pretrained`.
    """
    checkpoint_dir = _helpers.get_expanded_abspath(checkpoint_dir)
    _logger.info("Saving to checkpoint to %s", checkpoint_dir)
    with _tempfile.TemporaryDirectory(
        dir=_user_dir_utils.get_tamm_tmp_dir()
    ) as temp_dir:
        dummy_model = _create_dummy_hf_model()
        dummy_model.save_pretrained(
            save_directory=temp_dir,
            state_dict=state_dict,
            max_shard_size=max_shard_size,
            **kwargs,
        )

        _os.makedirs(checkpoint_dir, exist_ok=True)
        for path in _get_all_model_paths(temp_dir):
            basename = _os.path.basename(path)
            dest = _os.path.join(checkpoint_dir, basename)
            _shutil.move(path, dest)


def _create_dummy_hf_model():
    """Creates and returns a small hf transformers model."""
    import transformers  # pylint: disable=import-outside-toplevel

    config = transformers.BertConfig(
        vocab_size=1,
        hidden_size=1,
        num_hidden_layers=1,
        num_attention_heads=1,
        intermediate_size=1,
        max_position_embeddings=1,
    )
    return transformers.BertModel(config)
