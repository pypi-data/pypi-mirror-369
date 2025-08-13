"""
Implements SentencePiece tokenizers for Apple Foundation Models.
"""

import functools as _functools
import os as _os
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Iterable as _Iterable
from typing import Optional as _Optional
from typing import Union as _Union

from tamm import _helpers
from tamm.tokenizers import text_processors as _text_processors
from tamm.tokenizers.sentencepiece import (
    SentencePieceTokenizer as _SentencePieceTokenizer,
)
from tamm.tokenizers.text_processors import TextProcessor as _TextProcessorBase
from tamm.tokenizers.text_processors import TextProcessorConfig as _TextProcessorConfig
from tamm.tokenizers.text_processors import TextProcessorMode as _TextProcessorMode
from tamm.utils import _pretrained


class AFMTokenizer(_SentencePieceTokenizer):
    """
    Tokenizer for AFM models, includes a default text processor that converts newline
    characters to a special token representation ``<n>``.
    """

    def __init__(
        self,
        vocab_path: _Optional[str] = None,
        user_defined_tokens: _Optional[_Iterable[str]] = None,
        extra_properties: _Dict[str, _Any] = None,
        text_processor: _Optional[
            _Union[str, _TextProcessorMode, _TextProcessorBase, _TextProcessorConfig]
        ] = "afm_text_find_and_replace",
    ):
        self._vocab_file_path = vocab_path

        if extra_properties is not None:
            for key, value in extra_properties.items():
                setattr(self, key, value)

        if isinstance(text_processor, str):
            text_processor = _helpers.get_enum_member_from_name(
                _TextProcessorMode, text_processor
            )
        if text_processor is _TextProcessorMode.AFM_TEXT_FIND_AND_REPLACE:
            text_processor = _text_processors.FindAndReplaceTextProcessor({"\n": "<n>"})
        elif isinstance(text_processor, _TextProcessorConfig):
            text_processor = text_processor()

        super().__init__(
            vocab_path=self.vocab_path,
            user_defined_tokens=user_defined_tokens,
            text_processor=text_processor,
        )

    @_functools.cached_property
    def vocab_path(self) -> str:
        """Returns the local path of the vocabulary file."""
        if _os.path.exists(self._vocab_file_path):
            return str(self._vocab_file_path)
        return _pretrained.fetch_file(remote_path=self._vocab_file_path).as_posix()
