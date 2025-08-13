"""
tamm.preprocessors
------------------

This module implements configurable preprocessors that
process raw data into model inputs.

.. Tip::

    Users new to this module should also check out our
    :ref:`preprocessor tutorial <preprocessors_guide>`.

.. autoclass:: tamm.preprocessors.Preprocessor
    :members:
    :special-members: __call__
    :private-members:

.. autofunction:: tamm.preprocessors.create
.. autofunction:: tamm.preprocessors.list
.. automodule:: tamm.preprocessors.registry

"""
from tamm.preprocessors import instruct_lm

# pylint: disable=redefined-builtin
from tamm.preprocessors.api import create, describe
from tamm.preprocessors.api import list_objects as list
from tamm.preprocessors.base import Preprocessor

__all__ = [
    "Preprocessor",
    "list",
    "create",
    "describe",
    "instruct_lm",
]
