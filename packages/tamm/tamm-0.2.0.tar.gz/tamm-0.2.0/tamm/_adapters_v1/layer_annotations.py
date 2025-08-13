"""
adapters.layer_annotations
==========================

.. autoclass:: tamm.adapters.layer_annotations.FusedLinearProjection
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.AttentionInputTransformFused
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.LinearProjection
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.AttentionInputTransformQuery
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.AttentionInputTransformKey
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.AttentionInputTransformValue
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.AttentionOutputTransform
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.FeedForwardHiddenTransform
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.FeedForwardOutputTransform
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.BatchedFusedLinearProjection
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.BatchedAttentionInputTransformFused
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.BatchedLinearProjection
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.BatchedAttentionInputTransformQuery
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.BatchedAttentionInputTransformKey
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.BatchedAttentionInputTransformValue
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.BatchedAttentionOutputTransform
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.BatchedFeedForwardHiddenTransform
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_annotations.BatchedFeedForwardOutputTransform
    :show-inheritance:
    :members:
"""

import dataclasses as _dataclasses
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Type as _Type
from typing import Union as _Union

import torch.nn as _nn

from tamm.utils import registry as _registry

_LAYER_ANNOTATION_FIELD = "_layer_annotation_type"

_LAYER_ANNOTATION_TYPE_REGISTRY = _registry.Registry("Layer annotation types")


class LayerAnnotation:
    """
    An annotation data class which defines a contract between
    an adapter :py:class:`BaseAdapter` and a module which can be
    adapted using that adapter. This contract typically consists of
    names of fields and parameters of the module which are recognized
    by the adapter.

    This contract also enables a :py:class:`ModelAdapter`
    to correctly recognize different submodules of same type in the model
    and adapt them according to their annotations.

    Any new layer type can be added by subclassing :py:class:`LayerAnnotation`,
    which also automatically enables it to be specified using a
    string corresponding to its class name.
    """

    def __init_subclass__(cls):
        _dataclasses.dataclass(cls)
        _LAYER_ANNOTATION_TYPE_REGISTRY.register(cls, cls.__name__)


LayerAnnotationType = _Union[
    _Tuple[_Union[_Type[LayerAnnotation], str], _Optional[_Dict[str, str]]],
    _Tuple[_Union[_Type[LayerAnnotation], str]],
]


class FusedLinearProjection(LayerAnnotation):
    """
    Annotates a fused linear projection layer, which applies
    the following transformation to inputs `X`:

    ``output = split(W @ X + b, output_dims, dim=-1)``
    """

    input_dim_field: str
    output_dims_field: str
    weight_param_name: str


class BatchedFusedLinearProjection(LayerAnnotation):
    """
    Annotates a Batched fused linear projection layer, which applies
    the following transformation to inputs `X`:

    ``output = split(W @ X + b, output_dims, dim=-1)``
    """

    input_dim_field: str
    output_dims_field: str
    weight_param_name: str
    vec_dim_field: str


class AttentionInputTransformFused(FusedLinearProjection):
    """
    Annotates a layer which computes the query, key and value
    activations for an attention operation by projecting out
    the input activations.
    """


class BatchedAttentionInputTransformFused(BatchedFusedLinearProjection):
    """
    Annotates a layer which computes the query, key and value
    activations for an attention operation by projecting out
    the input activations using batched linear projections.
    """


class LinearProjection(LayerAnnotation):
    """
    Annotates a linear projection layer, which applies
    the following transformation to inputs `X`:

    ``output = W @ X + b``
    """

    input_dim_field: str = "in_features"
    output_dim_field: str = "out_features"
    weight_param_name: str = "weight"


class BatchedLinearProjection(LayerAnnotation):
    """
    Annotates a batched linear projection layer, which applies
    the following transformation to inputs `X`:

    ``output = W @ X + b``
    """

    input_dim_field: str = "in_features"
    output_dim_field: str = "out_features"
    vec_dim_field: str = "vec_dim"
    weight_param_name: str = "weight"


class AttentionInputTransformQuery(LinearProjection):
    """
    Annotates a layer which computes the query activation
    for attention operation.
    """


class AttentionInputTransformKey(LinearProjection):
    """
    Annotates a layer which computes the key activation
    for attention operation.
    """


class AttentionInputTransformValue(LinearProjection):
    """
    Annotates a layer which computes the value activation
    for attention operation.
    """


class AttentionOutputTransform(LinearProjection):
    """
    Annotates a layer which computes the output activation
    by projecting out the output of an attention operation
    in a transformer layer.
    """


