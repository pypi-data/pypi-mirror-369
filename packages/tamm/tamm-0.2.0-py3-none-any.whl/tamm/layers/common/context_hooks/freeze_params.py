from typing import ContextManager

from tamm.context_vars import freeze_params_flag_context
from tamm.layers.common.context_hooks.base import _BaseContextHook
from tamm.typing import LenientOptionalBool
from tamm.utils import OptionalBool as _OptionalBool


class FreezeParamsContextHook(_BaseContextHook):
    """
    Applies freeze params context if explicitly provided in
    ``create_builder(freeze_params=[True|False])`` calls.
    Context is not resolved here but deferred to :class:`FreezeParamsPostHook`
    """

    def __init__(self, freeze_params: "LenientOptionalBool" = _OptionalBool.NOTSET):
        self.freeze_params = _OptionalBool(freeze_params)

    def is_null(self) -> bool:
        return self.freeze_params == _OptionalBool.NOTSET

    def _get_context_manager(self) -> "ContextManager":
        return freeze_params_flag_context(self.freeze_params)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.freeze_params})"
