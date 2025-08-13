# pylint: disable=abstract-method

import abc as _abc
import warnings as _warnings
from typing import Optional as _Optional
from typing import Tuple as _Tuple

import torch as _torch
import transformers as _transformers
from transformers import modeling_outputs as _modeling_outputs

import tamm as _tamm
from tamm.hf.transformers import modeling_utils as _modeling_utils
from tamm.hf.transformers.helpers import is_cache_empty
from tamm.hf.transformers.models.causal_lm import kv_cache as _kv_cache
from tamm.hf.transformers.models.causal_lm.configuration_causal_lm import (
    TammCausalLMConfig as _TammCausalLMConfig,
)
from tamm.typing import StateDictType as _StateDictType


class TammCausalLMPreTrainedModel(_modeling_utils.PreTrainedModel):
    """
    A base class for wrapping |tamm| :class:`CausalLMTransformer` models
    into a HuggingFace model type.
    """

    config_class = _TammCausalLMConfig
    base_model_prefix = "transformer"
    supports_gradient_checkpointing = True
    _no_split_modules = ["TransformerDecoderLayer"]

    @classmethod
    def from_tamm_config(
        cls,
        config: _tamm.layers.ModuleConfig,
        state_dict: _Optional[_StateDictType] = None,
        **kwargs,
    ) -> "TammCausalLMPreTrainedModel":
        """
        Creates and returns a Hugging Face-compatible wrapper model.

        Args:
            config: A |tamm| model config for a :obj:`.CausalLMTransformer`.
            state_dict: An optional state dict for the model.  If ``None``,
                the model states are loaded from the config's pretrained path
                (if provided) and otherwise initialized from scratch.
            **kwargs: Optional keyword arguments to pass to
                :class:`TammCausalLMConfig`.
        """

        hf_config = _TammCausalLMConfig(tamm_config=config, **kwargs)
        with _torch.device("meta"):
            hf_model = cls(hf_config)

        if state_dict is None:
            tamm_model = config.create_model(pretrained=True)
            state_dict = tamm_model.state_dict()
        hf_model.get_tamm_model().load_state_dict(state_dict, assign=True)

        hf_model.tie_weights()

        return hf_model

    @classmethod
    def from_tamm_model(cls, model: _torch.nn.Module) -> "TammCausalLMPreTrainedModel":
        """
        Creates and returns a Hugging Face-compatible wrapper model.

        Args:
            model: The |tamm| model to wrap into a Hugging Face type.
        """

        hf_config = _TammCausalLMConfig()
        with _torch.device("meta"):
            hf_model = cls(hf_config)

        hf_model.set_tamm_model(model)

        hf_model.tie_weights()

        return hf_model

    @_abc.abstractmethod
    def get_tamm_model(self) -> _torch.nn.Module:
        """Get the underlying tamm model"""

    @_abc.abstractmethod
    def set_tamm_model(self, model: _torch.nn.Module) -> None:
        """Set the underlying tamm model"""

    def _init_weights(self, module):
        # Hugging Face calls this for every submodule
        if hasattr(module, "reset_parameters"):
            module.reset_parameters()

    def tie_weights(self):
        # pylint: disable=assignment-from-none
        model = self.get_tamm_model()
        should_tie = getattr(model, "is_embedding_tied_to_output_transform", False)
        if not should_tie:
            return

        output_embeddings = self.get_output_embeddings()
        if output_embeddings is None:
            return
        self._tie_or_clone_weights(output_embeddings, self.get_input_embeddings())

        for module in self.modules():
            if hasattr(module, "_tie_weights"):
                module._tie_weights()  # pylint: disable=protected-access

    def gradient_checkpointing_enable(self, gradient_checkpointing_kwargs=None):
        if gradient_checkpointing_kwargs is None:
            gradient_checkpointing_kwargs = {}
        tamm_model = self.get_tamm_model()
        for layer in tamm_model.layers.iter_transformer_layers():
            layer.checkpoint_activations(**gradient_checkpointing_kwargs)

    def gradient_checkpointing_disable(self):
        tamm_model = self.get_tamm_model()
        for layer in tamm_model.layers.iter_transformer_layers():
            layer.store_activations()

    def _maybe_warn_about_ignored_args_to_forward(self, **ignored_args):
        output_attentions = ignored_args.pop("output_attentions", False)
        if output_attentions and not self.config.output_attentions:
            _warnings.warn(
                "CausalLM forward() will ignore output_attentions=True. Please "
                "pass output_attentions=True instead to the tamm model config."
            )
        output_hidden_states = ignored_args.pop("output_hidden_states", False)
        if output_hidden_states and not self.config.output_hidden_states:
            _warnings.warn(
                "CausalLM forward() will ignore output_hidden_states=True. Please "
                "pass output_hidden_states=True instead to the tamm model config."
            )
        for key, value in ignored_args.items():
            if value is None:
                continue
            _warnings.warn(
                f"The CausalLM forward() method received a value for {key}, but "
                "this arg will be ignored.  Please contact the tamm developers "
                "to prioritize support for this feature."
            )

    def _should_use_return_dict(self, return_dict):
        return self.config.use_return_dict if return_dict is None else return_dict


