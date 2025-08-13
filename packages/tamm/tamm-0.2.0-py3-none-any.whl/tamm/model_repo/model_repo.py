import abc as _abc
import copy
import logging
import warnings as _warnings
from itertools import chain
from typing import TYPE_CHECKING
from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List
from typing import Mapping as _Mapping
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch.nn as _nn

from tamm import _adapters_v1
from tamm import _warnings as _tamm_warnings
from tamm.layers import common as layer_common
from tamm.model_repo._warning import _warn_deprecated_published_config
from tamm.model_repo.exceptions import UnrecognizedModelIdentifierError
from tamm.model_repo.publishing import PublishedModelConfig as _PublishedModelConfig

if TYPE_CHECKING:
    from tamm.models.common import ModuleConfig
logger = logging.getLogger(__name__)


_LORA_MODEL_ADAPTER_TYPES: _Tuple[_Any, ...] = (_adapters_v1.LoRAModelAdapter,)
_MULTI_LORA_MODEL_ADAPTER_TYPES: _Tuple[_Any, ...] = (
    _adapters_v1.MultiLoRAModelAdapter,
)


def _get_adapters_from_config(config: "ModuleConfig"):
    sub_modules = ["decoder", "image_tokenizer"]
    adapters = []
    for sub_module in sub_modules:
        if hasattr(config, sub_module):
            sub_module_adapters = _get_adapters_from_config(getattr(config, sub_module))
            if sub_module_adapters:
                adapters.extend(sub_module_adapters)
    if (
        hasattr(config, "adapters")
        and isinstance(config.adapters, dict)
        and len(config.adapters) > 0
    ):
        adapters.append(config.adapters)
    return adapters


def _get_lora_adapters(adapters):
    result = []
    if adapters is None:
        return result

    for adapter in adapters.values():
        if isinstance(adapter, _MULTI_LORA_MODEL_ADAPTER_TYPES):
            sub_adapters = _get_lora_adapters(adapter.lora_model_adapters)
            result.extend(sub_adapters)
        elif isinstance(adapter, _LORA_MODEL_ADAPTER_TYPES):
            result.append(adapter)

    return result


