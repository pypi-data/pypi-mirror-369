from typing import ContextManager, Optional

from tamm.context_vars import model_build_device_context as _model_build_device_context
from tamm.context_vars import resolve_pretrained_flag as _resolve_pretrained_flag
from tamm.layers.common.context_hooks.base import _BaseContextHook
from tamm.typing import LenientOptionalBool
from tamm.utils import OptionalBool as _OptionalBool


class UseMetaInitTrickContextHook(_BaseContextHook):
    def __init__(
        self,
        pretrained: "LenientOptionalBool" = _OptionalBool.NOTSET,
        pretrained_path: "Optional[str]" = None,
    ):
        self.pretrained = pretrained
        self.pretrained_path = pretrained_path

    @property
    def should_use_meta_init_trick(self) -> bool:
        return (
            _resolve_pretrained_flag(self.pretrained) == _OptionalBool.TRUE
            and self.pretrained_path is not None
        )

    def is_null(self) -> bool:
        return not self.should_use_meta_init_trick

    def _get_context_manager(self) -> "ContextManager":
        return _model_build_device_context(enable_meta_init_trick=True)