class FeedForwardHiddenTransform(LinearProjection):
    """
    Annotates the feed-forward hidden transform projection
    layer of a transformer block.
    """


class FeedForwardOutputTransform(LinearProjection):
    """
    Annotates the feed-forward output transform projection
    layer of a transformer block.
    """


class BatchedAttentionInputTransformQuery(BatchedLinearProjection):
    """
    Annotates a layer which computes the query activation
    for attention operation using batched linear projection.
    """


class BatchedAttentionInputTransformKey(BatchedLinearProjection):
    """
    Annotates a layer which computes the key activation
    for attention operation using batched linear projection.
    """


class BatchedAttentionInputTransformValue(BatchedLinearProjection):
    """
    Annotates a layer which computes the value activation
    for attention operation using batched linear projection.
    """


class BatchedAttentionOutputTransform(BatchedLinearProjection):
    """
    Annotates a layer which computes the output activation
    by projecting out the output of an attention operation
    in a transformer layer using batched linear projection.
    """


class BatchedFeedForwardHiddenTransform(BatchedLinearProjection):
    """
    Annotates the feed-forward hidden transform Batched linear projection
    layer of a transformer block.
    """


class BatchedFeedForwardOutputTransform(BatchedLinearProjection):
    """
    Annotates the feed-forward output transform Batched linear projection
    layer of a transformer block.
    """


class MoEFeedForwardHiddenTransform(BatchedLinearProjection):
    """
    Annotates the feed-forward hidden transform projection
    layer of a mixture-of-experts transformer block.
    """


class MoEFeedForwardOutputTransform(BatchedLinearProjection):
    """
    Annotates the feed-forward output transform projection
    layer of a mixture-of-experts transformer block.
    """


def annotate_layer(module: _nn.Module, layer_annotations: _List[LayerAnnotationType]):
    """
    Mark a module with a list of :py:class:`LayerAnnotation` to indicate it is
    an adaptable layer of those types.
    """
    layer_types = getattr(module, _LAYER_ANNOTATION_FIELD, [])
    existing_layer_types = set(
        layer_type.__class__.__name__ for layer_type in layer_types
    )
    for layer_annotation in layer_annotations:
        if not 1 <= len(layer_annotation) <= 2:
            raise ValueError(
                f"Found invalid layer_annotation: {layer_annotation}. "
                f"It should be a tuple of 1 <= length <= 2."
            )

        if len(layer_annotation) == 2:
            layer_type_cls_name_or_cls, kwargs = layer_annotation
        else:
            # len(layer_annotation) == 1
            layer_type_cls_name_or_cls, kwargs = layer_annotation[0], None
        # we always use a string for getting the correct layer_type_cls
        # so that if a class is not in registry, we can catch it
        layer_type_cls_name = (
            layer_type_cls_name_or_cls.__name__
            if not isinstance(layer_type_cls_name_or_cls, str)
            else layer_type_cls_name_or_cls
        )
        if layer_type_cls_name in existing_layer_types:
            continue
        layer_type_cls: LayerAnnotation = (
            _LAYER_ANNOTATION_TYPE_REGISTRY.get_factory_fn(layer_type_cls_name)
        )
        layer_type = (
            layer_type_cls(**kwargs)  # pylint: disable=not-callable
            if kwargs
            else layer_type_cls()  # pylint: disable=not-callable
        )
        layer_types.append(layer_type)
    setattr(module, _LAYER_ANNOTATION_FIELD, layer_types)


def unannotate_layer(module: _nn.Module):
    """
    Removes layer annotations from a module.
    """
    if is_adaptable_layer(module):
        delattr(module, _LAYER_ANNOTATION_FIELD)


def is_adaptable_layer(module: _nn.Module) -> bool:
    """
    Returns ``True`` if a module supports getting adapted with an adapter,
    i.e., it has been annotated with a list of :py:class:`LayerAnnotation`.
    """
    return hasattr(module, _LAYER_ANNOTATION_FIELD)


def get_layer_annotations(
    module: _nn.Module,
    filter_types: _Optional[_Tuple[_Type[LayerAnnotation]]] = None,
) -> _Optional[_List[LayerAnnotation]]:
    """
    Returns the list of :py:class:`LayerAnnotation` annotation of a
    module, if it exists. If ``filter_types`` is specified, only returns
    layer types which are of specified
    """
    if is_adaptable_layer(module):
        layer_types = getattr(module, _LAYER_ANNOTATION_FIELD)
        if filter_types:
            return [lt for lt in layer_types if isinstance(lt, filter_types)]
        return layer_types
    return None