class BaseModelRepo(metaclass=_abc.ABCMeta):
    """
    Base class of all model repos, defines the common interface that must be implemented by concrete backends.
    """

    def __init__(self, *args, **kwargs):
        del args, kwargs

    @_abc.abstractmethod
    def _get_configs_impl(self) -> _Mapping[str, "_PublishedModelConfig"]:
        """
        Returns a mapping from model ids to PublishedModelConfig
        """
        raise NotImplementedError(
            "_get_configs_impl() must be implemented"
            " for concrete classes inherited from BaseModelRepo"
        )

    @_abc.abstractmethod
    def is_alive(self) -> bool:
        """
        Returns whether the model repo is ready to serve models
        """

    def _list_models(
        self,
        include_descriptions=False,
        filter_deprecated=False,
        exclude_adapted=True,
    ) -> _Union[_List[str], _Dict[str, str]]:
        """
        Returns a list of model ids that can be created by this repo
        """
        _configs = [
            config
            for config in self._get_configs(
                filter_deprecated=filter_deprecated
            ).values()
            if exclude_adapted ^ config.model_config.has_adapters
        ]

        if not include_descriptions:
            return [config.model_id for config in _configs]

        return {config.model_id: config.description for config in _configs}

    def list_models(
        self, include_descriptions: bool = False, filter_deprecated: bool = False
    ) -> _Union[_List[str], _Dict[str, str]]:
        """
        Returns a list of model ids that can be created by this repo
        """
        return self._list_models(
            include_descriptions=include_descriptions,
            filter_deprecated=filter_deprecated,
            exclude_adapted=True,
        )

    def list_adapted_models(
        self, include_descriptions=False, filter_deprecated=False
    ) -> _Union[_List[str], _Dict[str, str]]:
        return self._list_models(
            include_descriptions=include_descriptions,
            filter_deprecated=filter_deprecated,
            exclude_adapted=False,
        )

    def list_model_builders(self, include_descriptions=False, filter_deprecated=False):
        return self.list_model_configs(
            include_descriptions=include_descriptions,
            filter_deprecated=filter_deprecated,
        )

    def list_model_configs(
        self, include_descriptions=False, filter_deprecated=False
    ) -> _Union[_List[str], _Dict[str, str]]:
        """
        Returns a list of model ids that can be created by this repo
        """
        items = self._get_configs(filter_deprecated=filter_deprecated)
        if not include_descriptions:
            return [item.model_id for item in items.values()]
        return {item.model_id: item.description for item in items.values()}

    def list_available_lora_adapted_models(self) -> _Dict[str, _Dict[int, str]]:
        """
        Helper method to retrieve the mapping from base model to all
        available adapted model.
        """
        result: _Dict[str, _Dict[int, str]] = {}
        all_model_ids = sorted(set(self.list_adapted_models() + self.list_models()))  # type: ignore[operator]
        for model_id in all_model_ids:
            with _warnings.catch_warnings(record=True):
                config = self.create_model_config(model_id)
            backbone_id = config.metadata.source_model_details.get(
                "backbone_tamm_model_id", None
            )
            if backbone_id is None:
                continue
            adapters = _get_adapters_from_config(config)

            if adapters is None or len(adapters) != 1:
                continue
            adapter = list(adapters[0].values())[0]

            if not isinstance(adapter, _LORA_MODEL_ADAPTER_TYPES):
                continue
            group = result.setdefault(backbone_id, {})
            if adapter.rank in group:
                raise RuntimeError(
                    f"Multiple adapted models found for {backbone_id} rank {adapter.rank}"
                )
            group[adapter.rank] = model_id

        for backbone_id, group in result.items():
            result[backbone_id] = dict(sorted(group.items()))

        return result

    def create_adapted_model(self, model_name: str, *args, **kwargs) -> "_nn.Module":
        """
        Creates a new adapted model

        .. warning::

            :func:`create_adapted_model` is deprecated. Please use
            :func:`create_model` or :func:`create_model_config` instead.
        """
        _tamm_warnings.deprecation(
            "create_adapted_model() is deprecated.  Please use create_model() "
            "or create_model_config() instead."
        )
        # Separate LoRA options from **kwargs:
        lora_key_mapping = {
            "rank": "rank",
            "alpha": "alpha",
            "adapt_q": "adapt_attention_queries",
            "adapt_k": "adapt_attention_keys",
            "adapt_v": "adapt_attention_values",
            "lora_dropout_p": "dropout_p",
        }
        lora_options = {
            v: kwargs.pop(k) for k, v in lora_key_mapping.items() if k in kwargs
        }

        # Create config without LoRA options:
        model_config = self.create_model_config(model_name, **kwargs)

        # Update LoRA adapters:
        for adapter in _get_lora_adapters(model_config.adapters):
            for key, val in lora_options.items():
                setattr(adapter, key, val)

        return model_config.create_model(*args, **kwargs)

    def create_model_builder(
        self, model_name: str, *args, **kwargs
    ) -> "layer_common.LayerBuilder":
        """
        Creates a new model builder
        """
        config = self.create_model_config(model_name, *args, **kwargs)
        return config.create_builder(*args, **kwargs)

    def create_model(self, model_name: str, *args, **kwargs) -> "_nn.Module":
        # test-create basic model config solely from model_name, ignore kwargs to determine if this model is adapted
        config = self.create_model_config(model_name)
        if config.has_adapters:
            return self.create_adapted_model(model_name, *args, **kwargs)
        return config.create_model(*args, **kwargs)

    def create_model_config(self, model_name: str, *args, **kwargs) -> "ModuleConfig":
        try:
            published_config = self._get_configs_impl()[model_name]
        except KeyError as e:
            raise KeyError(
                f"Model '{model_name}' does not exist in '{self.__class__.__name__}'"
            ) from e
        _warn_deprecated_published_config(published_config)
        published_config = copy.deepcopy(published_config)
        published_config.model_config.update_configured_args(*args, **kwargs)
        return published_config.model_config

    def is_model_name(self, model_name: str) -> bool:
        return model_name in self.list_models()

    def is_adapted_model_name(self, model_name: str) -> bool:
        return model_name in self.list_adapted_models()

    def is_model_builder_name(self, model_builder_name: str) -> bool:
        return model_builder_name in self.list_model_builders()

    def is_model_config_name(self, model_config_name: str) -> bool:
        return model_config_name in self.list_model_configs()

    def _get_configs(
        self, filter_deprecated: bool = False
    ) -> _Dict[str, "_PublishedModelConfig"]:
        configs = self._get_configs_impl()
        if filter_deprecated:
            configs = {
                model_name: published_config
                for model_name, published_config in configs.items()
                if not published_config.is_deprecated
            }

        return dict(sorted(configs.items()))

    @_abc.abstractmethod
    def clear_cache(self):
        """
        Clear any local cache this model repo may have used
        """

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __add__(self, other: "BaseModelRepo"):
        """
        Model configs defined in any model repo will supersede model configs of the
        same model_id in model repo to its left.

        Args:
            other: ModelRepo

        Returns: Composite ModelRepo

        """
        return CompositeModelRepo(self, other)


