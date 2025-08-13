"""
Preprocessor registry
=====================

This module defines baseclass for all ``PreprocessorRegistry``.

tamm plugin may extend Preprocessor registry by implementing a class that inherits :py:class:`.PreprocessorRegistry`
and publicize a custom Preprocessor registry by exposing a factory of PreprocessorRegistry via package metadata

.. code-block:: toml

    [project.entry-points.'tamm.plugins.extras']
    preprocessor-registry = 'module.submodule:get_preprocessor_registry'

"""
from tamm.preprocessors.registry.base import PreprocessorRegistry
from tamm.preprocessors.registry.uri_handler import URIHandlerPreprocessorRegistry

__all__ = ["PreprocessorRegistry", "URIHandlerPreprocessorRegistry"]
