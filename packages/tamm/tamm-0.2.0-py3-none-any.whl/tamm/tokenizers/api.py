""" Defines a registry for tokenizers and provides utility functions for
creating, registering, listing, and validating tokenizers."""

import logging as _logging
from typing import Union as _Union

from tamm import _warnings as _tamm_warnings
from tamm._plugin import utils as plugin_utils
from tamm.runtime_configuration import rc
from tamm.tokenizers.common import PublishedTokenizerConfig, Tokenizer, TokenizerConfig
from tamm.tokenizers.registry import TokenizerRegistry, URIHandlerTokenizerRegistry

_logger = _logging.getLogger(__name__)


TokenizerSpecType = _Union[str, TokenizerConfig, PublishedTokenizerConfig, Tokenizer]


def get_tokenizer_registry() -> TokenizerRegistry:
    entrypoints = plugin_utils.discover_plugin_extras(
        rc.PLUGINS_EXTRAS_ENTRYPOINT_NAMES.tokenizer_registry
    )
    tokenizer_registry = URIHandlerTokenizerRegistry()
    for entrypoint in entrypoints:
        extra_registry = plugin_utils.execute_plugin_object_reference(
            entrypoint.value,
            call_obj=True,
        )
        tokenizer_registry += extra_registry

    return tokenizer_registry


def create_tokenizer_config(tokenizer_name: str, **kwargs):
    """
    Returns a tokenizer config from the tokenizer registry.
    Either `tokenizer_id` or `tokenizer_config_path` should be specified.

    Args:
        tokenizer_name (:obj:`str`): Either a `tamm` tokenizer's id,
            or a custom tokenizer config path.
    Returns:
        tokenizer_config: A tokenizer config object.
    """
    return get_tokenizer_registry().create_config(tokenizer_name, **kwargs)


def create_tokenizer(
    tokenizer_spec: TokenizerSpecType,
    *args,
    **kwargs,
) -> "Tokenizer":
    """
    Creates and returns a tokenizer instance based on the provided tokenizer spec.

    Args:
        tokenizer_spec (:obj:`str | TokenizerConfig | PublishedTokenizerConfig | TokenizerBase`):
            Acceptable input formats are
                1. A ``str`` of tokenizer_id, which is used to map tp a published tokenizer config.
                2. A :py:class:`.TokenizerConfig` object.
                3. A :py:class:`.PublishedTokenizerConfig` object.
                4. An instance of class inherited from :py:class:`.TokenizerBase`.

    Raises
        ValueError: If the model ID is not a string, is None. Also, if the
            registry has no entry for the requested tokenizer.
        KeyError: If the registry has no entry for the provided
            model ID.
    """
    return get_tokenizer_registry().create(
        tokenizer_spec,
        *args,
        **kwargs,
    )


def create_tokenizer_from_model_id(
    model_id: str,
    **kwargs,
) -> "Tokenizer":
    """
    Creates and returns a tokenizer instance based on the provided model ID.

    Args:
        model_id (:obj:`str`): The `tamm` model's id.
        vocab_path (:obj:`str`, optional): the path to the vocab file.
        user_defined_tokens (:obj:`list`, optional): List of user defined tokens.
            Defaults to `None`.

    Raises
        ValueError: If the model ID is not a string, is None. Also, if the
            registry has no entry for the requested tokenizer.
        KeyError: If the registry has no entry for the provided
            model ID.
    """
    if model_id is None or not isinstance(model_id, str):
        raise ValueError(
            "To create a tokenizer, model_id needs to be a valid string and cannot be "
            f"None or empty. Currently provided model_id = {model_id}"
        )
    try:
        # pylint: disable-next=import-outside-toplevel
        from tamm.model_repo import create_model_config

        config = create_model_config(model_id)
    except KeyError as e:
        raise KeyError(
            f"Cannot determine tokenizer because model ID '{model_id}' "
            f"does not exist"
        ) from e

    return get_tokenizer_registry().create(
        config.metadata.tokenizer_spec,
        **kwargs,
    )


def create_tokenizer_from_tokenizer_id(
    tokenizer_id: str,
    **kwargs,
) -> "Tokenizer":
    """
    Creates and returns a tokenizer instance based on the provided tokenizer ID.

    Raises ValueError: If the tokenizer ID is not a string, or is None.
        Also, if the registry has no entry for the requested tokenizer.
    """
    _tamm_warnings.deprecation(
        "create_tokenizer_from_tokenizer_id() is deprecated.  "
        "Please use `tamm.create_tokenizer` instead."
    )
    if tokenizer_id is None or not isinstance(tokenizer_id, str):
        raise ValueError(
            "To create a tokenizer, tokenizer_id needs to be a valid string and cannot "
            f"be None or empty. Currently provided tokenizer_id = {tokenizer_id}"
        )

    return get_tokenizer_registry().create(
        tokenizer_id,
        **kwargs,
    )


def list_tokenizers(include_descriptions=False, filter_deprecated=False):
    """
    Lists all tokenizer ids from the tokenizer registry.

    Args:
        include_descriptions (:obj:`bool`, optional): Specifies if descriptions
            should be included. If set to `True`, the return value will be a `dict`
            with tokenizer_ids as keys and descriptions as values. Defaults to `False`.
        filter_deprecated (:obj:`bool`, optional): True: don't show deprecated tokenizers;
            False: show deprecated tokenizers
    Returns:
        A `list` or a `dict` containing available tokenizers.
    """
    tokenizer_ids = get_tokenizer_registry().list_(filter_deprecated=filter_deprecated)
    if not include_descriptions:
        return tokenizer_ids
    return {
        tokenizer_id: get_tokenizer_registry().describe(tokenizer_id)
        for tokenizer_id in tokenizer_ids
    }
