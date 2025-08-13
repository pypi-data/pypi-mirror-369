import functools as _functools
import json as _json
import warnings as _warnings
from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional

from tamm import tokenizers as _tokenizers
from tamm.preprocessors import base as _base
from tamm.preprocessors.instruct_lm import common as _common
from tamm.typing import LenientOptionalBool as _LenientOptionalBool
from tamm.utils import OptionalBool as _OptionalBool

DEFAULT_SYSTEM_MESSAGE = "A conversation between a user and a helpful assistant."
SYSTEM_ROLE = "system"


class JinjaChatTemplatePreprocessor(_base.Preprocessor):
    """
    An instruct LM preprocessor that uses Jinja for chat templating,
    similar to Hugging Face tokenizers.

    Args:
        tokenizer_spec: An argument to :func:`tamm.create_tokenizer` for
            creating a text tokenizer.
        chat_template (:obj:`str`): A Jinja template for preparing inputs
            to the tokenizer.  The template can accept ``messages`` and
            ``tools`` passed to :meth:`__call__` as well as an
            ``add_generation_prompt`` flag and ``target_role`` string.
        generate_prefix (:obj:`bool`): A flag for appending tokens to
            indicate the start of a response.  Typically this value is
            ``False`` during training and ``True`` during inference.
            Defaults to ``False``.
        max_sequence_length (:obj:`int`, optional): An optional max length
            for the preprocessed sequence.  If not ``None``, the
            preprocessor drops any tokens beyond this length.  This only
            applies when ``generate_prefix`` is ``False``. Defaults to
            ``None``.
        prepend_system_message (:obj:`bool`): A flag for prepending a system
            message to the input messages.  Set to ``False`` to pass a system
            message when calling the preprocessor.  Defaults to ``True``.
        system_message (:obj:`str`): A system message for providing the
            assistant with context or instructions for the conversation.
            Defaults to
            ``"A conversation between a user and a helpful assistant."``.
        strip_first_token (:obj:`bool`): A flag for stripping the first
            token from the output of the tokenizer.  Defaults to ``False``.
        prepend_eos (:obj:`bool`): A flag for prepending an EOS token id
            to the result.  Defaults to ``False``.
        target_role (:obj:`str`): The role name of the assistant.  Defaults
            to ``"assistant"``.
        ignored_id (:obj:`int`): The label ID for tokens that should be
            ignored during loss calculation.  Defaults to ``-100``.
    """

    def __init__(
        self,
        tokenizer_spec: _tokenizers.TokenizerSpecType,
        chat_template: str,
        generate_prefix: bool = False,
        max_sequence_length: _Optional[int] = None,
        prepend_system_message: bool = True,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        strip_first_token: bool = False,
        prepend_eos: bool = False,
        target_role: str = "assistant",
        ignored_id: int = -100,
    ):
        self.tokenizer_spec = tokenizer_spec
        self.chat_template = chat_template
        self.generate_prefix = generate_prefix
        self.max_sequence_length = max_sequence_length

        self.prepend_system_message = prepend_system_message
        if system_message is None:
            system_message = DEFAULT_SYSTEM_MESSAGE
        self.system_message = system_message

        self.prepend_eos = prepend_eos
        self.strip_first_token = strip_first_token

        self.target_role = target_role
        self.ignored_id = ignored_id

    @_functools.cached_property
    def tokenizer(self) -> _tokenizers.common.Tokenizer:
        """The tokenizer used by the preprocessor."""
        return _tokenizers.create_tokenizer(self.tokenizer_spec)

    @_functools.cached_property
    def _jinja_chat_template(self):
        # pylint: disable-next=import-outside-toplevel
        from jinja2 import sandbox as _jinja2_sandbox

        env = _jinja2_sandbox.ImmutableSandboxedEnvironment(
            trim_blocks=True, lstrip_blocks=True
        )
        env.filters["tojson"] = self._jinja_to_json
        return env.from_string(self.chat_template)

    @staticmethod
    def _jinja_to_json(value, indent=None):
        return _json.dumps(value, indent=indent, ensure_ascii=False)

    @_functools.cached_property
    def _target_role_generation_prefix(self) -> _List[int]:
        """
        Returns a list of token ids that signifies the start of a message
        from the target role (assistant).
        """
        messages = [
            {"role": SYSTEM_ROLE, "content": "A conversation"},
        ]
        if self.target_role != "user":
            messages.append({"role": "user", "content": "Hello"})

        chat_no_generation_prefix = self._jinja_chat_template.render(messages=messages)
        tokens_no_generation_prefix = self.tokenizer.encode(chat_no_generation_prefix)

        chat_with_generation_prefix = self._jinja_chat_template.render(
            messages=messages,
            target_role=self.target_role,
            add_generation_prompt=True,
        )
        tokens_with_generation_prefix = self.tokenizer.encode(
            chat_with_generation_prefix
        )
        return tokens_with_generation_prefix[len(tokens_no_generation_prefix) :]

    def __call__(
        self,
        messages: _List[_Dict[str, str]],
        *,
        generate_prefix: _LenientOptionalBool = _OptionalBool.NOTSET,
        tools: _Optional[_List[_Dict[str, _Any]]] = None,
    ):
        """
        Preprocesses a list of raw messages.

        Args:
            messages (:obj:`list`): The list of messages to pass to
                the Jinja template.  Each message must be a :obj:`dict`
                that contains at minimum ``"role"`` and ``"content"``
                keys.
            tools (:obj:`list`): A list of tool definitions to pass
                to the Jinja template.
            generate_prefix (:obj:`bool`, optional): An optional
                flag for overriding the preprocessor's
                ``generate_prefix`` option.  Typically ``True`` for
                inference and ``False`` for training.

        Returns: A :obj:`InstructLMPreprocessorOutput` that contains the
            tokenized ``input_ids`` and also ``label_ids``.  The labels
            are ``None`` when the input ``messages`` do not contain
            content from the preprocessor's target role.
            Otherwise the labels contain content from the target role
            for training or evaluation.
        """

        if len(messages) == 0:
            raise ValueError("Input must contain at least one message")
        if generate_prefix is _OptionalBool.NOTSET:
            generate_prefix = self.generate_prefix

        messages = self.maybe_prepend_system_message(messages)
        messages = [self.maybe_update_message(message) for message in messages]

        if tools is not None and messages[0]["role"] != SYSTEM_ROLE:
            raise ValueError(
                "When using tools, the first message must be a system "
                f"message but instead it is {messages[0]}"
            )
        if not generate_prefix:
            self._validate_messages_contain_target_role(messages)

        text = self._jinja_chat_template.render(
            messages=messages,
            target_role=self.target_role,
            tools=tools,
            add_generation_prompt=generate_prefix,
        )

        token_ids = self.tokenizer.encode(text)
        if self.strip_first_token:
            token_ids = token_ids[1:]
        if self.prepend_eos:
            token_ids = [self.tokenizer.eos_id] + token_ids

        input_ids, label_ids = self._create_input_and_label_ids_from_token_ids(
            token_ids=token_ids,
            messages=messages,
            generate_prefix=generate_prefix,
        )

        return _common.InstructLMPreprocessorOutput(
            input_ids=input_ids, label_ids=label_ids
        )

    def maybe_prepend_system_message(self, messages):
        if any(message["role"] == SYSTEM_ROLE for message in messages):
            if messages[0]["role"] != SYSTEM_ROLE:
                raise ValueError(f"System is not the first role in messages {messages}")
            if self.prepend_system_message:
                raise ValueError(
                    "prepend_system_message is True, but messages already contains a system "
                    f"message: {messages}"
                )
        elif self.prepend_system_message:
            if len(self.system_message) == 0:
                _warnings.warn(
                    "System message is empty; please set prepend_system_message=False to avoid "
                    "prepending a system message"
                )
            elif self.system_message[0] == " " or self.system_message[-1] == " ":
                raise ValueError(
                    "Custom system message should not start or end with a space but "
                    f"system_message='{self.system_message}'"
                )
            messages = [
                {"role": SYSTEM_ROLE, "content": self.system_message}
            ] + messages
        else:
            _warnings.warn(
                "No system message found but not prepending a system message because "
                "prepend_system_message is False"
            )
        return messages

    def maybe_update_message(self, message: _Dict[str, _Any]) -> _Dict[str, _Any]:
        """
        A helper function that provides subclasses a way to preprocess messages
        in Python prior to Jinja template rendering.
        """
        return message

    def _validate_messages_contain_target_role(self, messages):
        if any(self.target_role == msg["role"] for msg in messages):
            return
        raise ValueError(
            f"Target role '{self.target_role}' is missing from messages "
            f"(if the preprocessing is for {self.target_role} generation, please "
            "set generate_prefix=True)"
        )

    def _create_input_and_label_ids_from_token_ids(
        self, *, token_ids, messages, generate_prefix
    ):
        # pylint: disable=too-many-locals
        if generate_prefix and messages[-1]["role"] != self.target_role:
            # In this case (inference), there are no labels
            return token_ids, None

        generation_prefix = self._target_role_generation_prefix
        generation_prefix = "".join(f",{i}" for i in generation_prefix)

        if generate_prefix:
            # In this case (inference), the last message serves as the labels
            str_token_ids = "".join(f",{i}" for i in token_ids)
            eot_and_prefix = "," + str(self.tokenizer.eot_id) + generation_prefix
            str_labels_ids = str_token_ids.rsplit(eot_and_prefix, maxsplit=1)[-1]
            num_labels = str_labels_ids.count(",")
            return token_ids[:-num_labels], token_ids[-num_labels:]

        label_ids = []
        start_idx = 0
        for message in messages:
            try:
                end_idx = token_ids.index(self.tokenizer.eot_id, start_idx) + 1
            except ValueError:
                end_idx = len(token_ids)

            if message["role"] != self.target_role:
                # Use ignore label ids for non-target role
                label_ids.extend([self.ignored_id] * (end_idx - start_idx))
            else:
                # Extract content as labels for target role
                subsequence = token_ids[start_idx:end_idx]
                str_subsequence = "".join(f",{i}" for i in subsequence)
                labels_part = str_subsequence.split(generation_prefix, maxsplit=1)[-1]
                num_labels = labels_part.count(",")
                num_ignore = len(subsequence) - num_labels
                label_ids.extend([self.ignored_id] * num_ignore)
                label_ids.extend(subsequence[-num_labels:])

            start_idx = end_idx

        # Shift labels
        label_ids.append(self.ignored_id)
        label_ids = label_ids[1:]

        if self.max_sequence_length is not None:
            token_ids = token_ids[: self.max_sequence_length]
            label_ids = label_ids[: self.max_sequence_length]

        return token_ids, label_ids
