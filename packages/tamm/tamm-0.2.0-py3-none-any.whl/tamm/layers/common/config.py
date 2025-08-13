import contextlib as _contextlib
import contextvars as _contextvars
import dataclasses as _dataclasses
import logging as _logging
from typing import TYPE_CHECKING as _TYPE_CHECKING
from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch

from tamm import _helpers
from tamm.layers.common import builder as _builder
from tamm.layers.common import context_hooks as _context_hooks
from tamm.layers.common import metadata as _metadata
from tamm.layers.common import post_hooks as _post_hooks
from tamm.utils import OptionalBool as _OptionalBool
from tamm.utils import callable as _callable
from tamm.utils import json as _tamm_json
from tamm.utils import partial as _partial

if _TYPE_CHECKING:
    from tamm._adapters_v1 import ModelAdapter
    from tamm.ao import ArchOptimizer
    from tamm.typing import (
        LenientOptionalBool,
        OptionalDeviceOrString,
        OptionalDtypeOrString,
    )


_logger = _logging.getLogger(__name__)

_EXCLUDE_METADATA_DURING_CONFIG_SERIALIZATION = _contextvars.ContextVar(
    "EXCLUDE_METADATA_DURING_CONFIG_SERIALIZATION",
    default=False,
)


@_contextlib.contextmanager
def _exclude_metadata_during_serialization_context():
    token = _EXCLUDE_METADATA_DURING_CONFIG_SERIALIZATION.set(True)
    try:
        yield
    finally:
        _EXCLUDE_METADATA_DURING_CONFIG_SERIALIZATION.reset(token)


