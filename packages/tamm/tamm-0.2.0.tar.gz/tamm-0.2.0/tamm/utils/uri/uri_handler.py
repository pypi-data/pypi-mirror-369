import importlib as _importlib
import logging as _logging
from collections import defaultdict
from pathlib import Path as _Path
from typing import Any as _Any
from typing import List as _List
from typing import Mapping as _Mapping
from typing import Type as _Type

from tamm._plugin import discover_and_retrieve_plugins
from tamm.runtime_configuration import rc as _rc
from tamm.utils.uri._protocol import BaseURLHandler

_logger = _logging.getLogger(__name__)


def is_uri_or_posix(uri: str) -> bool:
    return _is_uri(uri) or _Path(uri).is_file()


def _is_uri(model_identifier: _Any):
    if not isinstance(model_identifier, str):
        return False
    return "://" in model_identifier


def _is_json_file(model_identifier: str):
    _path = _Path(model_identifier)
    return _path.suffix.lower() == ".json"


def _discover_plugin_uri_handlers():
    available_uri_handlers = {}
    for plugin, module_name in discover_and_retrieve_plugins().items():
        try:
            plugin_uri_module = _importlib.import_module(".utils.uri", module_name)
            new_handlers = {
                f"{module_name}:{handler.name}": handler
                for handler in plugin_uri_module.available_handlers
            }
            _logger.debug("Registering %s to available URI handlers", new_handlers)
            available_uri_handlers.update(new_handlers)
        except (ImportError, ModuleNotFoundError, AttributeError) as e:
            _logger.debug(
                "Plugin %s does not have any valid uri handlers: %s", plugin, e
            )
    return available_uri_handlers


class DiscoveredURIHandlers:
    def __init__(self, handlers: _Mapping[str, _Type["BaseURLHandler"]]):
        discovered_handlers: _Mapping[str, _List[str]] = defaultdict(list)
        for full_name in handlers.keys():
            base_name = full_name.split(":", maxsplit=2)[1]
            discovered_handlers[base_name].append(full_name)
        for base_name, full_names in discovered_handlers.items():
            if len(full_names) > 1:
                raise ValueError(
                    f"URI Handler named '{base_name}' is redefined multiple times in different plugins: {full_names}. "
                    "Uninstall one of the plugins or request plugin owners to resolve naming conflict"
                )

        self.base_name_to_namespaced_name = {
            k: v[0] for k, v in discovered_handlers.items()
        }
        self._handlers = handlers

    def __getitem__(self, item) -> _Type["BaseURLHandler"]:
        if item.lower() == "auto":
            try:
                return self._get_uri_handler(_rc.uri_handler)
            except KeyError as e:
                raise KeyError(
                    f"'auto' URI handler is set, but rc.uri_handler={_rc.uri_handler} does not exist"
                ) from e
        try:
            return self._get_uri_handler(item)
        except KeyError as e:
            raise KeyError(f"URI handler {item} does not exist") from e

    def _get_uri_handler(self, name: str) -> _Type["BaseURLHandler"]:
        try:
            return self._handlers[self.base_name_to_namespaced_name[name]]
        except KeyError:
            return self._handlers[name]

    @classmethod
    def discover(cls):
        return cls(_discover_plugin_uri_handlers())


# pylint: disable-next=invalid-name
def _URIHandler(*args, backend: str = "auto", **kwargs):
    """
    URI handler facade to determine which specific URI Handler to use based on the
    environment

    Args:
        backend: "auto", specific URI handler names by '<plugin_name>:<handler_name>' or '<handler_name>'
    """
    discovered_handlers = DiscoveredURIHandlers.discover()
    handler = discovered_handlers[backend]
    return handler(*args, **kwargs)
