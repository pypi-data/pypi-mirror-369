import functools as _functools
import importlib
import logging
from typing import TYPE_CHECKING
from typing import Dict as _Dict
from typing import List as _List
from typing import Union as _Union

import torch.nn as _nn

from tamm import _warnings as _tamm_warnings
from tamm._plugin import discover_and_retrieve_plugins
from tamm.model_repo.file import FileModelRepo
from tamm.model_repo.model_repo import BaseModelRepo
from tamm.model_repo.uri_handler import URIHandlerModelRepo

if TYPE_CHECKING:
    from tamm.layers.common import LayerBuilder, ModuleConfig
logger = logging.getLogger(__name__)


@_functools.lru_cache(maxsize=1)
def get_model_repo_lazy(*args, **kwargs) -> "BaseModelRepo":
    """
    Creates model repo lazily by calling :py:func:`tamm.model_repo.utils.get_model_repo_eager`
    whenever it is first needed.

    .. note::
        This reduces side effects when ``import tamm`` is executed.
    """

    return get_model_repo_eager(*args, **kwargs)


def create_model(model_name: str, *args, **kwargs) -> "_nn.Module":
    """
    Create a model instance for the specified model name.

    Args:
        model_name (:obj:`str`): The name of the model to be created.
        *args: Additional positional arguments for model creation.
        **kwargs: Additional keyword arguments for model creation.

    Returns:
        :obj:`_nn.Module`: Created model instance.
    """
    return get_model_repo_lazy().create_model(model_name, *args, **kwargs)


def create_adapted_model(model_name: str, *args, **kwargs) -> "_nn.Module":
    """
    Similar to `create_model()` but accepts some additional LoRA options in
        ``**kwargs`` for backward compatibility.

    .. admonition:: Deprecation warning
        :class: warning

        This function is deprecated.  Please use `tamm.create_model` instead.

    Args:
        model_name (:obj:`str`): The name or identifier of the model to be created.
        *args: Additional positional arguments for model creation.
        **kwargs: Additional keyword arguments for model creation.

    Returns:
        :obj:`_nn.Module`: The created adapted model instance.
    """
    return get_model_repo_lazy().create_adapted_model(model_name, *args, **kwargs)


def create_model_builder(model_name: str, *args, **kwargs) -> "LayerBuilder":
    """
    Create a model builder for the specified model.

    Args:
        model_name (:obj:`str`): The name of the model for which the builder is to be
            created.
        *args: Additional positional arguments for builder creation.
        **kwargs: Additional keyword arguments for builder creation.

    Returns:
        :obj:`layer_common.LayerBuilder`: The created model builder instance.
    """
    return get_model_repo_lazy().create_model_builder(model_name, *args, **kwargs)


def create_model_config(model_name: str, *args, **kwargs) -> "ModuleConfig":
    """
    Create a model config for the given model name.

    Args:
        model_name (:obj:`str`): The name of the model for which config is to be
            created.
        *args: Additional positional arguments for config creation.
        **kwargs: Additional keyword arguments for config creation.

    Returns:
        :obj:`ModuleConfig`: Module config.
    """
    return get_model_repo_lazy().create_model_config(model_name, *args, **kwargs)


def list_adapted_models(
    include_descriptions=False, filter_deprecated=False
) -> _Union[_List[str], _Dict[str, str]]:
    """
    List available models and adapted models within tamm model repository.

    Args:
        include_descriptions (:obj:`bool`, optional): Whether to include
            descriptions for each model. Defaults to `False`.
        filter_deprecated (:obj:`bool`, optional): Whether to remove deprecated
            models from the list. Defaults to `False`.

    Returns:
        :obj:`Union[List[str], Dict[str, str]]`: A list of model and adapted model
            IDs if `include_descriptions` is `False`, otherwise a dictionary with
            model and adapted model IDs as keys and their descriptions as values.
    """
    return get_model_repo_lazy().list_adapted_models(
        include_descriptions=include_descriptions, filter_deprecated=filter_deprecated
    )