class ModuleConfig(
    _callable.DataclassedCallable,
    _tamm_json.JSONSerializableMixin,
    json_namespace="module_configs",
    kw_only=True,
):
    """
    The base class for model and layer config types in |tamm|.  Each :obj:`ModuleConfig` is a
    dataclass and also a model factory.  Given a config, a user may set attributes to reconfigure
    fields and then build the :obj:`nn.Module` using :meth:`~.ModuleConfig.create_module`.

    To implement a new config type, a model developer should follow these steps:

    1. Subclass :class:`.ModuleConfig` and define config fields using annotated class
       variables (the same pattern as defining fields of a regular dataclass).
    2. Implement :meth:`.create_basic_builder` for the subclass.  This method should use the
       configured fields to create a :obj:`.LayerBuilder` and return it.

    This class implements the default fields :attr:`.adapters`, :attr:`.active_adapter`,
    :attr:`.arch_optimizers`, :attr:`.pretrained_path`, :attr:`.pretrained`,
    :attr:`.device`, :attr:`.dtype`, and :attr:`.freeze_params`.  For more info, please see
    each field's separate documentation.

    Example:

        .. code-block:: python

            class NormalizedLinearConfig(ModuleConfig):
                \"\"\"A simple config for a norm layer followed by a linear projection.\"\"\"

                input_dim: int
                \"\"\"The number of input features.\"\"\"

                output_dim: int
                \"\"\"The number of output features.\"\"\"

                norm_type: str = "rms_norm"
                \"\"\"The norm type.\"\"\"

                def create_basic_builder(self):
                    builder = tamm.layers.Sequential.Builder()
                    builder.named_layers = {
                        "norm": tamm.layers.norm.create_norm_builder(
                            (self.input_dim,), self.norm_type
                        ),
                        "linear": tamm.layers.Linear.Builder(
                            self.input_dim, self.output_dim
                        ),
                    }
                    return builder

            config = NormalizedLinearConfig(input_dim=3, output_dim=1)
            config.norm_type = "layer_norm"
            layer = config.create_module()
    """

    adapters: _Optional[_Dict[str, "ModelAdapter"]] = None
    """
    A dictionary that maps :obj:`str` adapter IDs to instances of :obj:`.ModelAdapter`.
    The returned builder will call these adapters to attach adapter layers (such as LoRA)
    to newly created modules.
    """

    active_adapter: _Union[int, str] = 0
    """
    The adapter to activate when initializing the model.  If a :obj:`str`, this is a key
    (adapter ID) from ``adapters``.  If an :obj:`int`, this is an index that specifies
    the adapter according to the ordering of ``adapters``.  Defaults to ``0``, which
    activates the first adapter.
    """

    arch_optimizers: _Optional[_Dict[str, "ArchOptimizer"]] = None
    """
    A dictionary that maps :obj:`str` architecture optimizer IDs to instances of
    :obj:`.ArchOptimizer`. The returned builder will apply these architecture optimizers
    (such as KVQuant) to newly created modules.
    """

    pretrained_path: _Optional[str] = None
    """
    A pretrained checkpoint path for the module's state dict.  This state should not
    include adapter state.
    """

    pretrained: "LenientOptionalBool" = _OptionalBool.NOTSET
    """
    A flag for loading pre-trained weights.  The module only loads from pretrained paths when
    ``pretrained`` is ``True``. This same flag also applies to the module adapters when
    initializing adapters.
    """

    device: "OptionalDeviceOrString" = None
    """
    The target device for module parameters and buffers.  This is also the default device
    for adapter layers, which is configurable in :obj:`.ModelAdapter`.
    """

    dtype: "OptionalDtypeOrString" = None
    """The :obj:`torch.dtype` for module parameters and buffers."""

    freeze_params: "LenientOptionalBool" = _OptionalBool.NOTSET
    """
    A flag for freezing parameters of the module (i.e., setting their ``requires_grad``
    attributes to ``False``).  This flag only applies to the base module, not adapter
    parameters, since adapters have their own ``freeze_params`` option, which commonly
    differs from the base model setting.
    """

    metadata: _metadata.ModuleMetadata = _dataclasses.field(
        default_factory=_metadata.ModuleMetadata
    )
    """
    An optional :obj:`.ModuleMetadata` for specifying the module's preprocessor,
    tokenizer, model id, and other auxiliary info about the model.
    """

    # pylint: disable=protected-access,no-self-argument

    def _order_fields_for_repr(self, fields: _List[str]) -> _List[str]:
        """Orders fields in the repr so that default fields come last."""
        default_field_names = _get_default_module_config_field_names()
        default_field_names_set = set(default_field_names)
        result = [f for f in fields if f not in default_field_names_set]
        result.extend(default_field_names)
        return result

    def create_basic_builder(self) -> _builder.LayerBuilder:
        """
        Creates and returns a configured :class:`~.layers.LayerBuilder`.  Model developers should
        implement this method for each config type.  Use attributes of ``self`` to configure the
        builder.

        Users should avoid calling this method directly and instead call :meth:`.create_module()`
        in most cases (and sometimes :meth:`~.ModuleConfig.create_builder`).

        .. caution::
            This method should not mutate any state within ``self``, and the class's behavior is
            undefined in this case.
        """
        raise NotImplementedError(
            f"{self.__class__} has not implemented create_basic_builder()"
        )

    def _call_impl(self):
        # Type casting first since ``pretrained`` can be either `bool` or `OptionalBool`
        disable_meta_device_init_trick = (
            _OptionalBool(self.pretrained) is _OptionalBool.FALSE
        )
        extended_context_hooks = [
            _context_hooks.DefaultDeviceContextHook(
                device=self.device,
                disable_meta_device_init_trick=disable_meta_device_init_trick,
            ),
            _context_hooks.PretrainedContextHook(self.pretrained),
            _context_hooks.DtypeContextHook(self.dtype),
            _context_hooks.FreezeParamsContextHook(self.freeze_params),
        ]
        with _contextlib.ExitStack() as stack:
            for extended_context_hook in extended_context_hooks:
                # Apply the same set of extended contexts to the calling context of
                # `create_basic_builder`, in case module developers instantiate concrete
                # ``nn.Modules`` within the builder.
                # fixme: Debate whether to un-support this use case and enforce builder
                # to only compose other 'pure' builders
                # (i.e., no nn.Module gets created 'within' a builder)
                stack.enter_context(extended_context_hook())

            builder = self.create_basic_builder()

        # UseMetaInitTrickContextHook is the only 'narrow scoped' context hook
        # (covering builder() only)
        builder.context_hooks.register(
            _context_hooks.UseMetaInitTrickContextHook(
                pretrained=self.pretrained, pretrained_path=self.pretrained_path
            )
        )

        for extended_context_hook in extended_context_hooks:
            # Register 'extended' context-hooks (covering both builder() and post_hooks)
            builder.extended_context_hooks.register(extended_context_hook)

        post_hooks = [
            _post_hooks.ModelInitializerPostHook(self.pretrained_path),
            _post_hooks.FreezeParamsPostHook(),
            _post_hooks.get_model_adapters_post_hook(
                adapters=self.adapters,
                active_adapter=self.active_adapter,
            ),
            _post_hooks.ArchOptimizersPostHook(
                arch_optimizers=self.arch_optimizers,
            ),
            _post_hooks.AttachConfigPostHook(self),
            _post_hooks.AttachMetadataPostHook(self.metadata),
        ]
        for post_hook in post_hooks:
            # fixme: refactor dataclass partial's hook registration API to filter out
            #  IdentityPostHook
            if not isinstance(post_hook, _post_hooks.IdentityPostHook):
                builder.post_hooks.register(post_hook)

        return builder

    @_helpers.hybridmethod
    def create_builder(self_or_cls, *args, **kwargs) -> _builder.LayerBuilder:
        """
        Creates and returns a :class:`~.LayerBuilder` according to the configured values.
        This method works as both an instance method and a class method, similar to
        :meth:`.create_module`.  See :meth:`.create_module` for a description of arguments.
        """
        if not isinstance(self_or_cls, ModuleConfig):  # called as a class method
            config = self_or_cls(*args, **kwargs)
            return config()

        return self_or_cls(*args, **kwargs)

    @_helpers.hybridmethod
    def create_module(self_or_cls, *args, **kwargs) -> _torch.nn.Module:
        """
        Creates and returns a :obj:`torch.nn.Module` according to the configured values.
        This method works as both an instance method and a class method.
        Calling it as a class method is equivalent to
        ``cls(*args, **kwargs).create_module()``.

        Args:
            *args: Optional positional arguments.  This must be empty if called as an
                instance method.
            **kwargs: Optional keyword arguments for specifying fields of the
                config.  If called as an instance method, these options override
                configured fields when creating the model, and afterward the
                fields reset to their prior state.

        Returns:
            A :obj:`nn.Module` created according to the configured values.
        """
        return self_or_cls._create_module_impl(self_or_cls, *args, **kwargs)

    @_helpers.hybridmethod
    def create_model(self_or_cls, *args, **kwargs) -> _torch.nn.Module:
        """An alias of :meth:`~.create_module`."""
        return self_or_cls._create_module_impl(self_or_cls, *args, **kwargs)

    @_helpers.hybridmethod
    def create_layer(self_or_cls, *args, **kwargs) -> _torch.nn.Module:
        """An alias of :meth:`~.create_module`."""
        return self_or_cls._create_module_impl(self_or_cls, *args, **kwargs)

    @staticmethod
    def _create_module_impl(self_or_cls, *args, **kwargs) -> _torch.nn.Module:
        builder = self_or_cls.create_builder(*args, **kwargs)
        return builder.build()

    @property
    def configured_args(self) -> "ModuleConfig":
        """A deprecated property that returns ``self`` (included for backward compatibility)."""
        return self

    def update_configured_args(self, *args, **kwargs) -> None:
        """
        A deprecated alias of :func:`.update_fields`.
        """
        self.update_fields(*args, **kwargs)

    def _to_json_dict_impl(self):
        result = _helpers.dataclass_to_dict(
            self, omit_defaults=True  # only non-defaults for forward compatibility
        )
        if "pretrained" in result:
            del result["pretrained"]
            _logger.warning(
                "Dropping pretrained option when serializing ModuleConfig to JSON. "
                "Please specify this argument explicitly after loading the config."
            )
        if _EXCLUDE_METADATA_DURING_CONFIG_SERIALIZATION.get():
            result.pop("metadata", None)
        return result

    @classmethod
    def _from_json_dict_impl(cls, **raw_dict):
        raw_dict = _helpers.maybe_get_enum_member_for_all_str_enums(raw_dict, cls)
        is_pretrained = raw_dict.pop("pretrained", False)
        if is_pretrained:
            _logger.warning(
                "Dropping pretrained=True option when loading ModuleConfig from JSON. "
                "Please specify this argument explicitly after loading the config."
            )
        return super()._from_json_dict_impl(**raw_dict)

    @property
    def has_adapters(self) -> bool:
        """
        Returns ``True`` if the config or any of its child configs contains an
        adapter in the ``adapters`` field.  Returns ``False`` otherwise.  A child
        config is any :obj:`ModuleConfig` serialized when serializing the parent config
        with :func:`tamm.utils.json.dumps`.
        """
        with _exclude_metadata_during_serialization_context():
            for obj in _tamm_json.iter_json_serializable(self):
                if (
                    isinstance(obj, ModuleConfig)
                    and obj.adapters is not None
                    and len(obj.adapters) > 0
                ):
                    return True
        return False


