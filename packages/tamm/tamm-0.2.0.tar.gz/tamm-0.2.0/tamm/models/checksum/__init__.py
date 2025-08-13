"""
Model Checksum
--------------

``tamm`` provides following utility functions for model checksum:

.. autofunction:: tamm.models.checksum.compare_checksum_with_source
.. autofunction:: tamm.models.checksum.compare_factory_checksum_with_source

Low-Level Functions
^^^^^^^^^^^^^^^^^^^
.. autofunction:: tamm.models.checksum.state_dict_checksum

"""

from tamm.models.checksum._checksum import state_dict_checksum
from tamm.models.checksum.api import (
    compare_checksum_with_source,
    compare_factory_checksum_with_source,
)

__all__ = [
    "state_dict_checksum",
    "compare_checksum_with_source",
    "compare_factory_checksum_with_source",
]
