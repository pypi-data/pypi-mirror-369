"""
Implements a |tamm| tokenizer using SentencePiece.
"""

import logging
import os
from functools import cached_property
from typing import Any, Iterable, List, Optional, Union, cast

from packaging.version import parse as parse_version

from tamm.tokenizers.common import Tokenizer as _TokenizerBase
from tamm.tokenizers.text_processors import TextProcessor as _TextProcessorBase

logger = logging.getLogger(__name__)


def _add_user_defined_tokens_and_save_to_file(
    vocab_path, output_path, user_defined_tokens
):
    os.environ[
        "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"
    ] = "python"  # Force protobuf to use Python backend, will not affect parent process

    # pylint: disable=import-outside-toplevel,import-error
    from sentencepiece import SentencePieceProcessor

    tokenizer = SentencePieceProcessor()
    tokenizer.Load(vocab_path)
    logger.debug(
        f"Loaded vocab file from {vocab_path}, vocab size = {tokenizer.vocab_size()}"
    )
    _add_user_defined_tokens(tokenizer, user_defined_tokens)
    with open(output_path, "wb") as file:
        file.write(tokenizer.serialized_model_proto())
        logger.debug(
            f"New vocab size = {tokenizer.vocab_size()}, written to {output_path}"
        )


def _add_user_defined_tokens_in_new_process(
    tokenizer: Any, vocab_path: str, user_defined_tokens: Iterable[str]
):
    # pylint: disable=import-outside-toplevel
    import multiprocessing as mp
    import tempfile

    from sentencepiece import SentencePieceProcessor  # pylint: disable=import-error

    assert isinstance(tokenizer, SentencePieceProcessor)
    with tempfile.NamedTemporaryFile() as temp_file:
        # First, pad the vocab in a new process and save to `temp_file`
        logger.debug("Starting a new process to add user defined tokens")
        ctx = mp.get_context("spawn")
        p = ctx.Process(
            target=_add_user_defined_tokens_and_save_to_file,
            args=(vocab_path, temp_file.name, user_defined_tokens),
        )
        p.start()
        p.join()
        if p.exitcode != 0:
            # pylint: disable=raise-missing-from
            raise RuntimeError(
                "Failed to pad sentencepiece model,"
                f" subprocess failed with exit code {p.exitcode}"
            )
        logger.debug("The new process exited successfully")

        # Load updated vocab from `temp_file`
        tokenizer.Load(temp_file.name)
        logger.debug("Loaded updated vocab file")


def _add_user_defined_tokens(tokenizer: Any, user_defined_tokens: Iterable[str]):
    # pylint: disable=import-outside-toplevel,import-error
    from sentencepiece import SentencePieceProcessor
    from sentencepiece import sentencepiece_model_pb2 as sp_pb2

    assert isinstance(tokenizer, SentencePieceProcessor)
    pb = sp_pb2.ModelProto()  # pylint: disable=invalid-name, E1101
    pb.ParseFromString(tokenizer.serialized_model_proto())
    for token in user_defined_tokens:
        # Add an user defined token
        new_token = sp_pb2.ModelProto().SentencePiece()  # pylint: disable=E1101
        new_token.piece = token
        new_token.score = 0.0
        new_token.type = 4  # USER_DEFINED
        pb.pieces.append(new_token)
    tokenizer.LoadFromSerializedProto(pb.SerializeToString())


