"""
This module implements the base converter type as well as some reusable components for
building converters of model state dicts.

"""

import abc as _abc
import logging as _logging
from typing import Optional as _Optional

import torch as _torch

from tamm.converters import common as _parent_common
from tamm.converters.models import registry as _registry
from tamm.typing import StateDictType as _StateDictType

_logger = _logging.getLogger(__name__)


class ModelStateDictConverter(_parent_common.StateDictConverter, _abc.ABC):
    """
    Interface for converting model state dicts.  Compared to the base
    :class:`StateDictConverter`, this class mainly adds methods for saving and loading
    model state.  This allows us to export to HuggingFace format, for example (for which
    must also save configs).  The class also adds :meth:`.from_tamm_state_dict` and
    :meth:`.from_other_state_dict`, which enable creation of converter instances by
    inferring the converter arguments from tensors and metadata in the state dict.
    """

    def __init_subclass__(cls, converter_id: _Optional[str] = None):
        """
        Recommended format for the converter_id is "{model-name}:{format}", using
        hyphen-separated (kebab) case for the model name and format.  For example,
        "deepseek:huggingface" converts a DeepSeek model to or from HuggingFace format.
        """
        if converter_id is None:
            return
        _registry.register_converter_cls(
            cls, converter_id=converter_id, description=cls.__doc__
        )

    def __init__(self, wrapped_converter):
        self._wrapped_converter = wrapped_converter

    def is_tamm_key(self, key: str) -> bool:
        return self._wrapped_converter.is_tamm_key(key)

    def is_other_key(self, key: str) -> bool:
        return self._wrapped_converter.is_other_key(key)

    def _convert_from_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        # pylint: disable-next=protected-access
        return self._wrapped_converter._convert_from_tamm_impl(state_dict)

    def _convert_to_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        # pylint: disable-next=protected-access
        return self._wrapped_converter._convert_to_tamm_impl(state_dict)

    @classmethod
    @_abc.abstractmethod
    def from_tamm_state_dict(cls, state_dict):
        """Returns an instance of the class, given a tamm state dict."""

    @classmethod
    @_abc.abstractmethod
    def from_other_state_dict(cls, state_dict):
        """Returns an instance of the class, given an "other" state dict."""

    @staticmethod
    def load_tamm_state_dict(filepath, weights_only: bool = True, **kwargs):
        """Load a tamm state dict from a file."""
        return _torch.load(filepath, weights_only=weights_only, **kwargs)

    @staticmethod
    def save_tamm_state_dict(state_dict, filepath, **kwargs):
        """Save a tamm state dict to a file."""
        _torch.save(state_dict, filepath, **kwargs)

    @staticmethod
    @_abc.abstractmethod
    def load_other_state_dict(filepath):
        """Load a non-tamm state dict from a file."""

    @staticmethod
    @_abc.abstractmethod
    def save_other_state_dict(state_dict, filepath):
        """Save a non-tamm state dict to a file."""


class TorchModelConverter(ModelStateDictConverter):
    """Converter for non-tamm Torch models that use PyTorch state dicts."""

    @staticmethod
    def load_other_state_dict(filepath, weights_only: bool = True):
        return _torch.load(filepath, weights_only=weights_only)

    @staticmethod
    def save_other_state_dict(state_dict, filepath):
        return _torch.save(state_dict, filepath)