class TammCausalLMModel(TammCausalLMPreTrainedModel):
    def __init__(self, config: _TammCausalLMConfig):
        super().__init__(config)
        self.config = config
        self.tamm_model = None

        if config.tamm_config is not None:
            tamm_model = config.tamm_config.create_model()
        else:
            _warnings.warn("TammCausalLMModel created without a tamm model")
            tamm_model = None
        self.set_tamm_model(tamm_model)

        self.post_init()

    def get_tamm_model(self) -> _torch.nn.Module:
        return self.tamm_model

    def set_tamm_model(self, model: _torch.nn.Module) -> None:
        self.tamm_model = model

    def get_input_embeddings(self):
        return self.tamm_model.embedding

    def set_input_embeddings(self, value):
        self.tamm_model.embedding = value

    def forward(
        self,
        input_ids=None,
        *,
        attention_mask=None,
        past_key_values: _Optional[_Tuple[_Tuple[_torch.Tensor]]] = None,
        inputs_embeds: _Optional[_torch.FloatTensor] = None,
        use_cache: _Optional[bool] = None,
        return_dict=None,
        **ignored_args,
    ):
        self._maybe_warn_about_ignored_args_to_forward(**ignored_args)
        inputs, mode = self._get_inputs_and_mode_for_forward(
            input_ids=input_ids, inputs_embeds=inputs_embeds
        )
        if attention_mask is None:
            attention_mask = _torch.ones(
                *inputs.shape[:2], dtype=_torch.int32, device=inputs.device
            )
        kv_cache_view = self._get_kv_cache_view(
            past_key_values=past_key_values,
            attention_mask=attention_mask,
            use_cache=use_cache,
        )
        if use_cache:
            attention_mask = attention_mask[:, -inputs.size(1) :]
        output = self.tamm_model(
            inputs,
            segment_ids=attention_mask,
            kv_cache=kv_cache_view,
            mode=mode,
        )
        return self._create_forward_return_value(
            tamm_output=output,
            kv_cache_view=kv_cache_view,
            return_dict=return_dict,
        )

    @staticmethod
    def _get_inputs_and_mode_for_forward(*, input_ids, inputs_embeds):
        if input_ids is not None:
            if inputs_embeds is not None:
                raise ValueError("Forward received both input_ids and inputs_embeds")
            return (
                input_ids,
                "skip_output_layer",
            )  # Hugging Face uses a separate LM head layer
        if inputs_embeds is not None:
            return (inputs_embeds, "skip_embedding_and_output_layers")
        raise ValueError("Forward received neither input_ids nor inputs_embeds")

    def _get_kv_cache_view(self, *, past_key_values, attention_mask, use_cache):
        if not use_cache:
            return None
        positions = attention_mask.cumsum(dim=1).sub_(1).clamp_min_(0)
        if is_cache_empty(past_key_values):
            num_layers = self.get_tamm_model().num_layers
            return _kv_cache.HFStyleKVCacheView.create_empty_cache(
                num_layers=num_layers, segment_ids=attention_mask, positions=positions
            )
        return _kv_cache.HFStyleKVCacheView(
            past_key_values, segment_ids=attention_mask, positions=positions
        )

    def _create_forward_return_value(
        self,
        *,
        tamm_output,
        kv_cache_view: _kv_cache.HFStyleKVCacheView,
        return_dict: bool,
    ):
        if kv_cache_view is not None:
            past_key_values = kv_cache_view.past_key_values
        else:
            past_key_values = None

        output = {
            "last_hidden_state": tamm_output.last_hidden_state,
            "hidden_states": tamm_output.hidden_states,
            "attentions": tamm_output.attentions,
            "past_key_values": past_key_values,
        }

        if not self._should_use_return_dict(return_dict):
            return tuple(val for val in output.values() if val is not None)
        return _modeling_outputs.BaseModelOutputWithPast(**output)

    def _reorder_cache(
        self, past_key_values: _Tuple[_Tuple[_torch.Tensor]], beam_idx: _torch.Tensor
    ):
        beam_idx = beam_idx.to(past_key_values[0][0].device)
        return tuple(
            tuple(tensor.index_select(0, beam_idx) for tensor in layer)
            for layer in past_key_values
        )