class PlaceholderModelRepo(BaseModelRepo):
    """
    Placeholder model repo, contains no model definitions
    """

    def _get_configs_impl(self) -> _Mapping[str, "_PublishedModelConfig"]:
        return {}

    def is_alive(self) -> bool:
        return True

    def clear_cache(self) -> None:
        """
        No-op
        """


class CompositeModelRepo(BaseModelRepo):
    """
    Composite model repo which keeps tracks of many model repo instances and act like a union of all
    """

    def __init__(self, *repo_instances: "BaseModelRepo"):
        super().__init__(*repo_instances)
        self._repo_instances = repo_instances
        self._configs: _Dict[str, "_PublishedModelConfig"] = {}

    def _chained_iterator(self, method, *args, **kwargs):
        """
        Call each repo_instance's ``method`` with *args, anw **kwargs
        """
        return_values = [
            getattr(repo_instance, method)(*args, **kwargs)
            for repo_instance in self._repo_instances
        ]
        if any(isinstance(return_value, dict) for return_value in return_values):
            return {
                k: v for return_value in return_values for k, v in return_value.items()
            }
        return list(chain(*return_values))

    def _first_successful(self, method, *args, **kwargs):
        """
        Call each repo_instance's ``method`` with *args, anw **kwargs, return the first successful call
        """
        exceptions = []
        for repo_instance in self._repo_instances:
            try:
                return getattr(repo_instance, method)(*args, **kwargs)
            except Exception as e:
                exceptions.append(e)
                logger.debug(
                    "%s raised exception when calling %s(%s): %s",
                    repo_instance,
                    method,
                    args[0],
                    str(e),
                )
        # Raise the first meaningful exception from composite repo, UnrecognizedModelIdentifierError is
        # not meaningful because it basically means a model repo doesn't understand a specific URI schema.
        # However, if all model repos raise UnrecognizedModelIdentifierError we will still surface it to the user.
        if all(isinstance(e, UnrecognizedModelIdentifierError) for e in exceptions):
            raise next(e for e in exceptions)
        raise next(
            e for e in exceptions if not isinstance(e, UnrecognizedModelIdentifierError)
        )

    def create_model(self, model_name: str, *args, **kwargs) -> "_nn.Module":
        return self._first_successful("create_model", model_name, *args, **kwargs)

    def create_model_builder(
        self, model_name: str, *args, **kwargs
    ) -> "layer_common.LayerBuilder":
        return self._first_successful(
            "create_model_builder", model_name, *args, **kwargs
        )

    def create_adapted_model(self, model_name: str, *args, **kwargs) -> "_nn.Module":
        return self._first_successful(
            "create_adapted_model", model_name, *args, **kwargs
        )

    def create_model_config(self, model_name: str, *args, **kwargs) -> "ModuleConfig":
        return self._first_successful(
            "create_model_config", model_name, *args, **kwargs
        )

    def list_model_builders(self, *args, **kwargs):
        return self._chained_iterator("list_model_builders", *args, **kwargs)

    def list_model_configs(self, *args, **kwargs):
        return self._chained_iterator("list_model_configs", *args, **kwargs)

    def list_available_lora_adapted_models(self, *args, **kwargs):
        return self._chained_iterator(
            "list_available_lora_adapted_models", *args, **kwargs
        )

    def list_adapted_models(self, *args, **kwargs):
        return self._chained_iterator("list_adapted_models", *args, **kwargs)

    def list_models(self, *args, **kwargs):
        return self._chained_iterator("list_models", *args, **kwargs)

    def is_alive(self) -> bool:
        return all(repo.is_alive() for repo in self._repo_instances)

    def _get_configs_impl(self) -> _Dict[str, "_PublishedModelConfig"]:
        """
        When model repos are added for composition, for example,
        composite_model_repo = model_repo_a + model_repo_b

        model_repo_b's model config will supersede model_repo_a's model config if they
        share the same model_id. Any model repo in the addition will supersede
        model repo to its left.

        Returns: A dictionary mapping model_id->PublishedModelConfig instance

        """
        # pylint:disable=protected-access
        for repo in self._repo_instances:
            self._configs.update(repo._get_configs_impl())
        return self._configs

    def __repr__(self):
        repo_instances_str = ", ".join([str(repo) for repo in self._repo_instances])
        return f"{self.__class__.__name__}({repo_instances_str})"

    def clear_cache(self):
        for repo in self._repo_instances:
            repo.clear_cache()
