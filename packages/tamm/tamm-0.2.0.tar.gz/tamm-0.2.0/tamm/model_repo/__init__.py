"""
Model Repository
================

.. automodule:: tamm.model_repo.publishing

Backends
--------

.. autoclass:: tamm.model_repo.RegistryModelRepo
    :members:
    :show-inheritance:

Base Class
----------
.. automodule:: tamm.model_repo.model_repo
    :members:

API
---

.. autofunction:: tamm.model_repo.get_model_repo_lazy
.. autofunction:: tamm.model_repo.get_model_repo_eager

"""
from tamm.model_repo.api import (
    create_adapted_model,
    create_model,
    create_model_builder,
    create_model_config,
    get_model_repo_eager,
    get_model_repo_lazy,
    is_adapted_model_name,
    is_model_builder_name,
    is_model_config_name,
    is_model_name,
    list_adapted_models,
    list_available_lora_adapted_models,
    list_model_builders,
    list_model_configs,
    list_models,
)
from tamm.model_repo.model_repo import CompositeModelRepo
from tamm.model_repo.publishing import PublishedModelConfig
from tamm.model_repo.registry import RegistryModelRepo

__all__ = (
    "create_model",
    "create_model_config",
    "create_adapted_model",
    "create_model_builder",
    "list_model_configs",
    "is_model_config_name",
    "is_model_name",
    "is_adapted_model_name",
    "is_model_builder_name",
    "list_adapted_models",
    "list_available_lora_adapted_models",
    "list_model_builders",
    "list_models",
    "get_model_repo_lazy",
    "get_model_repo_eager",
    "RegistryModelRepo",
    "PublishedModelConfig",
    "CompositeModelRepo",
)
