import abc as _abc
import contextlib as _contextlib
from typing import ContextManager


class _BaseContextHook(_abc.ABC):
    def __call__(self) -> "ContextManager":
        if self.is_null():
            return _contextlib.nullcontext()
        return self._get_context_manager()

    @_abc.abstractmethod
    def is_null(self) -> bool:
        ...

    @_abc.abstractmethod
    def _get_context_manager(self) -> "ContextManager":
        ...
