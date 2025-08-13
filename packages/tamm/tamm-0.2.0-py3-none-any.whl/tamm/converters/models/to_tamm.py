import logging as _logging

import torch as _torch

from tamm import _helpers
from tamm.converters.models import common as _common
from tamm.converters.models import registry as _registry
from tamm.typing import OptionalDtypeOrString as _OptionalDtypeOrString

_logger = _logging.getLogger(__name__)


def convert_to_tamm_state_dict(state_dict, converter):
    """
    Converts a state dict from another format to tamm format.

    Args:
        state_dict (:obj:`dict`): A state dict to convert.
        converter (:obj:`str` or :obj:`.ModelStateDictConverter`, optional): A converter
            id or converter instance for converting ``obj`` to tamm format.

    Returns:
        The converted state dict in tamm format.
    """
    if not isinstance(converter, _common.ModelStateDictConverter):
        converter = _registry.create_converter_from_other_state_dict(
            converter, state_dict
        )
    _logger.info(
        "Converting state dict to tamm format with %s", converter.__class__.__name__
    )
    return converter.convert_to_tamm(state_dict)


def load(
    f,
    *,
    converter=None,
    dtype: _OptionalDtypeOrString = None,
    weights_only: bool = True,
    **kwargs,
):
    """
    Loads a model checkpoint and converts it to tamm format.

    Args:
        f (:obj:`str` or :obj:`PathLike`): The filepath to the model state to load.
        converter (:obj:`str` or :obj:`.ModelStateDictConverter`, optional): A converter
            id or converter instance for converting the loaded state to a tamm model
            state dict.  This value is ``None`` by default, in which case the function
            behaves like :func:`torch.load` .  Use :func:`tamm.list_converters` or
            ``tamm ls converters -l`` for a list of available converter ids.
        dtype (:obj:`torch.dtype` or :obj:`str`, optional): Output dtype, such as
            ``float16``, ``float32``, etc.  After converting the state to tamm format,
            the function casts the state's floating point tensors to this dtype.  The
            default is ``None``, which results in no cast.
        weights_only (:obj:`bool`): Indicates whether unpickler should be restricted to loading
            only tensors, primitive types, dictionaries and any types added via
            torch.serialization.add_safe_globals()
        **kwargs: Keyword arguments to forward to the :meth:`load_other_state_dict`
            method of the converter.

    Returns:
        The converted state dict in tamm format.
    """
    if converter is None:
        return _torch.load(f, weights_only=weights_only, **kwargs)

    if isinstance(converter, str):
        converter_cls = _registry.get_converter_cls(converter)
        _logger.info("Loading %s with converter %s", f, converter_cls.__name__)
        obj = converter_cls.load_other_state_dict(f, **kwargs)
        converter = converter_cls.from_other_state_dict(obj)
    else:
        _logger.info("Loading %s with converter %s", f, converter.__class__.__name__)
        obj = converter.load_other_state_dict(f, weights_only=weights_only, **kwargs)

    _logger.info("Converting state to tamm format")
    state = converter.convert_to_tamm(obj)
    _helpers.maybe_cast_state_dict_(state, dtype=dtype)
    return state
