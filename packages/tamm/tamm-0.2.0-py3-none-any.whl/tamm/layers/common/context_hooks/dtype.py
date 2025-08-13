import contextlib as _contextlib
from typing import ContextManager, Literal, Union

import torch as _torch

from tamm import _helpers
from tamm.layers.common.context_hooks.base import _BaseContextHook


@_contextlib.contextmanager
def dtype_context_manager(
    dtype: Union[
        _torch.dtype, Literal["float", "double", "float16", "float32", "bfloat16"]
    ]
):
    original_dtype = _torch.get_default_dtype()
    dtype = _helpers.get_dtype_from_maybe_string(dtype)
    _torch.set_default_dtype(dtype)
    try:
        yield
    finally:
        _torch.set_default_dtype(original_dtype)


class DtypeContextHook(_BaseContextHook):
    def __init__(self, dtype=None):
        self.dtype = dtype

    def is_null(self) -> bool:
        return self.dtype is None

    def _get_context_manager(self) -> "ContextManager":
        return dtype_context_manager(self.dtype)
