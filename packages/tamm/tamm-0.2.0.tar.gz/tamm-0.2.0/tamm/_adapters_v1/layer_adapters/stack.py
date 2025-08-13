from typing import Any as _Any

import torch.nn as _nn

from tamm._adapters_v1.layer_adapters.common import AdapterMode as _AdapterMode
from tamm._adapters_v1.layer_adapters.common import (
    CompositeInputTransform as _CompositeInputTransform,
)
from tamm._adapters_v1.layer_adapters.common import (
    CompositeOutputTransform as _CompositeOutputTransform,
)
from tamm._adapters_v1.layer_adapters.common import (
    MergeableLayerAdapterMixin as _MergeableLayerAdapterMixin,
)


class StackedInputTransforms(_CompositeInputTransform, _MergeableLayerAdapterMixin):
    """
    A composite :class:`LayerAdapter` that stacks together input transformations from
    multiple child adapters.  The behavior is equivalent to the following:

    .. code-block:: python

        for adapter in adapters.values():
            args, kwargs = adapter(TRANSFORM_INPUTS, args=args, kwargs=kwargs)
        outputs = wrapped(args, kwargs)

    Args:
        adapters (:obj:`dict` that maps :obj:`str` to :obj:`LayerAdapter`): A dictionary
            that maps child adapter IDs to corresponding adapters.  Note that the
            ordering of the values in ``adapters`` determines the ordering of the stack.
    """

    def _transform_inputs(self, *, args, kwargs):
        for adapter in self._child_adapters.values():
            args, kwargs = adapter(
                mode=_AdapterMode.TRANSFORM_INPUTS, args=args, kwargs=kwargs
            )
        return args, kwargs

    def merge_adapter(self, wrapped_module: _nn.Module):
        if not all(
            getattr(adapter, "merge_adapter")
            for adapter in self._child_adapters.values()
        ):
            raise RuntimeError("All child adapters should be mergeable adapters.")

        for adapter in self._child_adapters.values():
            adapter.merge_adapter(wrapped_module)


class StackedOutputTransforms(_CompositeOutputTransform, _MergeableLayerAdapterMixin):
    """
    A composite :class:`LayerAdapter` that stacks together output transformations from
    multiple child adapters.  The behavior is equivalent to the following:

    .. code-block:: python

        outputs = wrapped(args, kwargs)
        for adapter in adapters.values():
            outputs = adapter(
                TRANSFORM_OUTPUTS,
                args=args,
                kwargs=kwargs,
                transformed_args=args,
                transformed_kwargs=kwargs,
                outputs=outputs,
            )

    Args:
        adapters (:obj:`dict` that maps :obj:`str` to :obj:`LayerAdapter`): A dictionary
            that maps child adapter IDs to corresponding adapters.  Note that the
            ordering of the values in ``adapters`` determines the ordering of the stack.
    """

    def _transform_outputs(
        self,
        *,
        args: _Any,
        kwargs: _Any,
        transformed_args: _Any,
        transformed_kwargs: _Any,
        outputs: _Any,
    ):
        for adapter in self._child_adapters.values():
            outputs = adapter(
                mode=_AdapterMode.TRANSFORM_OUTPUTS,
                outputs=outputs,
                args=args,
                kwargs=kwargs,
                transformed_args=transformed_args,
                transformed_kwargs=transformed_kwargs,
            )
        return outputs

    def merge_adapter(self, wrapped_module: _nn.Module):
        if not all(
            getattr(adapter, "merge_adapter")
            for adapter in self._child_adapters.values()
        ):
            raise RuntimeError("All child adapters should be mergeable adapters.")
        for adapter in self._child_adapters.values():
            adapter.merge_adapter(wrapped_module)
