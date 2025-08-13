"""
This module provides wrappers of tamm models for the Hugging Face
:mod:`transformers` ecosystem.
"""

# pylint: disable=wrong-import-position

import logging as _logging

_logger = _logging.getLogger(__name__)

try:
    import transformers as _hf_transformers
except Exception:
    _logger.error(
        "tamm.hf.transformers requires the Hugging Face transformers package, "
        "but tamm could not import this.  Please install transformers or check "
        "your transformers installation."
    )
    raise


from tamm import _plugin
from tamm.hf.transformers import modeling_utils
from tamm.hf.transformers.models.auto import (
    AutoConfig,
    AutoModel,
    AutoModelForCausalLM,
    register_with_auto_classes,
)
from tamm.hf.transformers.models.causal_lm import (
    TammCausalLMConfig,
    TammCausalLMForCausalLM,
    TammCausalLMModel,
)
from tamm.hf.transformers.models.sentencepiece import TammSentencePieceTokenizer

_plugin.execute_core_transformers_import_callbacks()
