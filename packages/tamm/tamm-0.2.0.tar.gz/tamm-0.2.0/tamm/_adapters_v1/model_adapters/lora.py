"""
_adapters_v1.model_adapters.lora
================================

.. autoclass:: tamm._adapters_v1.model_adapters.lora.LoRAModelAdapter
    :show-inheritance:
    :members:
"""

# pylint: disable=no-member, cyclic-import

import logging as _logging
import warnings as _warnings
from collections import OrderedDict as _OrderedDict
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch.nn as _nn

from tamm._adapters_v1 import layer_annotations as _annotations
from tamm._adapters_v1.adapted_layer import AdaptedLayer as _AdaptedLayer
from tamm._adapters_v1.layer_adapters import BatchedLoRA as _BatchedLoRA
from tamm._adapters_v1.layer_adapters import (
    BatchedLoRAFusedMultiOutputLinear as _BatchedLoRAFusedMultiOutputLinear,
)
from tamm._adapters_v1.layer_adapters import LoRA as _LoRA
from tamm._adapters_v1.layer_adapters import (
    LoRAFusedMultiOutputLinear as _LoRAFusedMultiOutputLinear,
)
from tamm._adapters_v1.layer_adapters.common import LayerAdapter as _LayerAdapter
from tamm._adapters_v1.layer_adapters.soft_mixing_lora import (
    SoftMixingLoRA as _SoftMixingLoRA,
)
from tamm._adapters_v1.layer_adapters.stack import (
    StackedOutputTransforms as _StackedOutputTransforms,
)
from tamm._adapters_v1.layer_annotations import LayerAnnotation as _LayerAnnotation
from tamm._adapters_v1.layer_annotations import (
    get_layer_annotations as _get_layer_annotations,
)
from tamm._adapters_v1.model_adapters.composition import (
    CompositeModelAdapterMixin as _CompositeModelAdapterMixin,
)
from tamm._adapters_v1.model_adapters.model_adapter import AdapterSpec as _AdapterSpec
from tamm._adapters_v1.model_adapters.model_adapter import ModelAdapter as _ModelAdapter

_logger = _logging.getLogger(__name__)


