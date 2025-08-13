import inspect as _inspect
import logging as _logging
from typing import Union as _Union

from tamm.layers import ModuleConfig as _ModuleConfig
from tamm.layers.common import _BaseConfigurableMixin
from tamm.layers.common.metadata import ModuleMetadata as _ModuleMetadata

_logger = _logging.getLogger(__name__)


class ModelMixin(_BaseConfigurableMixin):
    """
    A mixin for common functionality of |tamm| models.  Model subclasses must implement
    the ``.create_basic_builder()`` method.

    Here is what this mixin brings to the model:

    1. Creates :class:`.ModuleConfig` and :class:`.LayerBuilder` subclasses for the model
       type and attaches them to the model class as ``.Config`` and ``.Builder``
       attributes.
    2. Implements the :meth:`~ModuleMixin.create_builder` method, which wraps
       ``.create_basic_builder()`` to implement common functionality across models.
    3. Implements the ``<model_cls>.create()`` method, which is an
       alias of ``<model_cls>.Builder.build()``
    4. Decorates the model's initializer to collect usage telemetry.

    """

    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls._should_update_signature():
            cls._update_create_builder_signature()
            cls._update_create_signature()

    @classmethod
    def _should_update_signature(cls):
        """
        This predicate determine whether the signature for create_builder() should
        be updated
        """

        if "create_builder" in cls.__dict__:
            # model_yz = config_yz.create_model()
            _logger.debug(
                f"Skipping update to the signature of {cls.__name__}.create_builder() "
                "because this class overrides create_builder().  This may impact the "
                f"ModuleConfig type for {cls}."
            )
            return False
        return True

    @staticmethod
    def _get_base_create_builder_signature():
        return _inspect.signature(ModelMixin.create_builder.__func__)

    @property
    def config(self) -> _Union["_ModuleConfig", None]:
        """The :obj:`ModuleConfig` used to create the model."""
        return getattr(self, "_tamm_model_config", None)

    @config.setter
    def config(self, value: "_ModuleConfig") -> None:
        self._tamm_model_config = value

    @property
    def metadata(self) -> _Union["_ModuleMetadata", None]:
        """
        A :obj:`ModuleMetadata` for the model (or ``None`` if this has not been set).
        """
        return getattr(self, "_tamm_model_metadata", None)

    @metadata.setter
    def metadata(self, value: "_ModuleMetadata") -> None:
        self._tamm_model_metadata = value
