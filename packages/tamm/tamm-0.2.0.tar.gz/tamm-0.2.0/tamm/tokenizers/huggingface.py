"""
Implements a |tamm| tokenizer using HuggingFace.
"""

import logging
from functools import cached_property
from typing import Iterable, List, Union, cast

from tamm.tokenizers.common import Tokenizer as _TokenizerBase

logger = logging.getLogger(__name__)


class HuggingFaceTokenizer(_TokenizerBase):
    """
    Base class for HuggingFace Tokenizers. It wraps the Tokenizer implementation from
    HuggingFace ``transformers``.

    Args:
        tokenizer_path (:obj:`str`): Path to HuggingFace tokenizer configs. For
            pretrained tokenizers from transformers, the path usually contains multiple
            json files such as `tokenizer.json`, `tokenizer_config.json`,
            `vocab.json` and alike.
    """

    def __init__(self, tokenizer_path: str):
        try:
            # lazily import huggingface to support using tamm without huggingface tokenizers
            # pylint: disable=import-outside-toplevel
            from transformers import AutoTokenizer
        except ImportError:
            logger.error(
                "tamm tried to initialize a tokenizer that requires huggingface tokenizers"
                "library, but tamm could not import this.  Please install tokenizers"
                "or check your installation of this package."
            )
            raise
        self._tokenizer_path = tokenizer_path
        self._tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

    def __len__(self) -> int:
        """Vocabulary size of the HuggingFace tokenizer."""
        return len(self._tokenizer.get_vocab())

    @property
    def tokenizer_path(self):
        return self._tokenizer_path

    @property
    def hf_tokenizer(self):
        """The HuggingFace tokenizer."""
        return self._tokenizer

    def encode(
        self,
        texts: Union[str, Iterable[str]],
        **kwargs,  # pylint: disable=arguments-differ
    ) -> Union[List[int], List[List[int]]]:
        """Converts a string or a list of strings into a list of token IDs."""
        return self.hf_tokenizer.encode(texts, **kwargs)

    def decode(  # pylint: disable=arguments-differ
        self,
        token_ids: Union[int, Iterable[int], Iterable[Iterable[int]]],
        skip_special_tokens: bool = False,
        **kwargs,
    ) -> Union[str, List[str]]:
        """Decodes token IDs to their corresponding strings."""
        if isinstance(token_ids, int):
            token_ids = [token_ids]
        decoded_texts = self.hf_tokenizer.decode(
            token_ids, skip_special_tokens=skip_special_tokens, **kwargs
        )
        return decoded_texts

    @cached_property
    def pad_id(self) -> int:
        return self.hf_tokenizer.pad_token_id

    @cached_property
    def eos_id(self) -> int:
        return self.hf_tokenizer.eos_token_id

    @cached_property
    def unk_id(self) -> int:
        return self.hf_tokenizer.unk_token_id

    @cached_property
    def eot_id(self) -> int:
        eot_token = getattr(self.hf_tokenizer, "eot_token")
        if not eot_token:
            return self.eos_id
        return cast(int, self.encode(eot_token)[0])