class SentencePieceTokenizer(_TokenizerBase):
    """
    Base class for SentencePiece Tokenizers.

    Args:
        vocab_path (:obj:`str`): Path to sentencepiece vocab file.
        user_defined_tokens (:obj:`list`, optional): List of user defined tokens to
            add to vocab. Defaults to `None`.
        pad_vocab_size_to (:obj:`int`, optional): Pad the current vocab size to this
            size. If this value is not `None`, ..., "<extra_id_2>", "<extra_id_1>",
            "<extra_id_0>" will be added to vocab, otherwise no padding will be added.
            Defaults to `None`.
        text_processor(:obj:`tamm.tokenizers.base.TextProcessorBase`, optional): Text
            process to use before encoding and after decoding. Defaults to `None`.
    """

    def __init__(
        self,
        vocab_path: str,
        user_defined_tokens: Optional[Iterable[str]] = None,
        pad_vocab_size_to: Optional[int] = None,
        text_processor: Optional[_TextProcessorBase] = None,
    ):
        try:
            # lazily import sentencepiece to support using tamm without sentencepiece
            # pylint: disable=import-outside-toplevel
            import sentencepiece
        except ImportError:
            logger.error(
                "tamm tried to initialize a tokenizer that requires sentencepiece, but "
                "tamm could not import this.  Please install sentencepiece or check "
                "your installation of this package."
            )
            raise

        self._vocab_path = vocab_path
        self._tokenizer = sentencepiece.SentencePieceProcessor()
        self._tokenizer.Load(self._vocab_path)
        self.text_processor = text_processor

        additional_tokens = []
        if user_defined_tokens is not None:
            additional_tokens += user_defined_tokens

        if pad_vocab_size_to is not None:
            additional_tokens += [
                f"<extra_id_{idx}>"
                for idx in reversed(
                    range(pad_vocab_size_to - len(self) - len(additional_tokens))
                )
            ]

        if len(additional_tokens) > 0:
            self.add_user_defined_tokens(additional_tokens)

    def add_user_defined_tokens(self, user_defined_tokens: Iterable[str]):
        # pylint: disable=import-outside-toplevel,unused-import
        try:
            import sentencepiece  # noqa: F401
        except ImportError:
            logger.error(
                "tamm tried to initialize a tokenizer that requires sentencepiece, but "
                "tamm could not import this.  Please install sentencepiece or check "
                "your installation of this package."
            )
            raise

        from google import protobuf

        # Dispatch calls based on protobuf version
        if parse_version(protobuf.__version__) < parse_version("4.0"):
            _add_user_defined_tokens(self._tokenizer, user_defined_tokens)
        else:
            logger.debug(
                "Fall back to Python protobuf backend to add user defined tokens"
                f" because protobuf version {protobuf.__version__} is not supported"
            )
            _add_user_defined_tokens_in_new_process(
                self._tokenizer, self.vocab_path, user_defined_tokens
            )
        logger.debug(f"Added the following tokens {user_defined_tokens}")

    def __len__(self) -> int:
        """Vocabulary size of the SentencePiece tokenizer."""
        return cast(int, self.tokenizer.vocab_size())

    @property
    def vocab_path(self):
        return self._vocab_path

    @property
    def tokenizer(self):
        """The SentencePiece tokenizer."""
        return self._tokenizer

    def encode(
        self,
        texts: Union[str, Iterable[str]],
        apply_processor: bool = True,
        **kwargs,  # pylint: disable=arguments-differ
    ) -> Union[List[int], List[List[int]]]:
        """Converts a string or a list of strings into a list of token IDs."""
        if apply_processor and self.text_processor is not None:
            texts = self.text_processor.process(texts)
        return self.tokenizer.Encode(texts, **kwargs)

    def decode(  # pylint: disable=arguments-differ
        self,
        token_ids: Union[int, Iterable[int], Iterable[Iterable[int]]],
        apply_processor: bool = True,
        **kwargs,
    ) -> Union[str, List[str]]:
        """Decodes token IDs to their corresponding strings."""
        decoded_texts = self.tokenizer.Decode(token_ids, **kwargs)
        if apply_processor and self.text_processor is not None:
            decoded_texts = self.text_processor.inverse(decoded_texts)
        return decoded_texts

    def encode_as_pieces(  # pylint: disable=arguments-differ
        self,
        texts: Union[str, Iterable[str]],
        apply_processor: bool = True,
    ) -> Union[List[str], List[List[str]]]:
        """Tokenizes texts into subword pieces."""
        if apply_processor and self.text_processor is not None:
            texts = self.text_processor.process(texts)
        return cast(List[str], self.tokenizer.EncodeAsPieces(texts))

    @cached_property
    def pad_id(self) -> int:
        return cast(int, self.tokenizer.pad_id())

    @cached_property
    def eos_id(self) -> int:
        return cast(int, self.tokenizer.eos_id())

    @cached_property
    def unk_id(self) -> int:
        return cast(int, self.tokenizer.unk_id())