class LoRAModelAdapter(_ModelAdapter):
    """
    A model adapter which inserts :class:`_LoRA`
    and :class:`_LoRAFusedMultiOutputLinear` layers in a decoder only transformer model.
    """

    # pylint: disable=duplicate-code

    rank: int = 8
    alpha: _Optional[float] = None
    adapt_attention_queries: bool = True
    adapt_attention_keys: bool = True
    adapt_attention_values: bool = True
    adapt_attention_outputs: bool = True
    adapt_feed_forward_hidden_states: bool = True
    adapt_feed_forward_outputs: bool = True
    adapt_moe: bool = True
    dropout_p: float = 0
    layer_prefix: str = "layers.layer_"
    layer_pattern: _Optional[_Union[str, _List]] = None

    def _get_lora_linear_layer_type(
        self, layer_type: _List[_LayerAnnotation]
    ) -> _Tuple[_Optional[_LayerAnnotation], bool]:
        """
        Tests if the annotations match any of the supported layer annotation
        types for LoRA and if the config allows that layer type to be adapted.

        Returns the type of layer annotation and a boolean indicating
        if the layer is annotated with a batched layer annotation type.
        """
        masks = [
            self.adapt_attention_outputs,
            self.adapt_attention_queries,
            self.adapt_attention_keys,
            self.adapt_attention_values,
            self.adapt_feed_forward_hidden_states,
            self.adapt_feed_forward_outputs,
        ]
        annotation_types = [
            _annotations.AttentionOutputTransform,
            _annotations.AttentionInputTransformQuery,
            _annotations.AttentionInputTransformKey,
            _annotations.AttentionInputTransformValue,
            _annotations.FeedForwardHiddenTransform,
            _annotations.FeedForwardOutputTransform,
        ]
        batched_annotation_types = [
            _annotations.BatchedAttentionOutputTransform,
            _annotations.BatchedAttentionInputTransformQuery,
            _annotations.BatchedAttentionInputTransformKey,
            _annotations.BatchedAttentionInputTransformValue,
            _annotations.BatchedFeedForwardHiddenTransform,
            _annotations.BatchedFeedForwardOutputTransform,
        ]
        moe_annoation_types = [
            _annotations.MoEFeedForwardHiddenTransform,
            _annotations.MoEFeedForwardOutputTransform,
        ]
        for lt in layer_type:
            if any(
                (
                    mask and isinstance(lt, annotation_type)
                    for mask, annotation_type in zip(masks, annotation_types)
                )
            ):
                return lt, False
            if any(
                (
                    mask and isinstance(lt, annotation_type)
                    for mask, annotation_type in zip(masks, batched_annotation_types)
                )
            ):
                return lt, True
            if any(
                self.adapt_moe and isinstance(lt, annotation_type)
                for annotation_type in moe_annoation_types
            ):
                # MoE is implemented using BatchedLinear
                return lt, True
        return None, False

    def _get_lora_fused_multi_output_linear_type(
        self, layer_type: _List[_LayerAnnotation]
    ) -> _Tuple[_Optional[_LayerAnnotation], bool]:
        adapt_attention_input_transform = (
            self.adapt_attention_queries
            or self.adapt_attention_keys
            or self.adapt_attention_values
        )
        for lt in layer_type:
            if adapt_attention_input_transform and isinstance(
                lt, _annotations.AttentionInputTransformFused
            ):
                return lt, False
            if adapt_attention_input_transform and isinstance(
                lt, _annotations.BatchedAttentionInputTransformFused
            ):
                return lt, True
        return None, False

    def _create_adapters_impl(self, model: _nn.Module) -> _AdapterSpec:
        layer_adapters = {}
        for name, submodule in model.named_modules(remove_duplicate=True):
            if isinstance(submodule, _AdaptedLayer):
                if self.layer_pattern is not None:
                    layer_idx = (
                        int(name.split(self.layer_prefix)[-1].split(".")[0])
                        if self.layer_prefix in name
                        else None
                    )
                    if layer_idx is None:
                        _warnings.warn(
                            f"layer selector is specified but module's name: {name} "
                            f"does not match layer_prefix pattern: {self.layer_prefix}."
                            " Tamm will apply this adapter to all matched modules."
                        )
                    elif not self._adapt_current_layer(layer_idx):
                        continue

                adapter = self._create_adapter_for_submodule(submodule)
                if adapter is not None:
                    layer_adapters[name] = adapter
        return _AdapterSpec(layer_adapters=layer_adapters)

    def _adapt_current_layer(self, layer_idx: int):
        """
        Helper function to determine if we should
        adapt current module based on its layer_idx.
        """
        if isinstance(self.layer_pattern, str):
            if self.layer_pattern.lower() == "even":
                return layer_idx % 2 == 0
            if self.layer_pattern.lower() == "odd":
                return layer_idx % 2 != 0
            if ":" in self.layer_pattern:
                slice_values = self.layer_pattern.split(":")
                if len(slice_values) > 3:
                    raise RuntimeError(
                        "Found more than two `:` in layer_pattern. "
                        "Python slice only supports up to two `:`"
                    )
                start, end = int(slice_values[0]), int(slice_values[1])
                if len(slice_values) == 3:
                    return (
                        layer_idx
                        in list(range(end + 1))[slice(start, end, int(slice_values[2]))]
                    )
                if len(slice_values) == 2:
                    return layer_idx in list(range(end + 1))[slice(start, end)]

        if isinstance(self.layer_pattern, list):
            return layer_idx in self.layer_pattern

        raise ValueError(f"Unrecognized layer pattern {self.layer_pattern}")

    def _create_adapter_for_submodule(
        self, submodule: _nn.Module
    ) -> _Optional[_LayerAdapter]:
        wrapped_module = submodule.unwrap()
        layer_type = _get_layer_annotations(wrapped_module)
        linear_layer_type, is_batched = self._get_lora_linear_layer_type(layer_type)
        if linear_layer_type:
            input_dim = getattr(wrapped_module, linear_layer_type.input_dim_field)
            output_dim = getattr(wrapped_module, linear_layer_type.output_dim_field)
            if is_batched:
                vec_dim = getattr(wrapped_module, linear_layer_type.vec_dim_field)
                return _BatchedLoRA(
                    input_dim=input_dim,
                    output_dim=output_dim,
                    rank=self.rank,
                    vec_dim=vec_dim,
                    alpha=self.alpha,
                    dropout_p=self.dropout_p,
                    dtype=self.dtype,
                )
            return _LoRA(
                input_dim=input_dim,
                output_dim=output_dim,
                rank=self.rank,
                alpha=self.alpha,
                dropout_p=self.dropout_p,
                dtype=self.dtype,
            )
        (
            fused_linear_layer_type,
            is_batched,
        ) = self._get_lora_fused_multi_output_linear_type(layer_type)
        if fused_linear_layer_type:
            input_dim = getattr(wrapped_module, fused_linear_layer_type.input_dim_field)
            output_dims = getattr(
                wrapped_module, fused_linear_layer_type.output_dims_field
            )
            mask = (
                self.adapt_attention_queries,
                self.adapt_attention_keys,
                self.adapt_attention_values,
            )
            if is_batched:
                vec_dim = getattr(wrapped_module, fused_linear_layer_type.vec_dim_field)
                return _BatchedLoRAFusedMultiOutputLinear(
                    input_dim=input_dim,
                    output_dims=output_dims,
                    ranks=[self.rank] * 3,
                    vec_dim=vec_dim,
                    alphas=[self.alpha] * 3,
                    dropout_ps=[self.dropout_p] * 3,
                    mask=mask,
                    dtype=self.dtype,
                )
            return _LoRAFusedMultiOutputLinear(
                input_dim=input_dim,
                output_dims=output_dims,
                ranks=[self.rank] * 3,
                alphas=[self.alpha] * 3,
                dropout_ps=[self.dropout_p] * 3,
                mask=mask,
                dtype=self.dtype,
            )
        return None