def list_model_builders(
    include_descriptions=False, filter_deprecated=False
) -> _Union[_List[str], _Dict[str, str]]:
    """
    List available model configs within tamm model repository.

    Args:
        include_descriptions (:obj:`bool`, optional): Whether to include
            descriptions for each model builder. Defaults to `False`.
        filter_deprecated (:obj:`bool`, optional): Whether to remove deprecated
            model builders from the list. Defaults to `False`.

    Returns:
        :obj:`Union[List[str], Dict[str, str]]`: A list of model IDs if
            `include_descriptions` is `False`, otherwise a dictionary with model IDs
             as keys and their descriptions as values.
    """
    return get_model_repo_lazy().list_model_builders(
        include_descriptions=include_descriptions, filter_deprecated=filter_deprecated
    )


def list_model_configs(
    include_descriptions=False, filter_deprecated=False
) -> _Union[_List[str], _Dict[str, str]]:
    """
    List available model configs within tamm model repository.

    Args:
        include_descriptions (:obj:`bool`, optional): Whether to include
            descriptions for each model builder. Defaults to `False`.
        filter_deprecated (:obj:`bool`, optional): Whether to remove deprecated
            model builders from the list. Defaults to `False`.

    Returns:
        :obj:`Union[List[str], Dict[str, str]]`: A list of model IDs if
            `include_descriptions` is `False`, otherwise a dictionary with model IDs
             as keys and their descriptions as values.
    """
    return get_model_repo_lazy().list_model_configs(
        include_descriptions=include_descriptions, filter_deprecated=filter_deprecated
    )


def list_models(
    include_descriptions=False, filter_deprecated=False
) -> _Union[_List[str], _Dict[str, str]]:
    """
    List available models within tamm model repository.

    Args:
        include_descriptions (:obj:`bool`, optional): Whether to include
            descriptions for each model. Defaults to `False`.
        filter_deprecated (:obj:`bool`, optional): Whether to remove deprecated
            models from the list. Defaults to `False`.

    Returns:
        Union[List[str], Dict[str, str]]: A list of model IDs if
            `include_descriptions` is `False`, otherwise a dictionary with model IDs
            as keys and their descriptions as values.
    """
    return get_model_repo_lazy().list_models(
        include_descriptions=include_descriptions, filter_deprecated=filter_deprecated
    )


def list_available_lora_adapted_models() -> _Dict[str, _Dict[int, str]]:
    """
    Retrieve the mapping from base model to all available adapted models within
    tamm model repository.
    Returns:
        Dict[str, Dict[int, str]]: A dictionary with base model IDs as keys and
            a dictionary as values, wich has adapter rank as the keys and
            adapter model IDs as values.
    """
    return get_model_repo_lazy().list_available_lora_adapted_models()


@_tamm_warnings.deprecate(alternative="tamm.create_model_config")
def is_model_name(model_name: str) -> bool:
    """
    Check if the given name is a valid model name.

    .. admonition:: New deprecation
        :class: warning

        This API is being deprecate and will be removed in ``tamm`` 1.0.
        Please use `tamm.create_model_config(...)` and catch ``KeyError`` instead.

    Args:
        model_name (:obj:`str`): The name to be checked.

    Returns:
        :obj:`bool`: `True` if the name is a valid model name, `False` otherwise.
    """
    return get_model_repo_lazy().is_model_name(model_name)


@_tamm_warnings.deprecate(alternative="tamm.create_model_config")
def is_adapted_model_name(model_name: str) -> bool:
    """
    Check if the given name is a valid model or adapted model name.

    .. admonition:: New deprecation
        :class: warning

        This API is being deprecate and will be removed in ``tamm`` 1.0.
        Please use `tamm.create_model_config(...)` and catch ``KeyError`` instead.

    Args:
        model_name (:obj:`str`): The model name to be checked.

    Returns:
        :obj:`bool`: `True` if the name is a valid adapted model name,
            `False` otherwise.
    """
    return get_model_repo_lazy().is_adapted_model_name(model_name)


