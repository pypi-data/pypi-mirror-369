"""
tamm.converters
---------------

This module implements components for converting |tamm| state dicts to and from other formats.

Base class
^^^^^^^^^^

.. autoclass:: tamm.converters.StateDictConverter
    :members:


Configurable string matching converters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: tamm.converters.StringMatchingConverter
    :show-inheritance:

.. autoclass:: tamm.converters.ManyToManyStringMatchingConverter
    :show-inheritance:

.. autoclass:: tamm.converters.ParamMapper
    :show-inheritance:

.. autoclass:: tamm.converters.RegExSubstitutionConverter
    :show-inheritance:


Composite converter types
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: tamm.converters.UnionConverter
    :show-inheritance:

.. autoclass:: tamm.converters.SequentialConverter
    :show-inheritance:

.. autoclass:: tamm.converters.LayerwiseConverter
    :show-inheritance:

.. autoclass:: tamm.converters.PrefixStringMatchingConverter
    :show-inheritance:

.. autoclass:: tamm.converters.MultiPrefixStringMatchingConverter
    :show-inheritance:


Other converter types
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: tamm.converters.IdentityConverter
    :show-inheritance:
"""

from tamm.converters import layers
from tamm.converters.common import (
    IdentityConverter,
    LayerwiseConverter,
    ManyToManyStringMatchingConverter,
    MultiPrefixStringMatchingConverter,
    ParamMapper,
    PrefixStringMatchingConverter,
    RegExSubstitutionConverter,
    SequentialConverter,
    StateDictConverter,
    StringMatchingConverter,
    UnionConverter,
)
from tamm.converters.models import (
    ModelStateDictConverter,
    convert_from_tamm_state_dict,
    convert_to_tamm_state_dict,
    list_converters,
    load,
    save,
)
