import contextlib as _contextlib
from contextvars import ContextVar
from typing import Union

_INITIALIZING_PLUGIN_MODULE_NAME = ContextVar[Union[str, None]](
    "initializing_plugin_module_name", default=None
)


def get_initializing_plugin_module_name() -> Union[str, None]:
    """
    Returns the module name of the plugin that is currently initializing.
    Returns ``None`` if no plugin is currently initializing.
    """
    return _INITIALIZING_PLUGIN_MODULE_NAME.get()


@_contextlib.contextmanager
def plugin_initialization_context(module_name: str):
    """
    A context manager for initializing |tamm| plugins, which records the
    module name of the initializing plugin.

    Args:
        module_name (:obj:`str`): The module name of the initializing plugin.
    """
    token = _INITIALIZING_PLUGIN_MODULE_NAME.set(module_name)
    try:
        yield
    finally:
        _INITIALIZING_PLUGIN_MODULE_NAME.reset(token)