def _get_default_module_config_field_names():
    return [f.name for f in _dataclasses.fields(ModuleConfig)]


def create_config_type_from_builder_factory(
    builder_factory: _Callable[..., _builder.LayerBuilder],
    *,
    name: str,
    module_path: _Optional[str] = None,
) -> type:
    """
    A function that automatically derives a :class:`.ModuleConfig` subclass from a
    builder factory function.

    Args:
        builder_factory (:obj:`callable`): A callable that takes arbitrary arguments and
            returns a :obj:`.LayerBuilder`.  The function derives the config type's fields
            from the signature of this callable.
        name (:obj:`str`): The name of the new type.
        module_path (:obj:`str`, None): Optional Python module path for the new type.
            If ``None``, this defaults to ``builder_factory.__module__``.

        Returns:
            The new :class:`.ModuleConfig` subclass.
    """
    if module_path is None:
        module_path = builder_factory.__module__
    return type(
        name,
        (_ModuleConfigFromBuilderFactory,),
        {"__module__": module_path},
        _builder_factory=builder_factory,
    )


class _ModuleConfigFromBuilderFactory(ModuleConfig):
    """
    A helper class for :func:`.create_config_type_from_builder_factory`.
    The general strategy is to create a :class:`.DataclassedPartial` type for
    the ``builder_factory``, then wrap the new type into a :class:`.ModuleConfig`.

    This signature of `__init__()` takes the same arguments as the builder factory,
    plus additional "standard" fields from :class:`.ModuleConfig`.  We use the
    :class:`.DataclassedPartial` type to translate between the builder factory's
    arguments and the dataclass fields (especially for varargs and varkwargs, this
    gets complicated, but we can rely on :class:`.DataclassedPartial` to do this).
    """

    # pylint: disable-next=signature-differs
    def __init_subclass__(cls, _builder_factory=None, **kwargs):
        # create a DataclassedPartial type for the builder factory
        if _builder_factory is not None:
            if hasattr(cls, "_partial_type"):
                raise RuntimeError(f"{cls} already has a _partial_type")
            cls._partial_type = _partial.DataclassedPartial.create_subclass(
                _builder_factory, name=f"{cls.__name__}PartialType"
            )

            # inject fields from the DataclassedPartial into our ModuleConfig:
            for field in cls._get_builder_factory_fields():
                _helpers.set_annotated_class_attr(cls, field.name, field, field.type)
        else:
            # we take this branch when subclassing a ModuleConfig that was already
            # derived from a builder factory
            pass

        super().__init_subclass__(
            **kwargs,
            init=False,  # because we define our own init
            kw_only=True,  # to make clear that new fields are only passed by keyword
        )

    @classmethod
    def _get_builder_factory_fields(cls):
        """Returns fields specified by the builder factory"""
        # pylint: disable=protected-access
        default_field_names = set(_get_default_module_config_field_names())
        return [
            field
            for field in _dataclasses.fields(cls._partial_type._ARGS_DATACLASS)
            if field.name not in default_field_names
        ]

    @classmethod
    def _get_standard_fields(cls):
        """Returns fields not specified by the builder factory"""
        builder_factory_field_names = {
            f.name for f in cls._get_builder_factory_fields()
        }
        return [
            field
            for field in _dataclasses.fields(cls)
            if field.name not in builder_factory_field_names
        ]

    def __init__(self, *args, **kwargs):
        super().__init__()

        # assign values for standard fields from kwargs
        standard_fields = {f.name: f for f in self._get_standard_fields()}
        for name, field in standard_fields.items():
            if not field.init:
                continue
            if name in kwargs:
                value = kwargs.pop(name)
            elif field.default_factory is not _dataclasses.MISSING:
                value = field.default_factory()
            elif field.default is not _dataclasses.MISSING:
                value = field.default
            else:
                raise TypeError(
                    f"{self.__class__.__name__}.__init__() missing required "
                    f"keyword-only argument: '{name}'"
                )
            setattr(self, name, value)

        # assign values from partial for remaining fields
        # (we use the partial to translate the builder factory's arguments
        # into dataclass fields, which is not trivial)
        partial = self._partial_type(*args, **kwargs)
        for field in self._get_builder_factory_fields():
            value = getattr(partial.configured_args, field.name)
            setattr(self, field.name, value)

    def update_fields(self, *args, **kwargs):
        """
        Updates (possibly many) fields of the configs.  The signature
        should match that of :meth:`.__init__()`, except that not
        all positional arguments are required.
        """

        if len(kwargs) > 0:
            # assign values for standard fields from kwargs
            standard_fields = {f.name: f for f in self._get_standard_fields()}
            for name, field in standard_fields.items():
                if name in kwargs:
                    value = kwargs.pop(name)
                    setattr(self, name, value)

        if len(args) == 0 and len(kwargs) == 0:
            return

        # copy current values into a partial
        # (we use the partial to translate the builder factory's arguments
        # into dataclass fields, which is not trivial)
        partial = self._partial_type(*args, **kwargs)
        for field in self._get_builder_factory_fields():
            value = getattr(self, field.name)
            setattr(partial.configured_args, field.name, value)

        # update partial values
        partial.update_configured_args(*args, **kwargs)

        # copy values back
        for field in self._get_builder_factory_fields():
            value = getattr(partial.configured_args, field.name)
            setattr(self, field.name, value)

    def create_basic_builder(self) -> _builder.LayerBuilder:
        # copy fields from ModuleConfig to partial
        partial = self._partial_type()
        for field in self._get_builder_factory_fields():
            value = getattr(self, field.name)
            setattr(partial.configured_args, field.name, value)

        # call partial to create builder
        return partial()


# DEPRECATED
# pylint: disable=all
# isort: off

from tamm import _compat  # noqa

_compat.register_backward_compatibility_import(
    __name__,
    "LayerConfig",
    "tamm.layers.common.config.ModuleConfig",
)
