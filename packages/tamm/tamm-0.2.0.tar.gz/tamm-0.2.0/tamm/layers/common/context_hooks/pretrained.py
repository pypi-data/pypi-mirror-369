from typing import ContextManager

from tamm.context_vars import pretrained_flag_context
from tamm.layers.common.context_hooks.base import _BaseContextHook
from tamm.typing import LenientOptionalBool
from tamm.utils import OptionalBool as _OptionalBool


class PretrainedContextHook(_BaseContextHook):
    def __init__(self, pretrained: "LenientOptionalBool" = _OptionalBool.NOTSET):
        self.pretrained = _OptionalBool(pretrained)

    def is_null(self) -> bool:
        return self.pretrained == _OptionalBool.NOTSET

    def _get_context_manager(self) -> "ContextManager":
        return pretrained_flag_context(self.pretrained)
