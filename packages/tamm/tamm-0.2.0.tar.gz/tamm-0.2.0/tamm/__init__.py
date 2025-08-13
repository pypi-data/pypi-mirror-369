"""
tamm
----

Model API
^^^^^^^^^
.. autofunction:: tamm.create_model
.. autofunction:: tamm.create_adapted_model
.. autofunction:: tamm.create_model_builder
.. autofunction:: tamm.create_model_config
.. autofunction:: tamm.is_adapted_model_name
.. autofunction:: tamm.is_model_builder_name
.. autofunction:: tamm.is_model_config_name
.. autofunction:: tamm.is_model_name
.. autofunction:: tamm.list_adapted_models
.. autofunction:: tamm.list_model_builders
.. autofunction:: tamm.list_model_configs
.. autofunction:: tamm.list_models

Tokenizer API
^^^^^^^^^^^^^
See :ref:`tamm.tokenizers <tamm_tokenizers>`

Converter API
^^^^^^^^^^^^^
.. autofunction:: tamm.list_converters

Checkpoint API
^^^^^^^^^^^^^^
.. autofunction:: tamm.load
.. autofunction:: tamm.save


Logging
^^^^^^^

.. data:: tamm.logger

    The root |tamm| :obj:`logging.Logger`.


Runtime configuration
^^^^^^^^^^^^^^^^^^^^^

.. data:: tamm.rc

    The global :obj:`.RuntimeConfiguration` instance.


|tamm| Attributes
^^^^^^^^^^^^^^^^^
.. automodule:: tamm.context_vars

"""

# pylint: disable=wrong-import-position

# isort: off
# configure rc and logger first because they may be used during import
from tamm.runtime_configuration import rc  # pylint: disable=unused-import
from tamm import _logger

logger = _logger.init_logger()
# isort: on

from tamm import (
    _adapters_v1,
    _compat,
    _plugin,
    adapters,
    ao,
    converters,
    generation,
    layers,
    models,
    preprocessors,
    utils,
)
from tamm._version import __version__
from tamm.context_vars import (
    first_token_generation_context,
    freeze_params_flag_context,
    get_default_freeze_params_flag,
    get_default_pretrained_flag,
    get_first_token_generation_flag,
    pretrained_flag_context,
    resolve_device,
    resolve_freeze_params,
    resolve_pretrained_flag,
    set_default_freeze_params_flag,
    set_default_pretrained_flag,
)
from tamm.converters import list_converters, load, save
from tamm.model_repo import (
    create_adapted_model,
    create_model,
    create_model_builder,
    create_model_config,
    is_adapted_model_name,
    is_model_builder_name,
    is_model_config_name,
    is_model_name,
    list_adapted_models,
    list_model_builders,
    list_model_configs,
    list_models,
)
from tamm.tokenizers import (
    create_tokenizer,
    create_tokenizer_config,
    create_tokenizer_from_model_id,
    create_tokenizer_from_tokenizer_id,
    list_tokenizers,
)

_plugin.execute_core_import_callbacks()

_compat.execute_backward_compatibility_imports()

__all__ = [
    "logger",
    "adapters",
    "ao",
    "converters",
    "layers",
    "models",
    "preprocessors",
    "utils",
    "create_adapted_model",
    "create_model",
    "create_model_builder",
    "create_model_config",
    "generation",
    "is_adapted_model_name",
    "is_model_builder_name",
    "is_model_config_name",
    "is_model_name",
    "list_adapted_models",
    "list_model_builders",
    "list_model_configs",
    "list_models",
    "__version__",
    "list_converters",
    "load",
    "save",
    "rc",
    "create_tokenizer",
    "create_tokenizer_config",
    "create_tokenizer_from_model_id",
    "create_tokenizer_from_tokenizer_id",
    "list_tokenizers",
    "freeze_params_flag_context",
    "first_token_generation_context",
    "pretrained_flag_context",
    "get_default_freeze_params_flag",
    "get_first_token_generation_flag",
    "get_default_pretrained_flag",
    "set_default_freeze_params_flag",
    "set_default_pretrained_flag",
    "resolve_device",
    "resolve_pretrained_flag",
    "resolve_freeze_params",
]
