import dataclasses as _dataclasses
import logging as _logging
import warnings as _warnings

import torch.export as _torch_export

_logger = _logging.getLogger(__name__)


def torch_exportable_dataclass(cls):
    """
    A decorator that applies both ``@dataclasses.dataclass`` and
    ``@torch.export.register_dataclass``.  This is helpful for making dataclasses
    that are compatible with ``torch.export``.
    """

    cls = _dataclasses.dataclass(cls)

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")

        try:
            _torch_export.register_dataclass(cls)
        except AttributeError:
            # register_dataclass not available in some torch versions
            try:
                # pylint: disable=import-outside-toplevel,protected-access
                import torch._export.utils

                torch._export.utils.register_dataclass_as_pytree_node(cls)
            except Exception:
                _logger.debug("Could not register dataclass %s with torch.export", cls)

    return cls
