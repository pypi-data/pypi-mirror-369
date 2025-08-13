"""HF transformers model configuration for tamm wrappers"""

import json as _json
from typing import Optional as _Optional

from transformers import configuration_utils as _configuration_utils

import tamm as _tamm


class TammPretrainedConfig(_configuration_utils.PretrainedConfig):
    def __init__(
        self, tamm_config: _Optional[_tamm.layers.ModuleConfig] = None, **kwargs
    ):
        """
        HuggingFace transformers config for wrapper |tamm| models.

        Args:
            tamm_config (:obj:`ModelConfig`): The config for the |tamm| model.
            **kwargs: Keyword arguments for Hugging Face default options.
        """
        super().__init__(**kwargs)
        self.tamm_config = tamm_config

    def to_dict(self):
        return self._to_dict_impl(omit_defaults=False)

    def to_diff_dict(self):
        return self._to_dict_impl(omit_defaults=True)

    def _to_dict_impl(self, omit_defaults):
        tamm_config = self.tamm_config
        self.tamm_config = None

        result = super().to_diff_dict() if omit_defaults else super().to_dict()

        tamm_json = _tamm.utils.json.dumps(tamm_config)
        tamm_dict = _json.loads(tamm_json)
        result["tamm_config"] = tamm_dict

        self.tamm_config = tamm_config

        return result

    @classmethod
    def from_dict(cls, config_dict, **kwargs):
        tamm_dict = config_dict.get("tamm_config")
        if tamm_dict is not None:
            config_dict = config_dict.copy()
            tamm_json = _json.dumps(tamm_dict)
            tamm_config = _tamm.utils.json.loads(tamm_json)
            config_dict["tamm_config"] = tamm_config
        return super().from_dict(config_dict, **kwargs)

    @classmethod
    def from_json_file(cls, json_file):
        with open(json_file, "r", encoding="utf-8") as reader:
            text = reader.read()
        config_dict = _json.loads(text)
        return cls.from_dict(config_dict)
