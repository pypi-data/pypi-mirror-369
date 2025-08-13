"""
Tokenizer registry
==================

This module defines baseclass for all ``TokenizerRegistry``.

tamm plugin may extend tokenizer registry by implementing a class that inherits :py:class:`.TokenizerRegistry` and
publicize a custom tokenizer registry by exposing a factory of TokenizerRegistry  via package metadata

.. code-block:: toml

    [project.entry-points.'tamm.plugins.extras']
    tokenizer-registry = 'module.submodule:get_tokenizer_registry'

"""
from tamm.tokenizers.registry.base import ComposedTokenizerRegistry, TokenizerRegistry
from tamm.tokenizers.registry.placeholder import PlaceholderTokenizerRegistry
from tamm.tokenizers.registry.uri_handler import URIHandlerTokenizerRegistry

__all__ = [
    "TokenizerRegistry",
    "ComposedTokenizerRegistry",
    "PlaceholderTokenizerRegistry",
    "URIHandlerTokenizerRegistry",
]
