import dataclasses as _dataclasses
from typing import Iterable as _Iterable
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

from tamm import _helpers
from tamm.utils import partial as _partial
from tamm.utils.json import JSONSerializableMixin as _JSONSerializableMixin


class Tokenizer:
    """
    Base tokenizer class contains basic API for LM tokenization.
    """

    def __len__(self) -> int:
        raise NotImplementedError

    def encode(
        self, texts: _Union[str, _Iterable[str]], **kwargs
    ) -> _Union[_Iterable[int], _Iterable[_Iterable[int]]]:
        raise NotImplementedError

    def decode(
        self,
        token_ids: _Union[int, _Iterable[int], _Iterable[_Iterable[int]]],
        **kwargs,
    ) -> _Union[str, _Iterable[str]]:
        raise NotImplementedError

    def encode_as_pieces(
        self, texts: _Union[str, _Iterable[str]], **kwargs
    ) -> _Union[_List[str], _List[_List[str]]]:
        raise NotImplementedError

    @property
    def eos_id(self) -> int:
        raise NotImplementedError

    @property
    def pad_id(self) -> int:
        raise NotImplementedError

    @property
    def unk_id(self) -> int:
        raise NotImplementedError

    def __init_subclass__(cls):
        tokenizer_name = cls.__name__
        config_name = f"{tokenizer_name}Config"
        config_cls = TokenizerConfig.create_subclass(
            target_callable=cls, name=config_name
        )
        config_cls.__doc__ = (
            f"A :py:class:`.TokenizerConfig` subclass for configuring "
            f":py:class:`.{tokenizer_name}` tokenizer.  Use the alias :attr:`."
            f"{tokenizer_name}.Config` to access this class. "
            f"Please check :class:`.{tokenizer_name}` for more details about the "
            "signature."
        )
        cls.Config = config_cls


class TokenizerConfig(
    _partial.DataclassedPartial,
    _JSONSerializableMixin,
    json_namespace="tokenizers",
):
    # pylint:disable=useless-parent-delegation
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_tokenizer(self, *override_args, **override_kwargs):
        """
        Creates and returns a configured instance of the tokenizer.

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


@_dataclasses.dataclass
class PublishedTokenizerConfig(_JSONSerializableMixin, json_namespace="tokenizer_repo"):
    tokenizer_config: TokenizerConfig
    tokenizer_id: int
    is_deprecated: bool = False
    description: _Optional[str] = None

    def _to_json_dict_impl(self):
        return _helpers.dataclass_to_dict(self, omit_defaults=True)

    @classmethod
    def _from_json_dict_impl(cls, **raw_dict: dict):
        return _helpers.dataclass_init_drop_missing_keys(raw_dict, dataclass_type=cls)
