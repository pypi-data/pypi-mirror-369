from typing import ContextManager

from tamm.context_vars import model_build_device_context as _model_build_device_context
from tamm.layers.common.context_hooks.base import _BaseContextHook
from tamm.typing import OptionalDeviceOrString as _OptionalDeviceOrString


class DefaultDeviceContextHook(_BaseContextHook):
    def __init__(
        self,
        device: _OptionalDeviceOrString = None,
        disable_meta_device_init_trick: bool = False,
    ):
        """
        Args:
            device (:obj:`str`, optional):
                The new value for the ``torch`` default device. If ``None``,
                this will be a null context unless ``disable_meta_device_init_trick``
                is ``True``.
            disable_meta_device_init_trick (:obj:`bool`, optional):
                The flag indicating if the module should be built on actual devices.
                This is useful when we want to randomly initialize a specific module.
                If set to True, we will try to resolve the actual device that's in use.
                Defaults to ``False``.
        """
        self.device = device
        self.disable_meta_device_init_trick = disable_meta_device_init_trick

    def is_null(self) -> bool:
        return self.device is None and not self.disable_meta_device_init_trick

    def _get_context_manager(self) -> "ContextManager":
        return _model_build_device_context(
            device=self.device,
            disable_meta_init_trick=self.disable_meta_device_init_trick,
        )
