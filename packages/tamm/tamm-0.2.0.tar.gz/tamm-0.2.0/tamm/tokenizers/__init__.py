"""
.. _tamm_tokenizers:

tamm.tokenizers
===============

Create tokenizer
----------------
.. autofunction:: tamm.create_tokenizer

.. autofunction:: tamm.create_tokenizer_config

.. autofunction:: tamm.create_tokenizer_from_model_id

.. autofunction:: tamm.create_tokenizer_from_tokenizer_id

Tokenizers Base Classes
-----------------------

.. autoclass:: tamm.tokenizers.common.Tokenizer
   :show-inheritance:
   :members:
   :member-order: bysource

.. autoclass:: tamm.tokenizers.sentencepiece.SentencePieceTokenizer
   :show-inheritance:
   :members:
   :member-order: bysource

.. autoclass:: tamm.tokenizers.afm.AFMTokenizer
   :show-inheritance:
   :members:

Text Processors
---------------

.. autoclass:: tamm.tokenizers.text_processors.TextProcessor
   :show-inheritance:
   :members:
   :member-order: bysource

.. autoclass:: tamm.tokenizers.text_processors.FindAndReplaceTextProcessor
   :show-inheritance:
   :members:
   :member-order: bysource

.. automodule:: tamm.tokenizers.registry
"""

from tamm.tokenizers import afm, common, sentencepiece, text_processors
from tamm.tokenizers.api import (
    TokenizerSpecType,
    create_tokenizer,
    create_tokenizer_config,
    create_tokenizer_from_model_id,
    create_tokenizer_from_tokenizer_id,
    list_tokenizers,
)
