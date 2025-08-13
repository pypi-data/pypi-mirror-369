"""
.. autoclass:: tamm.layers.common.LayerBuilder
    :members:
    :show-inheritance:

"""
import logging as _logging

from tamm import _helpers
from tamm.utils import partial as _partial
from tamm.utils.json import JSONSerializableMixin as _JSONSerializableMixin

_logger = _logging.getLogger(__name__)


class LayerBuilder(
    _partial.DataclassedPartial,
    _JSONSerializableMixin,
    json_namespace="layers",
):
    """
    The base class for layer builders.  A :class:`.LayerBuilder` is a
    :class:`.DataclassedPartial` with a |tamm| layer class as the target callable.
    """

    def _to_json_dict_impl(self):
        result = _helpers.dataclass_to_dict(
            self.configured_args,
            omit_defaults=True,  # only include non-defaults for forward compatibility
        )
        return result

    def build(self, *override_args, **override_kwargs):
        """
        Creates and returns a configured instance of the layer.

        Args:
            override_args: Optional positional arguments to override args specified in
                the builder.  These args replace the first ``len(override_args)``
                positional args (and *all* varargs if ``override_args`` contains
                varargs) in the layer's constructor.
            override_kwargs: Optional keyword override arguments.  These arguments
                replace any additional named arguments not overriden by
                ``override_args``.

        Returns:
            The newly created layer.
        """
        return self(*override_args, **override_kwargs)


class BuildableMixin:
    """
    A mixin to attach ``.Builder`` to a class.
    This mixin is meant to supersede the ``@buildable`` decorator.
    """

    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__(**kwargs)
        _buildable_no_deprecate(cls)


def _buildable_no_deprecate(layer_cls):
    """
    Creates a :class:`.LayerBuilder` for a layer class and attaches the newly created
    type to ``layer_cls`` as the ``Builder`` attribute.
    """
    layer_name = layer_cls.__name__
    builder_name = f"{layer_name}Builder"
    builder_cls = LayerBuilder.create_subclass(
        target_callable=layer_cls, name=builder_name
    )
    builder_cls.__doc__ = (
        f"A :class:`.LayerBuilder` subclass for configuring :class:`.{layer_name}` "
        f"layers.  Use the alias :attr:`.{layer_name}.Builder` to access this class. "
        f"Please check :class:`.{layer_name}` for more details about the signature."
    )
    layer_cls.Builder = builder_cls
    return layer_cls