class TammCausalLMForCausalLM(
    TammCausalLMPreTrainedModel, _transformers.GenerationMixin
):
    def __init__(self, config: _TammCausalLMConfig):
        super().__init__(config)
        self.transformer = TammCausalLMModel(config)

        self.lm_head = None
        if self.get_tamm_model() is not None:
            self._init_lm_head()

        self.post_init()

    def _init_lm_head(self):
        model = self.get_tamm_model()
        if model is None:
            self.lm_head = None
            return

        output_transform = model.output_transform
        hidden_dim = output_transform.in_features
        vocab_size = output_transform.out_features
        device = output_transform.weight.device
        dtype = output_transform.weight.dtype

        self.lm_head = _torch.nn.Linear(
            hidden_dim, vocab_size, bias=False, device=device, dtype=dtype
        )
        self.lm_head.load_state_dict(output_transform.state_dict())

    @property
    def _tied_weights_keys(self):
        keys = [*super()._tied_weights_keys]

        model = self.get_tamm_model()
        try:
            has_tied_embedding = self.lm_head.weight is model.embedding.weight
        except AttributeError:
            has_tied_embedding = False

        if has_tied_embedding:
            keys.append("lm_head.weight")

        return keys

    def get_tamm_model(self) -> _torch.nn.Module:
        return self.transformer.get_tamm_model()

    def set_tamm_model(self, model: _torch.nn.Module) -> None:
        self.transformer.set_tamm_model(model)
        self._init_lm_head()
        self._maybe_update_generation_config()

    def _maybe_update_generation_config(self):
        if self.generation_config is None:
            return
        tamm_model = self.get_tamm_model()
        if tamm_model is None:
            return
        try:
            tokenizer = _tamm.create_tokenizer(tamm_model.metadata.tokenizer_spec)
        except Exception:
            _warnings.warn(
                "Could not create a tokenizer to update the HuggingFace generation config. If "
                "generating text, please ensure that the eos_token_id and pad_token_id are set correctly."
            )
            return

        if hasattr(tokenizer, "bos_id"):
            self.generation_config.bos_token_id = tokenizer.bos_id

        if hasattr(tokenizer, "eot_id"):
            self.generation_config.eos_token_id = tokenizer.eot_id
        elif hasattr(tokenizer, "eos_id"):
            self.generation_config.eos_token_id = tokenizer.eos_id
        else:
            _warnings.warn(
                "Could not update the eos_token_id in the HuggingFace generation config. "
                "If generating text, please ensure that the eos_id is set correctly."
            )

        if hasattr(tokenizer, "pad_id"):
            self.generation_config.pad_token_id = tokenizer.pad_id
        else:
            _warnings.warn(
                "Could not update the pad_token_id in the HuggingFace generation config. "
                "If generating text, please ensure that the pad id is set correctly."
            )

    def get_output_embeddings(self):
        return self.lm_head

    def set_output_embeddings(self, new_embeddings):
        self.lm_head = new_embeddings

    def prepare_inputs_for_generation(
        self,
        input_ids: _torch.LongTensor,
        past_key_values: _Optional[_Tuple[_Tuple[_torch.Tensor]]] = None,
        attention_mask: _Optional[_torch.Tensor] = None,
        inputs_embeds: _Optional[_torch.FloatTensor] = None,
        cache_position: _Optional[_torch.LongTensor] = None,
        **kwargs,
    ):
        try:
            return super().prepare_inputs_for_generation(
                input_ids=input_ids,
                past_key_values=past_key_values,
                attention_mask=attention_mask,
                inputs_embeds=inputs_embeds,
                cache_position=cache_position,
                **kwargs,
            )
        except NotImplementedError:
            # transformers.GenerationMixin only implements this method since
            # v4.46--when not implemented, fall back to old implementation
            pass

        if past_key_values is not None:
            input_ids = input_ids[:, -1:]

        if inputs_embeds is not None:
            if past_key_values is None:
                input_ids = None
            else:
                inputs_embeds = None

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "past_key_values": past_key_values,
            "inputs_embeds": inputs_embeds,
            "cache_position": cache_position,
            **kwargs,
        }

    def forward(
        self,
        input_ids: _Optional[_torch.Tensor] = None,
        *,
        attention_mask: _Optional[_torch.Tensor] = None,
        inputs_embeds: _Optional[_torch.FloatTensor] = None,
        past_key_values: _Optional[_Tuple[_Tuple[_torch.Tensor]]] = None,
        use_cache: _Optional[bool] = None,
        labels=None,
        return_dict=None,
        **ignored_args,
    ):
        self._maybe_warn_about_ignored_args_to_forward(**ignored_args)
        backbone_output = self.transformer(
            input_ids,
            attention_mask=attention_mask,
            inputs_embeds=inputs_embeds,
            past_key_values=past_key_values,
            use_cache=use_cache,
            return_dict=True,
        )
        logits = self.lm_head(backbone_output.last_hidden_state)
        loss = self._compute_loss(logits, labels)
        return self._create_forward_return_value(
            backbone_output=backbone_output,
            logits=logits,
            loss=loss,
            return_dict=return_dict,
        )

    @staticmethod
    def _compute_loss(logits, labels):
        if labels is None:
            return None
        logits = logits[..., :-1, :]
        labels = labels[..., 1:]
        logits = logits.reshape(-1, logits.shape[-1])
        labels = labels.flatten()
        return _torch.nn.functional.cross_entropy(logits, labels)

    def _create_forward_return_value(
        self, *, backbone_output, logits, loss, return_dict
    ):
        output = {
            "loss": loss,
            "logits": logits,
            "hidden_states": backbone_output.hidden_states,
            "attentions": backbone_output.attentions,
            "past_key_values": backbone_output.past_key_values,
        }
        if not self._should_use_return_dict(return_dict):
            return tuple(val for val in output.values() if val is not None)
        return _modeling_outputs.CausalLMOutputWithPast(**output)

    def _reorder_cache(
        self, past_key_values: _Tuple[_Tuple[_torch.Tensor]], beam_idx: _torch.Tensor
    ):
        # pylint: disable-next=protected-access
        return self.transformer._reorder_cache(past_key_values, beam_idx)
