import dataclasses

import torch.nn as _nn

from tamm.runtime_configuration import rc as _rc
from tamm.utils.optional_bool import OptionalBool


def init_marker(module: _nn.Module, overwrite=False):
    """
    Attaches default module marker to a ``nn.Module``. No-op if ``module`` already
    has an attribute named :py:obj:`tamm.rc.constants.MARKER_ATTRIBUTE`, unless
    ``overwrite=True``

    Args:
        module (:obj:`nn.Module`): Any ``nn.Module``
        overwrite: Force overwrite if ``True``

    """
    if overwrite or not hasattr(module, _rc.MARKER_ATTRIBUTE):
        setattr(module, _rc.MARKER_ATTRIBUTE, ModuleMarker())


def update_marker(module: _nn.Module, **attributes):
    """
    'Upserts' a dictionary of ``attributes`` to a ``nn.Module``.
    If ``module`` does not have an attribute named
    :py:obj:`tamm.rc.constants.MARKER_ATTRIBUTE`, the attribute will be created
    before updating

    Args:
        module (:obj:`nn.Module`): Any ``nn.Module``
        **attributes: Keyword markers to upsert.
            Must be :class:`ModuleMarker` attributes

    Returns: None
    """
    init_marker(module, overwrite=False)
    new_attributes = dataclasses.replace(
        getattr(module, _rc.MARKER_ATTRIBUTE), **attributes
    )
    setattr(module, _rc.MARKER_ATTRIBUTE, new_attributes)


def get_marker(module: _nn.Module) -> "ModuleMarker":
    """
    Reads extra markers from a ``nn.Module``.

    Raises ``AttributeError`` if ``module`` does not have extra markers

    Args:
        module (:obj:`nn.Module`): Any ``nn.Module``

    Returns: :class:`ModuleMarker`
    """
    init_marker(module, overwrite=False)
    return getattr(module, _rc.MARKER_ATTRIBUTE)


@dataclasses.dataclass
class ModuleMarker:
    """
    A dataclass which can be optionally attached to a ``nn.Module`` as an attribute
    named :py:obj:`tamm.rc.constants.MARKER_ATTRIBUTE`

    .. tip::

        Use :meth:`update_marker`, :meth:`init_marker` and :meth:`get_marker` to
        interact with the attribute.

    """

    freeze_params_hook_applied: "OptionalBool" = OptionalBool.NOTSET
    """
    Indicates whether builder has applied the 'freeze parameters' post hook to the
    module
    """

    weights_initialized: "bool" = False
    """
    Indicates whether a submodule has already initialized its weights.
    """

    def __post_init__(self):
        self.freeze_params_hook_applied = OptionalBool(self.freeze_params_hook_applied)
