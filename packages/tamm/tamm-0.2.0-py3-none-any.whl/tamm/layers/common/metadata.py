import dataclasses as _dataclasses
import logging as _logging
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Union as _Union

from tamm import _helpers
from tamm.preprocessors import Preprocessor
from tamm.tokenizers.common import TokenizerConfig
from tamm.utils.json import JSONSerializableMixin as _JSONSerializableMixin

_logger = _logging.getLogger(__name__)


def maybe_supersede_tokenizer_spec(new_cls: "ModuleMetadata") -> "ModuleMetadata":
    """
    Attempt to overwrite .tokenizer_spec with .preprocessor_spec.tokenizer_spec if
    `.preprocessor_spec.tokenizer_spec` is properly defined.

    Args:
        new_cls: A newly created :class:`ModuleMetadata`

    Returns: :class:`ModuleMetadata`

    """
    try:
        tokenizer_spec = new_cls.preprocessor_spec.tokenizer_spec
    except AttributeError:
        return new_cls
    if new_cls.tokenizer_spec is None:
        return _dataclasses.replace(new_cls, tokenizer_spec=tokenizer_spec)
    if tokenizer_spec == new_cls.tokenizer_spec:
        return new_cls

    _logger.warning(
        "`.preprocessor_spec.tokenizer_spec` supersedes `.tokenize_spec`"
        " for this ModuleMetadata. "
        "Ask model owner to address the discrepancy in model config. "
        "Set debug mode to see details."
    )
    _logger.debug(
        "model_metadata = %s",
        new_cls,
    )
    _logger.debug(
        "`.preprocessor_spec.tokenizer_spec` = %s",
        new_cls.preprocessor_spec.tokenizer_spec,
    )
    _logger.debug("`.tokenizer_spec` = %s", new_cls.tokenizer_spec)
    return _dataclasses.replace(new_cls, tokenizer_spec=tokenizer_spec)


@_dataclasses.dataclass(frozen=True, repr=False)
class ModuleMetadata(
    _helpers.DataClassReprMixin,
    _JSONSerializableMixin,
    json_namespace="module_metadata",
):
    tokenizer_spec: _Optional[_Union[str, "TokenizerConfig"]] = None
    preprocessor_spec: _Optional[
        _Union[_Dict[str, "Preprocessor"], str, "Preprocessor"]
    ] = None
    source_model_details: _Dict[str, _Any] = _dataclasses.field(default_factory=dict)
    source_model_tamm_id: _Optional[str] = None

    def _to_json_dict_impl(self):
        return _helpers.dataclass_to_dict(self, omit_defaults=True)

    @classmethod
    def _from_json_dict_impl(cls, **raw_dict: dict):
        new_cls = _helpers.dataclass_init_drop_missing_keys(
            raw_dict, dataclass_type=cls
        )
        new_cls = maybe_supersede_tokenizer_spec(new_cls)
        return new_cls

    @property
    def is_empty(self):
        return (
            len(self.source_model_details) == 0
            and self.tokenizer_spec is None
            and self.source_model_tamm_id is None
        )
