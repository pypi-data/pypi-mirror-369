import contextlib as _contextlib
from contextvars import ContextVar
from typing import Union

from tamm.utils.optional_bool import OptionalBool

pretrained = ContextVar("pretrained", default=OptionalBool.FALSE)


def get_default_pretrained_flag():
    """
    ``.create_builder()`` of each configurable module will use the return value to
    resolve whether to load pretrained weights, *if* invoked without an explict
    Boolean value (i.e., ``None``, or ``OptionalBool.NOTSET``).

    Default value is ``False``
    """
    return pretrained.get()


def set_default_pretrained_flag(value: Union[bool, OptionalBool]):
    """
    Sets |tamm| global ``pretrained`` value

    Args:
        value: True, False, OptionalBool.[TRUE, FALSE]
    """
    value = OptionalBool(value)
    if value not in {OptionalBool.TRUE, OptionalBool.FALSE}:
        raise ValueError(
            "pretrained can only be either 'OptionalBool.TRUE' or 'OptionalBool.FALSE'"
        )
    return pretrained.set(value)


@_contextlib.contextmanager
def pretrained_flag_context(value):
    """
    Context of |tamm| global ``pretrained``

    Example:

    .. code-block:: python

        with pretrained_flag_context(True):
            tamm.create_model(...) # pretrained=True not needed

    """
    token = set_default_pretrained_flag(value)
    try:
        yield
    finally:
        pretrained.reset(token)
