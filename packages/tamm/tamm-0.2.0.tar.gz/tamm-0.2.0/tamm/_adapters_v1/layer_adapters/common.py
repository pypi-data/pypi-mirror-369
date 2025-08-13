import enum as _enum
from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List

import torch.nn as _nn

from tamm import _helpers
from tamm._helpers import case_insensitive_lookup
from tamm.utils import partial as _partial
from tamm.utils.json import JSONSerializableMixin as _JSONSerializableMixin


class AdapterMode(str, _enum.Enum):
    TRANSFORM_INPUTS = "TRANSFORM_INPUTS"
    TRANSFORM_OUTPUTS = "TRANSFORM_OUTPUTS"

    @classmethod
    def _missing_(cls, value):
        return case_insensitive_lookup(cls, value)


class LayerAdapter(_nn.Module):
    """
    Base class for implementing a layer adapter.
    """

    def __init__(self):
        super().__init__()
        self._child_adapters = {}

        self._has_input_transform = (
            _helpers.get_function_from_maybe_method(self._transform_inputs)
            is not LayerAdapter._transform_inputs
            # we set this attribute during __init__ so that we can use
            # :attr:`has_input_transform` during forward() -- if we dynamically
            # compute this instead during :meth:`forward()` it conflicts
            # with torch.compile() and torch.jit.trace()
        )
        self._has_output_transform = (
            _helpers.get_function_from_maybe_method(self._transform_outputs)
            is not LayerAdapter._transform_outputs
        )

    def _transform_inputs(self, *, args: _Any, kwargs: _Any) -> _Any:
        return args, kwargs

    def _transform_outputs(  # pylint: disable=unused-argument
        self,
        *,
        args: _Any,
        kwargs: _Any,
        transformed_args: _Any,
        transformed_kwargs: _Any,
        outputs: _Any,
    ) -> _Any:
        return outputs

    @property
    def has_input_transform(self) -> bool:
        """
        Returns :obj:`False` if the adapter uses the base input transform (which is a
        no-op) and :obj:`True` otherwise.
        """
        return self._has_input_transform

    @property
    def has_output_transform(self) -> bool:
        """
        Returns :obj:`False` if the adapter uses the base output transform (which is a
        no-op) and :obj:`True` otherwise.
        """
        return self._has_output_transform

    def forward(
        self,
        mode: AdapterMode,
        *,
        args: _Any,
        kwargs: _Any,
        transformed_args: _Any = None,
        transformed_kwargs: _Any = None,
        outputs: _Any = None,
    ):
        mode = _helpers.get_enum_member_from_name(AdapterMode, mode)
        if mode is AdapterMode.TRANSFORM_INPUTS:
            return self._transform_inputs(args=args, kwargs=kwargs)
        return self._transform_outputs(
            outputs=outputs,
            args=args,
            kwargs=kwargs,
            transformed_args=transformed_args,
            transformed_kwargs=transformed_kwargs,
        )

    def register_child_adapter(self, name: str, adapter: "LayerAdapter"):
        """
        Register a child adapter.
        """
        self.register_module(name, adapter)
        self._child_adapters[name] = adapter

    def register_child_adapters(self, adapters: _Dict[str, "LayerAdapter"]):
        """
        Register child adapters.
        """
        for ad_name, adapter in adapters.items():
            self.register_child_adapter(ad_name, adapter)

    def freeze(self):
        """
        Make the parameters of the adapter un-trainable.
        """
        for param in self.parameters():
            param.requires_grad = False

    def unfreeze(self):
        """
        Make the parameters of the adapter trainable.
        """
        for param in self.parameters():
            param.requires_grad = True

    def reset_parameters(self):
        """
        Reset adapter parameters.
        """
        for _, adapter in self._child_adapters.items():
            adapter.reset_parameters()

    def reset_adapter_parameters(self):
        """
        Same as :py:meth:`reset_parameters`. Adds backward compatibility with adapters v0 implementation.
        """
        self.reset_parameters()