class MultiLoRAModelAdapter(_CompositeModelAdapterMixin, _ModelAdapter):
    """
    Applies :py:class:`StackedOutputTransforms` composition to all modules which have
    LoRA adapters with ids specified in ``adapters``.
    The :py:class:`StackedOutputTransforms` adds up the results of
    multiple LoRA adapters in parallel to the adapted layer,
    such that the output of the adapted layer is:

    output = adapted_layer(input) + lora_0(inputs) +
        lora_1(inputs) + lora_2(inputs) + ...
    """

    adapters: _Dict[str, _ModelAdapter]

    def _create_composite_adapter(self, child_adapters: _Dict[str, _LayerAdapter]):
        return _StackedOutputTransforms(_OrderedDict(child_adapters))


class SoftMixingLoRAModelAdapter(_CompositeModelAdapterMixin, _ModelAdapter):
    """
    Applies :py:class:`SoftMixingLoRA` composition to all modules which have
    adapters with ids specified in ``adapters``. The :py:class:`SoftMixingLoRA`
    applies a mixture of multiple LoRA adapters in parallel to the
    adapted layer, such that the output of the adapted layer is:

    output = adapted_layer(input) + lora_0(weight[:, 0] * inputs) +
        lora_1(weight[:, 1] * inputs) + lora_2(weight[:, 2] * inputs) + ...

    where weight is a m x n tensor where m is equal to the batch size of inputs
    and n is equal to the number of LoRA adapters being applied together.
    """

    adapters: _Dict[str, _ModelAdapter]

    def _create_composite_adapter(self, child_adapters: _Dict[str, _LayerAdapter]):
        return _SoftMixingLoRA(_OrderedDict(child_adapters))
