from typing import Any as _Any
from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional

from tamm._plugin import import_discovered_plugins
from tamm.utils import registry as _registry

_REGISTRY = _registry.Registry("Model state dict converters")


def register_converter_cls(
    converter_cls, converter_id: str, description: _Optional[str] = None
):
    _REGISTRY.register(converter_cls, key=converter_id, description=description)


def get_converter_cls(converter_id: str) -> _Callable:
    """
    Retrieve the registered converter class from the registry based on the provided
    converter ID. Also discovers the converters from all installed plugins.
    """
    import_discovered_plugins()
    return _REGISTRY.get_factory_fn(converter_id)


def create_converter_from_tamm_state_dict(
    converter_id: str, state_dict: _Dict[str, _Any]
):
    converter_cls = get_converter_cls(converter_id)
    return converter_cls.from_tamm_state_dict(state_dict)


def create_converter_from_other_state_dict(
    converter_id: str, state_dict: _Dict[str, _Any]
):
    converter_cls = get_converter_cls(converter_id)
    return converter_cls.from_other_state_dict(state_dict)


def list_converters(
    include_descriptions: bool = False,
    filter_deprecated: _Optional[bool] = True,
) -> _List[str]:
    """
    List the registered converter IDs from all installed plugins.
    """
    import_discovered_plugins()  # Ensure all plugins are loaded before listing
    return _REGISTRY.list(
        include_descriptions=include_descriptions,
        filter_deprecated=filter_deprecated,
    )
