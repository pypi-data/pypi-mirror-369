"""
.. _adapted_layer:

adapters.adapted_layer
======================

.. autoclass:: tamm.adapters.AdaptedLayer
    :show-inheritance:
    :members:
"""

import logging as _logging
from typing import Optional as _Optional
from typing import Tuple as _Tuple

import torch.nn as _nn

from tamm._adapters_v1.layer_adapters.common import AdapterMode as _AdapterMode
from tamm._adapters_v1.layer_adapters.common import LayerAdapter as _LayerAdapter
from tamm._adapters_v1.layer_adapters.common import (
    MergeableLayerAdapterMixin as _MergeableLayerAdapterMixin,
)

_logger = _logging.getLogger(__name__)


class AdaptedLayer(_nn.Module):
    """
    A wrapper layer for enabling adapters for a module. Provides functionality
    for managing adapters and modifies either the inputs or the outputs (or both) of
    the wrapped model using the currently active adapter.
    """

    def __init__(self, layer: _nn.Module):
        super().__init__()
        self.wrapped = layer
        self.adapters = _nn.ModuleDict()
        self._active_adapter_id = None

    @staticmethod
    def _get_parent_child_adapter_id(adapter_id: str) -> _Optional[_Tuple[str, str]]:
        children = adapter_id.split(".")
        if len(children) > 1:
            return children[0], ".".join(children[1:])
        return None

    def unwrap(self) -> _nn.Module:
        """
        Returns the layer wrapped in this :py:class:`AdaptedLayer`
        """
        return self.wrapped

    def add_adapter(
        self,
        adapter_id: str,
        adapter: _LayerAdapter,
    ):
        """
        Add an adapter to the layer.

        Args:
            adapter_id (:obj:`str`): A unique identifier for the adapter being added.
            adapter: (:py:class:`_LayerAdapter` ): Adapter to be added to
              this layer.
        """
        self.adapters[adapter_id] = adapter

    def _get_adapter_impl(self, adapter_id: str) -> _Optional[_LayerAdapter]:
        parent_child_id = self._get_parent_child_adapter_id(adapter_id)
        if parent_child_id:
            parent_id, child_id = parent_child_id
            if parent_id not in self.adapters:
                return None
            try:
                return self.adapters[parent_id].get_submodule(child_id)
            except AttributeError:
                return None
        if adapter_id in self.adapters:
            return self.adapters[adapter_id]
        return None

    def _is_nested_adapter_id(self, adapter_id: str) -> bool:
        """
        Returns True if the adapter id is a nested id, such as
        adapter_a.child_1.child2
        """
        return self._get_parent_child_adapter_id(adapter_id) is not None

    def has_adapter(self, adapter_id: str) -> bool:
        """
        Returns True if an adapter identified by the ``adapter_id`` exists.
        Args:
            adapter_id (:obj:`str`): The unique identifier for the desired adapter.
        """

        return self._get_adapter_impl(adapter_id) is not None

    def get_adapter(self, adapter_id: str) -> _LayerAdapter:
        """
        Returns the adapter identified by the ``adapter_id``, if it exists.
        Args:
            adapter_id (:obj:`str`): The unique identifier for the desired adapter.
        """
        adapter = self._get_adapter_impl(adapter_id)
        if not adapter:
            raise AttributeError(
                f"Adapter with id: {adapter_id} does not exist in the adapted layer."
            )
        return adapter

    def delete_adapter(self, adapter_id: str):
        """
        Deletes an adapter identified by ``adapter_id``, if it exists.

        Args:
            adapter_id (:obj:`str`): The unique identifier for the adapter being
              deleted.
        """
        if self._is_nested_adapter_id(adapter_id):
            raise AttributeError(
                f"Received nested adapter id: {adapter_id}. delete_adapter only"
                f"supports un-nested adapter_ids with no '.' in the id."
            )
        self.get_adapter(adapter_id)
        self.adapters.pop(adapter_id)
        if self._active_adapter_id == adapter_id:
            self._active_adapter_id = None

    def freeze_adapter(self, adapter_id: str):
        """
        Freeze the parameters of the adapter identified by ``adapter_id``.

        Args:
            adapter_id (:obj:`str`): The unique identifier for the adapter being frozen.
        """
        self.get_adapter(adapter_id).freeze()

    def unfreeze_adapter(self, adapter_id: str):
        """
        Make the parameters of the adapter identified by ``adapter_id`` trainable.

        Args:
            adapter_id (:obj:`str`): The unique identifier for the adapter
              being made trainable.
        """
        self.get_adapter(adapter_id).unfreeze()

    @property
    def active_adapter(self):
        """
        Returns the currently active adapter.
        """
        if self._active_adapter_id is None:
            return None
        return self.get_adapter(self._active_adapter_id)

    @property
    def active_adapter_id(self):
        """
        Returns the id of the currently active adapter.
        """
        return self._active_adapter_id

    def set_active_adapter(self, adapter_id: str, replace: bool = True):
        """
        Set one of the adapters already added to the layer as the active adapter.
        All other adapters besides this are inactive and won't be used during
        model's forward pass.

        Args:
            adapter_id (:obj:`str`): The unique identifier for the adapter
              to be activated.
            replace (:obj:`bool`): When set to ``True``, the current active adapter is replaced
              by the adapter with ``adapter_id``. Throws an exception when ``False`` if an
              active adapter already exists.
        """
        # call get adapter to make sure the adapter exists
        self.get_adapter(adapter_id)
        if self._is_nested_adapter_id(adapter_id):
            raise AttributeError(
                f"Received nested adapter id: {adapter_id}. set_active_adapter only"
                f"supports un-nested adapter_ids with no '.' in the id."
            )
        if replace:
            self.unset_active_adapter()
        elif (
            not replace
            and self._active_adapter_id is not None
            and adapter_id != self._active_adapter_id
        ):
            raise ValueError(
                f"Found an existing active adapter {self._active_adapter_id}. For replacing "
                f"the existing active adapter, call set_active_adapter with replace=True. "
                "Only one adapter can be activated at a time. For combining multiple adapters, "
                "consider using composite adapters, such as CompositeInputTransform or CompositeInputTransform."
            )
        self._active_adapter_id = adapter_id

    def unset_active_adapter(self):
        """
        Unset the active adapter from the layer, if any.
        """
        if self._active_adapter_id is not None:
            _logger.debug(f"De-activating adapter with id: {self._active_adapter_id}.")
            self._active_adapter_id = None

    def _merge_adapter(self, adapter_id: str):
        """
        Merge weights of adapter with adapter_id into the wrapped module,
        if the adapter supports merging.

         Args:
            adapter_id (:obj:`str`): The unique identifier for the adapter
              to be merged.
        """
        if self._is_nested_adapter_id(adapter_id):
            raise AttributeError(
                f"Received nested adapter id: {adapter_id}. merge_adapter only"
                f"supports un-nested adapter_ids with no '.' in the id."
            )
        adapter = self.get_adapter(adapter_id)
        if not isinstance(adapter, _MergeableLayerAdapterMixin):
            raise ValueError(  # pylint: disable=raise-missing-from
                f"Adapter with id: {adapter_id} of type: {type(adapter)}"
                f" doesn't support merge operation."
            )
        adapter.merge_adapter(self.wrapped)
        self.delete_adapter(adapter_id)

    def forward(self, *args, **kwargs):
        """
        Modifies either the inputs or the outputs (or both) of the wrapped
        model with the currently active adapter.
        """
        if self.active_adapter is None:
            return self.wrapped(*args, **kwargs)

        # pylint: disable=not-callable
        if self.active_adapter.has_input_transform:
            transformed_args, transformed_kwargs = self.active_adapter(
                mode=_AdapterMode.TRANSFORM_INPUTS,
                args=args,
                kwargs=kwargs,
                transformed_args=None,
                transformed_kwargs=None,
                outputs=None,
            )
        else:
            # The base input transform is a noop, but we avoid calling it
            # because if active_adapter is wrapped with FSDP v1, it triggers
            # an extra parameter unshard (which can slow performance)
            transformed_args, transformed_kwargs = args, kwargs

        model_out = self.wrapped(*transformed_args, **transformed_kwargs)

        if self.active_adapter.has_output_transform:
            return self.active_adapter(
                mode=_AdapterMode.TRANSFORM_OUTPUTS,
                args=args,
                kwargs=kwargs,
                transformed_args=transformed_args,
                transformed_kwargs=transformed_kwargs,
                outputs=model_out,
            )
        return model_out
