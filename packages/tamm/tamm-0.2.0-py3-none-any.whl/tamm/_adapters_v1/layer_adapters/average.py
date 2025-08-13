from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional

from tamm._adapters_v1.layer_adapters.common import AdapterMode as _AdapterMode
from tamm._adapters_v1.layer_adapters.common import (
    CompositeInputTransform as _CompositeInputTransform,
)
from tamm._adapters_v1.layer_adapters.common import (
    CompositeOutputTransform as _CompositeOutputTransform,
)
from tamm._adapters_v1.layer_adapters.common import LayerAdapter as _LayerAdapter
from tamm.utils._torch_compatibility import _pytree_average


class AveragedInputTransforms(_CompositeInputTransform):
    """
    A composite :class:`LayerAdapter` that averages together input transformations from
    multiple child adapters.  The behavior is equivalent to the following:

    .. code-block:: python

        transformed_inputs = [
            adapter(TRANSFORM_INPUTS, args=args, kwargs=kwargs)
            for adapter in adapters.values()
        ]
        args, kwargs = average(transformed_inputs, weights=weights)
        outputs = wrapped(args, kwargs)

    The transformed inputs returned by each adapter may be a container object as long
    as the structure of the object is identical across adapters.  In this case, the
    average applies to all floating point tensors in the container and the result's
    other values come from the transformed inputs of the first adapter.

    Args:
        adapters (:obj:`dict` that maps :obj:`str` to :obj:`LayerAdapter`): A dictionary
            that maps child adapter IDs to corresponding adapters.
        weights (:obj:`dict` that maps :obj:`str` to :obj:`float`, optional): A
            dictionary that maps child adapter IDs to corresponding weights for
            averaging transformed inputs.  Defaults to ``None``, which results in no
            weighting.
    """

    def __init__(
        self,
        adapters: _Dict[str, _LayerAdapter],
        weights: _Optional[_Dict[str, float]] = None,
    ):
        super().__init__(adapters=adapters)
        self.weights = weights

    def _transform_inputs(self, *, args: _Any, kwargs: _Any) -> _Any:
        transformed_inputs = [
            adapter(mode=_AdapterMode.TRANSFORM_INPUTS, args=args, kwargs=kwargs)
            for adapter in self._child_adapters.values()
        ]
        if self.weights is not None:
            weights = [self.weights[key] for key in self._child_adapters]
        else:
            weights = None
        return _pytree_average(*transformed_inputs, weights=weights)


class AveragedOutputTransforms(_CompositeOutputTransform):
    """
    A composite :class:`LayerAdapter` that averages together output transformations from
    multiple child adapters.  The behavior is equivalent to the following:

    .. code-block:: python

        outputs = wrapped(args, kwargs)
        transformed_outputs = [
            adapter(
                TRANSFORM_OUTPUTS,
                args=args,
                kwargs=kwargs,
                transformed_args=args,
                transformed_kwargs=kwargs,
                outputs=outputs,
            )
            for adapter in adapters.values()
        ]
        outputs = average(transformed_outputs, weights=weights)

    The transformed outputs returned by each adapter may be a container object as long
    as the structure of the object is identical across adapters.  In this case, the
    average applies to all floating point tensors in the container and the result's
    other values come from the transformed outputs of the first adapter.

    Args:
        adapters (:obj:`dict` that maps :obj:`str` to :obj:`LayerAdapter`): A dictionary
            that maps child adapter IDs to corresponding adapters.
        weights (:obj:`dict` that maps :obj:`str` to :obj:`float`, optional): A
            dictionary that maps child adapter IDs to corresponding weights for
            averaging transformed outputs.  Defaults to ``None``, which results in no
            weighting.
    """

    def __init__(
        self,
        adapters: _Dict[str, _LayerAdapter],
        weights: _Optional[_Dict[str, float]] = None,
    ):
        super().__init__(adapters=adapters)
        self.weights = weights

    def _transform_outputs(  # pylint: disable=unused-argument
        self,
        *,
        args: _Any,
        kwargs: _Any,
        transformed_args: _Any,
        transformed_kwargs: _Any,
        outputs: _Any,
    ) -> _Any:
        outputs = [
            adapter(
                mode=_AdapterMode.TRANSFORM_OUTPUTS,
                outputs=outputs,
                args=args,
                kwargs=kwargs,
                transformed_args=transformed_args,
                transformed_kwargs=transformed_kwargs,
            )
            for adapter in self._child_adapters.values()
        ]
        if self.weights is not None:
            weights = [self.weights[key] for key in self._child_adapters]
        else:
            weights = None
        return _pytree_average(*outputs, weights=weights)
