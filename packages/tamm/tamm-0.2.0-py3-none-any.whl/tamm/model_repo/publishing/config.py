import dataclasses as _dataclasses
from typing import TYPE_CHECKING, Optional

from tamm import _helpers
from tamm.utils.json import JSONSerializableMixin as _JSONSerializableMixin

if TYPE_CHECKING:
    from tamm.layers import ModuleConfig


@_dataclasses.dataclass
class PublishedModelConfig(  # type: ignore[call-arg]
    _JSONSerializableMixin, json_namespace="model_repo"
):
    """
    Use the following :class:`tamm.models.AFMText`
    example to create a :class:`.PublishedModelConfig` (same process applies to
    any model supported by |tamm| and |tamm|-plugins):

    .. code-block:: python

        import tamm.models
        from tamm import adapters as _adapters
        import tamm.utils.json as tamm_json
        from tamm.model_repo import PublishedModelConfig

        config = tamm.models.AFMText.Config()
        # fill in fields by modifying the example below
        config.num_layers = 8
        config.adapters = {"my_lora_adapter":
            _adapters.LoRAModelAdapter(
            rank=rank,
            alpha=alpha,
            adapt_attention_queries=adapt_q,
            adapt_attention_keys=adapt_k,
            adapt_attention_values=adapt_v,
            adapt_attention_outputs=True,
            adapt_feed_forward_hidden_states=True,
            adapt_feed_forward_outputs=True,
            dropout_p=lora_dropout_p,
            pretrained_path=lora_pretrained_path,
        )}

        # PublishedModelConfig which includes model ID,
        # description and deprecation info are required for publishing.
        published_config = PublishedModelConfig(
                model_config=config,
                model_id="model_xyz",
                description="model_xyz has 1T parameters, 8 layers, and LoRA adapter",
                # the following 2 attributes are optional
                is_deprecated=True,
                replacement_model_id="model_superseding_xyz",
            )

        with open("config.json", "w") as f:
            tamm_json.dump(published_config, f)
        # share config.json with people who want to use this model
    """

    model_config: "ModuleConfig"
    model_id: str
    is_deprecated: bool = False
    replacement_model_id: Optional[str] = None
    description: str = ""

    def __lt__(self, other):
        return self.model_id < other.model_id

    def _to_json_dict_impl(self):
        return _helpers.dataclass_to_dict(self, omit_defaults=True)

    @classmethod
    def _from_json_dict_impl(cls, **raw_dict: dict):
        return _helpers.dataclass_init_drop_missing_keys(raw_dict, dataclass_type=cls)