@_tamm_warnings.deprecate(alternative="tamm.create_model_config")
def is_model_builder_name(model_builder_name: str) -> bool:
    """
    Check if the given name is a valid model builder name.

    .. admonition:: New deprecation
        :class: warning

        This API is being deprecate and will be removed in ``tamm`` 1.0.
        Please use `tamm.create_model_config(...)` and catch ``KeyError`` instead.

    Args:
        model_builder_name (:obj:`str`): The builder name to be checked.

    Returns:
        :obj:`bool`: `True` if the name is a valid model builder name,
            `False` otherwise.
    """
    return get_model_repo_lazy().is_model_builder_name(model_builder_name)


@_tamm_warnings.deprecate(alternative="tamm.create_model_config")
def is_model_config_name(model_config_name: str) -> bool:
    """
    Check if the given name is a valid model config name.

    .. admonition:: New deprecation
        :class: warning

        This API is being deprecate and will be removed in ``tamm`` 1.0.
        Please use `tamm.create_model_config(...)` and catch ``KeyError`` instead.

    Args:
        model_config_name (:obj:`str`): The config name to be checked.

    Returns:
        :obj:`bool`: `True` if the name is a valid model config name,
            `False` otherwise.
    """
    return get_model_repo_lazy().is_model_config_name(model_config_name)


def get_model_repo_eager(*args, **kwargs) -> "BaseModelRepo":
    """
    Get model repo based on current environment (env variables, plugins, and calling args)

    Returns a composition of

    1. tamm-core defined model repo (currently empty, i.e., :py:class:`tamm.model_repo.model_repo.PlaceholderModelRepo`)
    2. Plugin defined model repos

    The implementation is roughly equivalent to the following pseudo-code

    .. code-block::

        repo = get_tamm_core_defined_model_repo()

        for <plugin_name> in discover_all_plugin_module_names():
            guard [Continue for loop if the following lines failed due to known exceptions]

            from <plugin_name>.model_repo import get_model_repo
            extra_repo_defined_by_plugin = get_model_repo(*args, **kwargs)
            repo += extra_repo_defined_by_plugin

        return repo

    Returns:
        Composed model repo, including extended model repos defined by plugins

    """
    # model repo defined by the core package, currently a placeholder (nothing defined)
    repo = FileModelRepo(*args, **kwargs) + URIHandlerModelRepo(*args, **kwargs)

    for plugin_name, plugin_repo in discover_and_retrieve_plugins().items():
        try:
            logger.debug("Attempt to create model repo from plugin %s", plugin_name)
            extra_repo = importlib.import_module(
                ".model_repo", package=plugin_repo
            ).get_model_repo(*args, **kwargs)
            logger.debug("Plugin %s defines model repo %s", plugin_name, extra_repo)
            repo += extra_repo
        except (AttributeError, ModuleNotFoundError) as e:
            logger.debug(
                "Plugin %s does not extend model repo module: %s", plugin_name, e
            )
        except ImportError as e:
            logger.warning(
                "Plugin %s's model_repo cannot be imported. "
                "Models extended by plugin may not be accessible. "
                "export TAMM_LOG_LEVEL=debug to see debug info",
                plugin_name,
            )
            logger.debug("%s", e)
        except (TypeError, ValueError) as e:
            logger.warning(
                "Failed to compose model repo defined by plugin %s. "
                "Models extended by plugin may not be accessible. "
                "export TAMM_LOG_LEVEL=debug to see debug info",
                plugin_name,
            )
            logger.debug("%s", e)
        except Exception as e:
            # TODO: Now all exceptions are swallowed. Consider refactor model repo to raise error when
            #  a model expected from plugin-defined model repo fails to create. Also consider defining a
            #  new 'entry-point' (e.g., [project.entry-points.tamm.model_repo]) in package metadata to replace
            #  this trial and error discovery strategy.
            logger.warning(
                "Unhandled error occurred during discovery of model repo from plugin %s. "
                "Models extended by plugin may not be accessible. %s",
                plugin_name,
                e,
            )

    return repo
