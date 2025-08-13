"""
transformer.token_metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^

This module defines classes for handling token metadata within a
:class:`.TransformerStack`.


.. autoclass:: tamm.layers.transformer.token_metadata.TokenMetadataLogic
    :show-inheritance:
    :members: forward

.. autoclass:: tamm.layers.transformer.token_metadata.TokenMetadata
    :members:

.. autoclass:: tamm.layers.transformer.token_metadata.VanillaTokenMetadataLogic
    :show-inheritance:
"""

from tamm.layers.transformer.token_metadata.common import (
    TokenMetadata,
    TokenMetadataLogic,
)
from tamm.layers.transformer.token_metadata.vanilla import VanillaTokenMetadataLogic
