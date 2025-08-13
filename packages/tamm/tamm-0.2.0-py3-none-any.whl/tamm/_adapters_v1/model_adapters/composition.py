# pylint: disable=no-member, cyclic-import, line-too-long

"""
_adapters_v1.model_adapters.composition
=======================================

.. autoclass:: tamm._adapters_v1.model_adapters.composition.StackedOutputTransformsModelAdapter
    :show-inheritance:
    :members:

.. autoclass:: tamm._adapters_v1.model_adapters.composition.StackedInputTransformsModelAdapter
    :show-inheritance:
    :members:

.. autoclass:: tamm._adapters_v1.model_adapters.composition.AverageOutputTransformsModelAdapter
    :show-inheritance:
    :members:

.. autoclass:: tamm._adapters_v1.model_adapters.composition.AverageInputTransformsModelAdapter
    :show-inheritance:
    :members:
"""

import logging as _logging
from typing import Dict as _Dict
from typing import Optional as _Optional

import torch.nn as _nn

from tamm._adapters_v1.adapted_layer import AdaptedLayer as _AdaptedLayer
from tamm._adapters_v1.layer_adapters import (
    AveragedInputTransforms as _AveragedInputTransforms,
)
from tamm._adapters_v1.layer_adapters import (
    AveragedOutputTransforms as _AveragedOutputTransforms,
)
from tamm._adapters_v1.layer_adapters import LayerAdapter as _LayerAdapter
from tamm._adapters_v1.layer_adapters import (
    StackedInputTransforms as _StackedInputTransforms,
)
from tamm._adapters_v1.layer_adapters import (
    StackedOutputTransforms as _StackedOutputTransforms,
)
from tamm._adapters_v1.model_adapters.model_adapter import AdapterSpec as _AdapterSpec
from tamm._adapters_v1.model_adapters.model_adapter import ModelAdapter as _ModelAdapter

_logger = _logging.getLogger(__name__)


class CompositeModelAdapterMixin:
    """
    A mixin which implements composition of multiple model adapters. Any class
    that inherits from this mixin should implement the :func:`_create_composite_adapter`
    method which consumes child :class:`LayerAdapter`s and composes them to create
    a composite adapter.
    """

    def __post_init__(self):
        # if an adapter's pretrained flag is not set, inherit it from parent
        for adapter in self.adapters.values():
            if adapter.pretrained_path is not None and adapter.pretrained is None:
                adapter.pretrained = self.pretrained

    def _create_adapters_impl(self, model: _nn.Module) -> _AdapterSpec:
        child_adapter_specs = {
            ad_id: adapter.create_adapters(model).layer_adapters
            for ad_id, adapter in self.adapters.items()
        }

        layer_adapters = {}
        for name, submodule in model.named_modules(remove_duplicate=True):
            if isinstance(submodule, _AdaptedLayer):
                child_adapters = {
                    ad_id: child_adapter_specs[ad_id][name]
                    for ad_id in self.adapters
                    if name in child_adapter_specs[ad_id]
                }
                if len(child_adapters) == 0:
                    continue
                if len(child_adapters) == 1:
                    _logger.debug(
                        f"Exactly one adapter for module {name}, so passing it through."
                    )
                    layer_adapters[name] = list(child_adapters.values())[0]
                elif len(child_adapters) < len(self.adapters):
                    no_child_adapters = set(self.adapters.keys()) - set(
                        child_adapters.keys()
                    )
                    raise ValueError(
                        f"Adapters cannot be composed for module: {name}, "
                        "because adapters with these ids do not create "
                        f"any layer adapters: {no_child_adapters}."
                    )
                else:
                    layer_adapters[name] = self._create_composite_adapter(
                        child_adapters
                    )
        return _AdapterSpec(layer_adapters=layer_adapters)


class StackedOutputTransformsModelAdapter(CompositeModelAdapterMixin, _ModelAdapter):
    """
    A composite :class:`ModelAdapter` that stacks together output transformations from
    multiple child adapters. This model adapter initializes
    :class:`StackedOutputTransforms` :class:`LayerAdapter`s for all the layers
    where layer adapters are inserted by child model adapters.

    Args:
        adapters (:obj:`dict` that maps :obj:`str` to :obj:`ModelAdapter`): A dictionary
            that maps child adapter IDs to corresponding adapters.  Note that the
            ordering of the values in ``adapters`` determines the ordering of the stack.
    """

    adapters: _Dict[str, _ModelAdapter]

    def _create_composite_adapter(self, child_adapters: _Dict[str, _LayerAdapter]):
        return _StackedOutputTransforms(child_adapters)


class StackedInputTransformsModelAdapter(CompositeModelAdapterMixin, _ModelAdapter):
    """
    A composite :class:`ModelAdapter` that stacks together input transformations from
    multiple child adapters. This model adapter initializes
    :class:`StackedInputTransforms` :class:`LayerAdapter`s for all the layers
    where layer adapters are inserted by child model adapters.

    Args:
        adapters (:obj:`dict` that maps :obj:`str` to :obj:`ModelAdapter`): A dictionary
            that maps child adapter IDs to corresponding adapters.  Note that the
            ordering of the values in ``adapters`` determines the ordering of the stack.
    """

    adapters: _Dict[str, _ModelAdapter]

    def _create_composite_adapter(self, child_adapters: _Dict[str, _LayerAdapter]):
        return _StackedInputTransforms(child_adapters)


class AveragedOutputTransformsModelAdapter(CompositeModelAdapterMixin, _ModelAdapter):
    """
    A composite :class:`ModelAdapter` that averages together output transformations from
    multiple child adapters. This model adapter initializes
    :class:`AveragedOutputTransforms` :class:`LayerAdapter`s for all the layers
    where layer adapters are inserted by child model adapters.

    Args:
        adapters (:obj:`dict` that maps :obj:`str` to :obj:`ModelAdapter`): A dictionary
            that maps child adapter IDs to corresponding model adapters.
        weights (:obj:`dict` that maps :obj:`str` to :obj:`float`, optional): A
            dictionary that maps child adapter IDs to corresponding weights for
            averaging transformed inputs.  Defaults to ``None``, which results in no
            weighting.
    """

    adapters: _Dict[str, _ModelAdapter]
    weights: _Optional[_Dict[str, float]] = None

    def _create_composite_adapter(self, child_adapters: _Dict[str, _LayerAdapter]):
        return _AveragedOutputTransforms(child_adapters, weights=self.weights)


class AveragedInputTransformsModelAdapter(CompositeModelAdapterMixin, _ModelAdapter):
    """
    A composite :class:`ModelAdapter` that averages together input transformations from
    multiple child adapters. This model adapter initializes
    :class:`AveragedInputTransforms` :class:`LayerAdapter`s for all the layers
    where layer adapters are inserted by child model adapters.

    Args:
        adapters (:obj:`dict` that maps :obj:`str` to :obj:`ModelAdapter`): A dictionary
            that maps child adapter IDs to corresponding model adapters.
        weights (:obj:`dict` that maps :obj:`str` to :obj:`float`, optional): A
            dictionary that maps child adapter IDs to corresponding weights for
            averaging transformed inputs.  Defaults to ``None``, which results in no
            weighting.
    """

    adapters: _Dict[str, _ModelAdapter]
    weights: _Optional[_Dict[str, float]] = None

    def _create_composite_adapter(self, child_adapters: _Dict[str, _LayerAdapter]):
        return _AveragedInputTransforms(child_adapters, weights=self.weights)
