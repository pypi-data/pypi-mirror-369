import contextlib as _contextlib
import logging as _logging
import os as _os
import warnings as _warnings
from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

from transformers.tokenization_utils import AddedToken as _AddedToken
from transformers.tokenization_utils import PreTrainedTokenizer as _PreTrainedTokenizer

from tamm.tokenizers.sentencepiece import _add_user_defined_tokens
from tamm.typing import PathLike as _PathLike
from tamm.utils.uri import _is_uri, _URIHandler

_HFTokenType = _Union[str, _AddedToken]

_logger = _logging.getLogger(__name__)


class TammSentencePieceTokenizer(_PreTrainedTokenizer):
    """
    This is a HuggingFace tokenizer implementation that wraps an underlying
    :module:`sentencepiece` tokenizer.  Compared to the :class:`LlamaTokenizer`
    from :module:`transformers`, it is a thinner wrapper around the SentencePiece
    model, and it intentionally does not support ``split_special_tokens=False``
    (at least for now). We do this so that the tokenizer more precisely follows
    the behavior of the underlying SentencePiece tokenizer.

    Args:
        vocab_file (:obj:`str`): A filepath or URI for the SentencePiece
            vocab file.
        bos_token (:obj:`str` or :obj:`AddedToken`): The beginning-of-sequence
            token, typically ``"<s>"``.
        eos_token (:obj:`str` or :obj:`AddedToken`): The end-of-sequence
            token, typically ``"</s>"``.
        unk_token (:obj:`str` or :obj:`AddedToken`): The unknown token,
            typically ``"<unk>"``.
        pad_token (:obj:`str` or :obj:`AddedToken`): The padding token,
            typically ``"<pad>"``.
        additional_special_tokens (:obj:`list` of :obj:`str`): An optional
            list of additional special tokens.
        add_bos_token (:obj:`bool`, optional): A flag that controls prepending
            the BOS token id when encoding.  Defaults to ``False``.  When
            enabled, prepending only happens if ``add_special_tokens`` is also
            ``True``.
        chat_template (:obj:`str`): An optional Jinja template for
            :meth:`apply_chat_template`.
        chat_template_strip_first_token (:obj:`str`, optional): A flag that
            controls whether to drop the first token when calling
            :meth:`apply_chat_template`.  Defaults to ``False``.
        chat_template_add_special_tokens (:obj:`str`, optional): A flag that
            controls whether to add special tokens in :meth:`apply_chat_template`.
            Defaults to ``False``.
        text_replacements (:obj:`dict` of :obj:`str` pairs): A dictionary
            of text pairs to preprocess encoding and postprocess decoding.
            For example, ``text_replacements={"\n": "<n>"}`` replaces
            newlines with ``"<n>"`` prior to tokenization and replaces
            "<n>" with newlines after detokenization.
        **kwargs: Additional keyword arguments for
            :meth:`PreTrainedTokenizer.__init__`.
    """

    # Developer note: The point of this class is to provide a HF tokenizer that
    # can be configured to precisely match the SentencePiece behavior that we run
    # in production.  As of transformers==4.50, this is tricky due to some tedious
    # details, mostly involving HF's custom treatment of special tokens when
    # split_special_tokens=False (the HF default).  In particular, this option
    # results in different handling of the SentencePiece control tokens <s>, </s>,
    # <pad>, and <unk>, and it also requires many tricks to preserve the
    # SentencePiece dummy prefix behavior (see the implementation of
    # transformers.LlamaTokenizer).  We work around these challenges by dynamically
    # adding user-defined tokens to the SentencePiece vocab and forcing
    # split_special_tokens=True.  The only downside that we are aware of is that
    # some HF special token features (such as stripping neighboring whitespace) are
    # not supported.  This is not concerning, since SentencePiece does not support
    # this behavior either.

    vocab_files_names = {"vocab_file": "tokenizer.model"}
    model_input_names = ["input_ids", "attention_mask"]

    def __init__(
        self,
        vocab_file: _Union[str, _PathLike],
        bos_token: _Optional[_HFTokenType] = "<s>",
        eos_token: _Optional[_HFTokenType] = "</s>",
        unk_token: _Optional[_HFTokenType] = "<unk>",
        pad_token: _Optional[_HFTokenType] = "<pad>",
        additional_special_tokens: _Optional[_List[_HFTokenType]] = None,
        add_bos_token: bool = False,
        chat_template: _Optional[str] = None,
        chat_template_add_special_tokens: bool = False,
        chat_template_strip_first_token: bool = False,
        text_replacements: _Optional[_Dict[str, str]] = None,
        **kwargs,
    ):
        self.vocab_file = vocab_file
        self.text_replacements = text_replacements
        self.add_bos_token = add_bos_token

        self.chat_template_add_special_tokens = chat_template_add_special_tokens
        self.chat_template_strip_first_token = chat_template_strip_first_token
        self._is_apply_chat_template_context = False

        if additional_special_tokens is None:
            additional_special_tokens = []
        self._init_sp_model(vocab_file)
        self._register_sp_tokens(
            bos_token, eos_token, unk_token, pad_token, *additional_special_tokens
        )

        kwargs.setdefault("split_special_tokens", True)
        super().__init__(
            bos_token=bos_token,
            eos_token=eos_token,
            unk_token=unk_token,
            pad_token=pad_token,
            additional_special_tokens=additional_special_tokens,
            add_bos_token=add_bos_token,
            chat_template=chat_template,
            chat_template_add_special_tokens=chat_template_add_special_tokens,
            chat_template_strip_first_token=chat_template_strip_first_token,
            text_replacements=text_replacements,
            **kwargs,
        )

    def _init_sp_model(self, vocab_file: str = None) -> None:
        import sentencepiece  # pylint: disable=import-outside-toplevel

        self._sp_model = sentencepiece.SentencePieceProcessor()
        if vocab_file is None:
            return

        if _is_uri(vocab_file):
            vocab_file = _URIHandler(use_cache=True).map_to_local(vocab_file)
        self._sp_model.Load(str(vocab_file))

    def _register_sp_tokens(self, *new_tokens):
        current_vocab = self.get_vocab()
        new_tokens = [str(tok) for tok in new_tokens]
        new_tokens = [
            tok for tok in new_tokens if tok is not None and tok not in current_vocab
        ]
        if len(new_tokens) == 0:
            return
        new_tokens = list(dict.fromkeys(new_tokens))  # dedupe, preserving order
        _add_user_defined_tokens(self._sp_model, new_tokens)

    @property
    def vocab_size(self) -> int:
        return self._sp_model.get_piece_size()

    def get_vocab(self) -> _Dict[str, int]:
        return {
            self._sp_model.id_to_piece(token_id): token_id
            for token_id in range(self.vocab_size)
        }

    def add_tokens(
        self,
        new_tokens: _Union[_HFTokenType, _List[_HFTokenType]],
        special_tokens: bool = False,
        **kwargs,
    ) -> int:
        """
        Wraps :meth:`transformers.PreTrainedTokenizer.add_tokens` to also
        add the new tokens to the SentencePiece model's vocabulary.
        """
        if not isinstance(new_tokens, (list, tuple)):
            new_tokens = [new_tokens]
        self._register_sp_tokens(*new_tokens)
        return super().add_tokens(new_tokens, special_tokens=special_tokens, **kwargs)

    def prepare_for_tokenization(
        self, text: str, is_split_into_words: bool = False, **kwargs
    ) -> _Tuple[str, _Dict[str, _Any]]:
        """
        Performs string replacements prior to tokenization.  See
        :meth:`transformers.PreTrainedTokenizer.prepare_for_tokenization` for
        more info.
        """
        if self.text_replacements is not None:
            for old, new in self.text_replacements.items():
                text = text.replace(old, new)
        return text, kwargs

    @property
    def split_special_tokens(self) -> bool:
        """
        A flag that controls the :meth:`tokenize` behavior.  When ``False``,
        :meth:`tokenize` applies special treatment to special tokens.  This
        class forces the flag to ``True``.
        """
        return True

    @split_special_tokens.setter
    def split_special_tokens(self, value: bool) -> None:
        if not value:
            _warnings.warn(
                "split_special_tokens assigned to False in SentencePieceTokenizer, "
                "which is unsupported.  Forcing this value to True.  Please contact "
                "the tamm team if you require support for this feature."
            )

    def tokenize(self, text: str, **kwargs) -> _List[str]:
        """
        Wraps :meth:`transformers.tokenize` to force ``split_special_tokens=True``.

        Args:
            text (:obj:`str`): The text to tokenize.
            **kwargs: Keyword arguments for the wrapped
                :meth:`transformers.PreTrainedTokenizer.tokenize` method.
        """
        split_special_tokens = kwargs.pop("split_special_tokens", True)
        if not split_special_tokens:
            _warnings.warn(
                "SentencePieceTokenizer.tokenize() is ignoring False value for"
                "split_special_tokens, which is unsupported.  Please contact the"
                "tamm team if you require support for this feature."
            )
        result = super().tokenize(text, **kwargs)
        if (
            self._is_apply_chat_template_context
            and self.chat_template_strip_first_token
        ):
            result = result[1:]
        return result

    def __call__(self, *args, **kwargs):
        if self._is_apply_chat_template_context:
            kwargs["add_special_tokens"] = self.chat_template_add_special_tokens
        return super().__call__(*args, **kwargs)

    def build_inputs_with_special_tokens(
        self, token_ids_0: _List[int], token_ids_1: _Optional[_List[int]] = None
    ) -> _List[int]:
        prefix = []
        if self.add_bos_token:
            bos_id = self._convert_token_to_id(str(self.bos_token))
            prefix.append(bos_id)

        if prefix:
            token_ids_0 = prefix + token_ids_0

        if token_ids_1 is None:
            return token_ids_0

        return token_ids_0 + prefix + token_ids_1

    def get_special_tokens_mask(
        self,
        token_ids_0: _List[int],
        token_ids_1: _Optional[_List[int]] = None,
        already_has_special_tokens: bool = False,
    ) -> _List[int]:
        # Developer note (TJ): It's unclear to me how this is used within the HF ecosystem
        # (could not find an example easily).  This implementation follows LlamaTokenizer.

        if already_has_special_tokens:
            return super().get_special_tokens_mask(
                token_ids_0=token_ids_0,
                token_ids_1=token_ids_1,
                already_has_special_tokens=True,
            )
        sequences = [token_ids_0]
        if token_ids_1 is not None:
            sequences.append(token_ids_1)

        result = []
        for seq in sequences:
            if self.add_bos_token:
                result.append(1)
            result.extend([0] * len(seq))
        return result

    def _tokenize(self, text: str, **kwargs) -> _List[str]:
        return self._sp_model.encode_as_pieces(text)

    def _convert_token_to_id(self, token: str) -> int:
        return self._sp_model.piece_to_id(token)

    @_contextlib.contextmanager
    def _chat_template_context(self):
        original = self._is_apply_chat_template_context
        self._is_apply_chat_template_context = True
        yield
        self._is_apply_chat_template_context = original

    def apply_chat_template(self, *args, **kwargs):
        """
        Wraps :meth:`transformers.PreTrainedTokenizer.apply_chat_template` to
        pass additional ``tokenizer_kwargs`` to :meth:`.tokenize`.
        """
        with self._chat_template_context():
            return super().apply_chat_template(*args, **kwargs)

    def decode(
        self,
        token_ids: _Union[int, _List[int]],
        skip_special_tokens: bool = False,
        clean_up_tokenization_spaces: bool = None,
        **kwargs,
    ) -> str:
        """
        Wraps :meth:`transformers.PreTrainedTokenizer.decode` to
        apply string replacements after detokenization.
        """
        result = super().decode(
            token_ids,
            skip_special_tokens=skip_special_tokens,
            clean_up_tokenization_spaces=clean_up_tokenization_spaces,
            **kwargs,
        )
        if self.text_replacements is not None:
            for new, old in reversed(self.text_replacements.items()):
                result = result.replace(old, new)
        return result

    def convert_tokens_to_string(self, tokens: _List[str]) -> str:
        """
        Decodes a list of pieces to a string using the SentencePiece model.
        See :meth:`transformers.convert_tokens_to_string` for more info.
        """
        return self._sp_model.decode(tokens)

    def _convert_id_to_token(self, index: int) -> str:
        return self._sp_model.id_to_piece(index)

    def save_vocabulary(
        self, save_directory: str, filename_prefix: _Optional[str] = None
    ) -> _Tuple[str]:
        filename = self.vocab_files_names["vocab_file"]
        if filename_prefix is not None:
            filename = f"{filename_prefix}-{filename}"
        filepath = _os.path.join(save_directory, filename)
        file_contents = self._sp_model.serialized_model_proto()
        with open(filepath, "wb") as fp:
            fp.write(file_contents)
        return (filepath,)

    def __getstate__(self):
        state = self.__dict__.copy()
        state["_sp_model"] = None
        state["_sp_model_proto"] = self._sp_model.serialized_model_proto()
        return state

    def __setstate__(self, d):
        model_proto = d.pop("_sp_model_proto")
        self.__dict__.update(d)
        self._init_sp_model()
        self._sp_model.LoadFromSerializedProto(model_proto)
