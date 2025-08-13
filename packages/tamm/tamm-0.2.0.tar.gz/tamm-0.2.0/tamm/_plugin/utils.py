"""
Utilities for discovering and potentially importing plugins for |tamm|.
"""
import importlib
import logging as _logging
import sys
from typing import Any as _Any
from typing import Dict as _Dict

from tamm.context_vars import _plugin_init
from tamm.runtime_configuration import rc

if sys.version_info < (3, 10):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


_logger = _logging.getLogger(__name__)


def execute_plugin_object_reference(object_ref: str, *, call_obj: bool = True) -> _Any:
    """
    Imports a plugin submodule/object and optionally calls it.

    Args:
        object_ref (:obj:`str`): A string of the format ``importable.module`` or
            ``importable.module:object.attr``.
        call_obj (:obj:`bool`): A flag that controls calling the referenced object.
            If the object is not callable, the flag has no effect.  Defaults to
            ``True``.

    Returns:
        The result of the object call if it is called, otherwise the object itself.
    """

    try:
        modname, separator, qualname = object_ref.partition(":")
        root_modname = modname.split(".", maxsplit=1)[0]

        with _plugin_init.plugin_initialization_context(root_modname):
            _logger.debug(f"Importing plugin module {modname}")
            obj = importlib.import_module(modname)
            _logger.debug(f"{modname} import complete")

            if separator:
                for attr in qualname.split("."):
                    obj = getattr(obj, attr)

            if call_obj and callable(obj):
                _logger.debug(f"Calling plugin object reference {object_ref}")
                result = obj()
                _logger.debug(f"{object_ref} call complete")
                return result

            return obj

    except Exception as e:
        _logger.debug(f"Caught exception during {object_ref} plugin handling: {e}")

    return None


def discover_plugin_extras(extras_name: str) -> importlib_metadata.EntryPoints:
    """
    Retrieves an iterable of entrypoints for a type of plugin extra.

    Args:
        extras_name: The entrypoint name for the extras.
    """
    return importlib_metadata.entry_points(
        name=extras_name, group=rc.PLUGINS_EXTRAS_ENTRYPOINT_GROUP
    )


def discover_and_retrieve_plugins() -> _Dict[str, str]:
    """
    Discovers plugin by entrypoints mechanism:
    https://packaging.python.org/en/latest/specifications/entry-points/

    All plugins with the plugins entrypoint group name with be discovered and
    returned.

    Returns:
        (:obj:`_Dict[str, str]`): Discovered plugins dictionary of the format
        ```
        {
            "plugin-name": "plugin_module"
        }
        ```
    """

    plugins: _Dict[str, str] = {}

    discovered_plugins = importlib_metadata.entry_points(
        group=rc.PLUGINS_ENTRYPOINT_GROUP
    )

    for plugin in discovered_plugins:
        plugins[plugin.name] = plugin.value
    return plugins


def import_named_plugin(plugin_module_name: str) -> None:
    """
    Import the specified plugin module.

    Args:
        plugin_module_name (:obj:`str`): plugin module to
            import a specific plugin.

    Raises:
        ValueError: If the plugin module name is not a string or not installed.
        ImportError: If there is an exception importing the plugin module.
    """

    if not isinstance(plugin_module_name, str):
        raise ValueError(
            f"plugin_module must be a str, got "
            f"type({type(plugin_module_name).__name__})"
        )

    plugins = discover_and_retrieve_plugins()
    if plugin_module_name not in plugins.values():
        raise ValueError(
            f"{plugin_module_name} is not in the list of installed plugins. "
            f"Ensure {plugin_module_name} plugin is installed."
        )
    try:
        importlib.import_module(plugin_module_name)
        _logger.debug(f"Successfully imported {plugin_module_name}.")
    except ImportError as e:
        raise ImportError(
            f"'{plugin_module_name}' is discovered but cannot be imported by tamm"
        ) from e


def import_discovered_plugins() -> None:
    """
    Retrieves plugins and attempts runtime import of all discovered plugins.

    Raises:
        ImportError: If there is an exception importing any plugin module.
    """

    plugins = discover_and_retrieve_plugins()

    for plugin_name, plugin_module in plugins.items():
        try:
            import_named_plugin(plugin_module)
        except (ImportError, ValueError) as e:
            _logger.debug("%s", e)
        except Exception as e:
            _logger.debug(
                "unknown exception occurred when importing plugin %s (%s). "
                "tamm will proceed anyways, please inform plugin owner and/or tamm team about this error: %s",
                plugin_name,
                plugin_module,
                str(e),
            )
