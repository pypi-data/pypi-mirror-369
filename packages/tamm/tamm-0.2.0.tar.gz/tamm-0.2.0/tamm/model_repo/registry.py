import logging as _logging
from functools import lru_cache as _lru_cache
from typing import Dict as _Dict
from typing import Optional as _Optional

from tamm import utils as _utils
from tamm.model_repo.model_repo import BaseModelRepo as _BaseModelRepo
from tamm.model_repo.publishing import PublishedModelConfig as _PublishedModelConfig

_logger = _logging.getLogger(__name__)


class RegistryModelRepo(_BaseModelRepo):
    """
    Deprecated model registry in which model configs are defined within the
    |tamm| package source.
    """

    _MODEL_CONFIG_REGISTRY = _utils.registry.Registry("Model Configs")

    def is_alive(self) -> bool:
        return True

    @_lru_cache
    def _get_configs_impl(self) -> _Dict[str, "_PublishedModelConfig"]:
        raw_configs = [
            self._MODEL_CONFIG_REGISTRY.create(config_name)
            for config_name in self._MODEL_CONFIG_REGISTRY.list()
        ]
        configs = {config.model_id: config for config in raw_configs}
        return configs

    @classmethod
    def register_model_config(
        cls,
        factory_fn=None,
        name: _Optional[str] = None,
        description: _Optional[str] = None,
    ):
        return cls._MODEL_CONFIG_REGISTRY.register(
            factory_fn, key=name, description=description
        )

    def clear_cache(self):
        ...
