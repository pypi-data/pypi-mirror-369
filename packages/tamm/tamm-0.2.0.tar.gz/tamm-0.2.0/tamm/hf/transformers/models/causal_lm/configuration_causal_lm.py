"""HF transformers model configuration for tamm CausalLMTransformer"""

import logging as _logging
from typing import Optional as _Optional

import tamm as _tamm
from tamm.hf.transformers import configuration_utils as _configuration_utils

_logger = _logging.getLogger(__name__)


class TammCausalLMConfig(_configuration_utils.TammPretrainedConfig):
    """
    Config for CausalLM models.

    Args:
        tamm_config (:obj:`.ModelConfig`): A |tamm| config for a
            :obj:`.CausalLMTransformer`.
        **kwargs: Keyword arguments for default fields in
            :obj:`transformers.PretrainedConfig`.
    """

    model_type = "tamm_causal_lm"

    def __init__(
        self, tamm_config: _Optional[_tamm.layers.ModuleConfig] = None, **kwargs
    ):
        kwargs.setdefault(
            "use_cache", True
        )  # required to pass use_cache to from_pretrained
        super().__init__(tamm_config=tamm_config, **kwargs)
        self.is_decoder = True
        self.is_encoder_decoder = False

    @property
    def tie_word_embeddings(self):
        try:
            model = self.tamm_config.create_model(device="meta")
        except Exception:
            return False
        return getattr(model, "is_embedding_tied_to_output_transform", False)

    @tie_word_embeddings.setter
    def tie_word_embeddings(self, value):  # pylint: disable=unused-argument
        _logger.debug("ignoring call to TammCausalLMConfig.tie_word_embeddings setter")

    @property
    def vocab_size(self) -> int:
        """
        The model's vocab size.  We include this property because some parts of the
        HuggingFace ecosystem require it (specifically beam search decoding as of
        ``transformers==4.50``).

        This attribute is not standardized in |tamm|, so it may not work for all
        models.  Please contact the |tamm| team if you encounter issues with this.
        """
        if self.tamm_config is None:
            raise RuntimeError("Cannot provide vocab_size, since tamm_config is None")
        if not hasattr(self.tamm_config, "vocab_size"):
            raise RuntimeError(
                "Cannot provide vocab_size, since tamm_config does not have an "
                "attribute named 'vocab_size'.  Please contact the tamm team "
                "to support this use case."
            )
        return self.tamm_config.vocab_size
