"""
utils.json
==========

This submodule includes functions for serializing |tamm| objects to JSON.

Example:

To deserialize a model config from JSON and to use it for model creation:

.. tip::
    See :ref:`configure tamm models <configure_models>` for extra context regarding tamm
    model lifecycle.

.. code-block:: python

    import tamm.utils.json as tamm_json

    with open("invalid_type.json", "r", encoding="utf-8") as fptr:
        config = tamm_json.load(fptr)

    model = config.create_model()


To serialize a model config from JSON and to use it for model creation:

.. code-block:: python

    import tamm
    import tamm.utils.json as tamm_json

    config = tamm.create_model_config(model_id)
    # apply customizations to config (e.g., change number of layers)
    config.num_layers = 8
    with open("customized_model_config.json", "w", encoding="utf-8") as fptr:
        tamm_json.dump(config, fptr)

.. autofunction:: load
.. autofunction:: loads
.. autofunction:: dump
.. autofunction:: dumps

.. autofunction:: tamm.utils.json.iter_json_serializable


Classes useful for plugin developers
------------------------------------

.. autoclass:: tamm.utils.json.JSONSerializableMixin
   :members:
   :private-members:

.. autoclass:: tamm.utils.json.JSONSerializableABCMixin

.. autoclass:: tamm.utils.json.SupportsObjectHook
    :members:

.. autofunction:: tamm.utils.json.register_load_normalizer

.. autoclass:: tamm.utils.json.BackwardCompatibilityTypeNormalizer
    :show-inheritance:

.. autoclass:: tamm.utils.json.BackwardCompatibilityTypeNormalizerMode
    :members:
"""

from tamm.utils.json._normalization import (
    BackwardCompatibilityTypeNormalizer,
    BackwardCompatibilityTypeNormalizerMode,
    SupportsObjectHook,
    register_load_normalizer,
)
from tamm.utils.json._utils import JSONSerializableABCMixin, JSONSerializableMixin
from tamm.utils.json.api import dump, dumps, load, loads
from tamm.utils.json.itertools import iter_json_serializable

__all__ = [
    "BackwardCompatibilityTypeNormalizer",
    "BackwardCompatibilityTypeNormalizerMode",
    "dump",
    "dumps",
    "load",
    "loads",
    "JSONSerializableABCMixin",
    "JSONSerializableMixin",
    "SupportsObjectHook",
    "register_load_normalizer",
]
