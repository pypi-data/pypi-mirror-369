import contextlib as _contextlib
from contextvars import ContextVar
from typing import Union

from tamm.utils.optional_bool import OptionalBool

freeze_params = ContextVar("freeze_params", default=OptionalBool.NOTSET)


def get_default_freeze_params_flag():
    """
    ``.create_builder()`` of each configurable module will use the return value to
    resolve whether to freeze parameters, *if* invoked without an explict
    Boolean value (i.e., ``None``, or ``OptionalBool.NOTSET``).

    Default value is ``False``
    """
    return freeze_params.get()


def set_default_freeze_params_flag(value: Union[bool, OptionalBool]):
    """
    Sets |tamm| global ``freeze_params`` value

    Args:
        value: True, False. None, OptionalBool.[TRUE, FALSE, NOTSET]
    """
    value = OptionalBool(value)
    return freeze_params.set(value)


@_contextlib.contextmanager
def freeze_params_flag_context(value):
    """
    Context of |tamm| global ``freeze_params``

    Example:

    .. code-block:: python

        with freeze_params_context(True):
            tamm.create_model(...) # freeze_params=True not needed

    """
    token = set_default_freeze_params_flag(value)
    try:
        yield
    finally:
        freeze_params.reset(token)
