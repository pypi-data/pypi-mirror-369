import logging as _logging
from os import PathLike as _PathLike
from typing import Union as _Union

import torch as _torch

from tamm import _helpers
from tamm.converters.models import common as _common
from tamm.converters.models import registry as _registry
from tamm.typing import OptionalDtypeOrString as _OptionalDtypeOrString
from tamm.typing import StateDictType as _StateDictType

_logger = _logging.getLogger(__name__)


def convert_from_tamm_state_dict(
    state_dict: _StateDictType, converter: _Union[str, _common.ModelStateDictConverter]
) -> _StateDictType:
    """
    Converts a tamm state dict to another format.

    Args:
        state_dict (:obj:`StateDictType`): A state dict for a tamm model.
        converter (:obj:`str` or :obj:`.ModelStateDictConverter`, optional): A converter
            id or converter instance for converting ``obj`` to a different format.

    Returns:
        :obj:``StateDictType``: The converted state dict.
    """
    if not isinstance(converter, _common.ModelStateDictConverter):
        converter = _registry.create_converter_from_tamm_state_dict(
            converter, state_dict
        )
    _logger.info(
        f"Converting tamm state dict to new format with {converter.__class__.__name__}."
    )
    return converter.convert_from_tamm(state_dict)


def save(
    state_dict: _StateDictType,
    f: _Union[str, _PathLike],
    *,
    converter: _Union[str, _common.ModelStateDictConverter] = None,
    dtype: _OptionalDtypeOrString = None,
    **kwargs,
):
    """
    Saves a tamm state dict to a converted format on disk.

    Args:
        state_dict (:obj:`StateDictType`): A state dict for a tamm model, which maps
            parameter names to parameter values.
        f (:obj:`str` or :obj:`PathLike`): The filepath for saving the converted state.
        converter (:obj:`str` or :obj:`.ModelStateDictConverter`, optional): A converter
            id or converter instance for converting ``obj`` to a non-tamm format.  This
            value is ``None`` by default, in which case this function behaves like
            :func:`torch.save` .  Use :func:`tamm.list_converters` or
            ``tamm ls converters -l`` for a list of available converter ids.
        dtype (:obj:`torch.dtype` or :obj:`str`, optional): Output dtype, such as
            ``float16``, ``float32``, etc.  Before converting ``state_dict`` to the
            other format, the function casts the floating point tensors to this dtype.
            The default is ``None``, which results in no cast.
        **kwargs: Keyword arguments to forward to the :meth:`save_other_state_dict`
            method of the converter.
    """
    _helpers.maybe_cast_state_dict_(state_dict, dtype=dtype)

    if converter is None:
        _torch.save(state_dict, f, **kwargs)
        _logger.info(f"Saved tamm state dict to {f} without conversion.")
        return

    if not isinstance(converter, _common.ModelStateDictConverter):
        converter = _registry.create_converter_from_tamm_state_dict(
            converter, state_dict
        )
    state_dict = convert_from_tamm_state_dict(state_dict, converter=converter)
    _logger.info(f"Saving converted state to {f}.")
    converter.save_other_state_dict(state_dict, f, **kwargs)
