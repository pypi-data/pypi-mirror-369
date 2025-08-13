import dataclasses as _dataclasses
import enum as _enum
from typing import Dict as _Dict
from typing import Iterable, List, Union

from tamm._helpers import case_insensitive_lookup as _case_insensitive_lookup
from tamm.utils import partial as _partial
from tamm.utils.json import JSONSerializableMixin as _JSONSerializableMixin

# pylint: disable=duplicate-code


class TextProcessorConfig(
    _partial.DataclassedPartial,
    _JSONSerializableMixin,
    json_namespace="text_processors",
):
    # pylint:disable=useless-parent-delegation
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_text_processor(self, *override_args, **override_kwargs):
        """
        Creates and returns a configured instance of the text processor.

        Args:
            override_args: Optional positional arguments to override args specified in
                the config.  These args replace the first ``len(override_args)``
                positional args.
            override_kwargs: Optional keyword override arguments.  These arguments
                replace any additional named arguments not overriden by
                ``override_args``.

        Returns:
            The newly created tokenizer.
        """
        return self(*override_args, **override_kwargs)

    def _to_json_dict_impl(self):
        result = {}
        for field in _dataclasses.fields(self.configured_args):
            value = getattr(self.configured_args, field.name)
            if value == field.default:
                continue
            result[field.name] = value
        return result


class TextProcessor:
    """
    Text processor class for pre-processing methods to be applied on a text before
    calling Tokenizer.
    """

    def _process(self, text: str) -> str:
        """
        Apply pre-processing on a single piece of text.
        """
        raise NotImplementedError()

    def process(self, texts: Union[str, Iterable[str]]) -> Union[str, List[str]]:
        """
        Apply pre-processing on a single piece of text or an iterable of texts.
        """
        if isinstance(texts, str):
            return self._process(texts)

        if issubclass(type(texts), Iterable):
            return [self._process(text) for text in texts]

        raise TypeError("Input must be a string or a list of strings")

    def _inverse(self, text: str) -> str:
        """
        Revert the effects of pre-processing on a single piece of text.
        """
        raise NotImplementedError()

    def inverse(self, texts: Union[str, Iterable[str]]) -> Union[str, List[str]]:
        """
        Revert the effects of pre-processing on a single piece of text or an
        iterable of texts.
        """
        if isinstance(texts, str):
            return self._inverse(texts)

        if issubclass(type(texts), Iterable):
            return [self._inverse(text) for text in texts]

        raise TypeError("Input must be a string or an iterable of strings")

    def __init_subclass__(cls):
        text_processor_name = cls.__name__
        config_name = f"{text_processor_name}Config"
        config_cls = TextProcessorConfig.create_subclass(
            target_callable=cls, name=config_name
        )
        config_cls.__doc__ = (
            f"A :py:class:`.TextProcessorBase` subclass for configuring "
            f":py:class:`.{text_processor_name}` text processor. "
            f"Use the alias :attr:`.{text_processor_name}.Config` to access this class. "
            f"Please check :class:`.{text_processor_name}` for more details about the "
            "signature."
        )
        cls.Config = config_cls


class FindAndReplaceTextProcessor(TextProcessor):
    """
    Handles text preprocessing by replacing substrings with specified replacements.
    """

    def __init__(self, replacements: _Dict[str, str]):
        self.replacements = dict(replacements)

    def _process(self, text: str) -> str:
        """Applies text replacements on a given text."""
        for search, repl in self.replacements.items():
            text = text.replace(search, repl)
        return text

    def _inverse(self, text: str) -> str:
        """Revert the effects of pre-processing on a given text."""
        for original, repl in reversed(self.replacements.items()):
            text = text.replace(repl, original)
        return text


class TextProcessorMode(str, _enum.Enum):
    #: FindAndReplaceTextProcessor with replacements={"\n": "<n>"}
    AFM_TEXT_FIND_AND_REPLACE = "AFM_TEXT_FIND_AND_REPLACE"

    @classmethod
    def _missing_(cls, value):
        return _case_insensitive_lookup(cls, value)