class MergeableLayerAdapterMixin:
    """
    An adapter mixin which implements a merge method to merge adapter
    weights into the wrapped layer's weights.
    """

    def merge_adapter(self, wrapped_module: _nn.Module):
        raise NotImplementedError("This method is not implemented.")


# pylint: disable-next=abstract-method
class AdapterWithExtraInputs(LayerAdapter):
    """
    An adapter which accepts extra keyword arguments as inputs,
    besides the args and kwargs of the layer it adapts
    """

    extra_input_names: _List[str]


class LayerAdapterConfig(
    _partial.DataclassedPartial,
    _JSONSerializableMixin,
    json_namespace="adapters",
):
    """
    Base class for implementing a layer adapter config.
    """

    def create_adapter(
        self,
        *override_args,
        **override_kwargs,
    ) -> LayerAdapter:
        """
        Create a configured adapter.

        Args:
            override_args: Optional positional arguments to override args specified in
                the config.  These args replace the first ``len(override_args)``
                positional args (and *all* varargs if ``override_args`` contains
                varargs) in the adapter's constructor.
            override_kwargs: Optional keyword override arguments. These arguments
                replace any additional named arguments not overriden by
                ``override_args``.
        Returns:
            The newly created adapter.
        """
        return self(*override_args, **override_kwargs)

    def _to_json_dict_impl(self):
        result = _helpers.dataclass_to_dict(
            self.configured_args,
            omit_defaults=True,  # only include non-defaults for forward compatibility
        )
        return result


def attach_config_class(base_cls):
    """
    A class decorator that creates a config for an adapter
    and attaches that type to the class as the attribute
    ``Config``.
    """
    adapter_name = base_cls.__name__
    config_name = f"{adapter_name}Config"
    config_cls = LayerAdapterConfig.create_subclass(
        target_callable=base_cls, name=config_name
    )
    config_cls.__doc__ = (
        f"A :py:class:`.BaseAdapterConfig` subclass for configuring "
        f":py:class:`.{adapter_name}` adapters.  Use the alias :attr:`."
        f"{adapter_name}.Config` to access this class. "
        f"Please check :class:`.{adapter_name}` for more details about the "
        "signature."
    )
    base_cls.Config = config_cls
    return base_cls


def _validate_adapters(adapters: _Dict[str, LayerAdapter]):
    if not adapters:
        raise ValueError(
            "The input adapters list is empty. In order to construct a composite "
            "adapter, there should be at least one adapter in the list."
        )


class CompositeInputTransform(LayerAdapter):
    """
    A base class for composite layer adapters that only transform the wrapped layer's
    inputs, not outputs.

    Args:
        adapters (:obj:`dict` that maps :obj:`str` to :obj:`LayerAdapter`): A dictionary
            that maps child adapter IDs to corresponding adapters.
    """

    def __init__(self, adapters: _Dict[str, LayerAdapter]):
        super().__init__()
        _validate_adapters(adapters)
        for adapter in adapters.values():
            if adapter.has_output_transform:
                raise ValueError(
                    "CompositeInputTransform received a child adapter that transforms "
                    "outputs."
                )
        self.register_child_adapters(adapters)


class CompositeOutputTransform(LayerAdapter):
    """
    A base class for composite layer adapters that only transform the wrapped layer's
    outputs, not inputs.

    Args:
        adapters (:obj:`dict` that maps :obj:`str` to :obj:`LayerAdapter`): A dictionary
            that maps child adapter IDs to corresponding adapters.
    """

    def __init__(self, adapters: _Dict[str, LayerAdapter]):
        super().__init__()
        _validate_adapters(adapters)
        for adapter in adapters.values():
            if adapter.has_input_transform:
                raise ValueError(
                    "CompositeOutputTransform received a child adapter that transforms "
                    "inputs."
                )
        self.register_child_adapters(adapters)
