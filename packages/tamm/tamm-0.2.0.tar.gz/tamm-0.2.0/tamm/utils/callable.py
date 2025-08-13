"""
utils.callable
==============

This module implements base classes for callable objects in |tamm|.

.. autoclass:: tamm.utils.callable.CallableWithHooks
    :members: __call__, _call_impl, context_hooks, extended_context_hooks, post_hooks

.. autoclass:: tamm.utils.callable.ContextHooks
    :members:

.. autoclass:: tamm.utils.callable.PostHooks
    :members:

.. autoclass:: tamm.utils.callable.HookHandle
    :members:

.. autoclass:: tamm.utils.callable.DataclassedCallable
    :members: __call__, _call_impl, context_hooks, extended_context_hooks, post_hooks
    :show-inheritance:
"""

import contextlib as _contextlib
import dataclasses as _dataclasses
import textwrap as _textwrap
import weakref as _weakref
from typing import Any as _Any
from typing import Callable as _Callable
from typing import List as _List

from tamm import _helpers


class CallableWithHooks:
    """A base class for callable objects that use hooks to extend :meth:`.__call__`."""

    def __init__(self):
        self._post_hooks = PostHooks()
        self._context_hooks = ContextHooks()
        self._extended_context_hooks = ContextHooks()

    @property
    def post_hooks(self) -> "PostHooks":
        """A :obj:`PostHooks` for modifying the callable's return value."""
        return self._post_hooks

    @property
    def context_hooks(self) -> "ContextHooks":
        """A :obj:`ContextHooks` for modifying the call context, not covering :attr:`.post_hooks`."""
        return self._context_hooks

    @property
    def extended_context_hooks(self) -> "ContextHooks":
        """A :obj:`ContextHooks` for modifying the call context, also covering :attr:`.post_hooks`."""
        return self._extended_context_hooks

    def _call_impl(self):
        """
        The underlying implementation of :meth:`.__call__`.  Each subclass must implement this method.
        Subclasses may change the signature, since :meth:`.__call__` forwards any arguments to this one.
        """
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        """
        Calls :meth:`._call_impl` (a method that subclasses must implement)
        with hooks applied.

        Args:
            args: Optional positional arguments for :meth:`._call_impl`.
            kwargs: Optional keyword arguments for :meth:`._call_impl`.

        Returns:
            The result of ``_call_impl(*args, **kwargs)`` with hooks applied.

        This method is equivalent to the following pseudocode:

        .. code-block:: python

            with extended_context_hooks():  # enter self.extended_context_hooks
                with context_hooks(): # enter self.context_hooks
                    results = self._call_impl(*args, **kwargs)
                return self.post_hooks.apply(results)  # apply self.post_hooks
        """

        with _contextlib.ExitStack() as extended_stack:
            self.extended_context_hooks.enter_contexts(extended_stack)

            with _contextlib.ExitStack() as stack:
                self.context_hooks.enter_contexts(stack)
                result = self._call_impl(*args, **kwargs)

            return self.post_hooks.apply(result)


class _HooksBase:
    """A base class for a collection of hooks."""

    def __init__(self):
        self._hooks = {}
        self._next_hook_id = 0

    def register(self, hook: _Callable[[_Any], _Any]) -> "HookHandle":
        """
        Registers a new hook and returns a :obj:`HookHandle` for optionally
        removing it later.
        """
        hook_id = self._next_hook_id
        self._hooks[hook_id] = hook
        self._next_hook_id += 1
        return HookHandle(hooks=self, hook_id=hook_id)

    def __iter__(self):
        return iter(self._hooks.values())

    def __len__(self) -> int:
        return len(self._hooks)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return list(self)[idx]
        return _helpers.get_item_by_index(self, idx)

    def __setitem__(self, idx, value):
        if isinstance(idx, slice):
            selected_keys = list(self._hooks)[idx]
            if len(selected_keys) != len(value):
                raise ValueError(
                    f"slice specifies {len(selected_keys)} layers but value has length "
                    f"{len(value)}"
                )
            for key, hook in zip(selected_keys, value):
                self._hooks[key] = hook
        else:
            key = _helpers.get_item_by_index(self._hooks, idx)
            self._hooks[key] = value

    def __delitem__(self, idx):
        if isinstance(idx, slice):
            selected_keys = list(self._hooks)[idx]
            for key in selected_keys:
                self._hooks.pop(key)
        else:
            key = _helpers.get_item_by_index(self._hooks, idx)
            self._hooks.pop(key)

    def __repr__(self):
        items = [repr(el) + "," for el in self]
        joined = "\n".join(items)
        joined = _textwrap.indent(joined, prefix=" " * 4)
        return f"{self.__class__.__name__}(\n{joined}\n)"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self._hooks == other._hooks
                and self._next_hook_id == other._next_hook_id
            )
        return False


class PostHooks(_HooksBase):
    """
    A collection of callbacks for modifying the result of a callable.  Each hook should take
    the return type of the callable and return either a new return value or ``None``.
    """

    def apply(self, result: _Any) -> _Any:
        """
        Calls the hooks by passing ``result`` to each hook and updating the result with
        the returned value if it is not ``None``.  Calls hooks in the order of hook
        registration.
        """
        for hook in self:
            new_result = hook(result)
            if new_result is not None:
                result = new_result
        return result


class ContextHooks(_HooksBase):
    """
    A collection of hooks for altering the context of a callable. Each hook should take
    no arguments and return a context manager.
    """

    def enter_contexts(self, stack: _contextlib.ExitStack) -> None:
        """
        Calls each hook and enters the returned context.  This happens in the order of
        hook registration.

        Args:
            stack (:obj:`contextlib.ExitStack`): An exit stack for combining multiple
                context managers.
        """
        for hook in self:
            stack.enter_context(hook())


class HookHandle:
    """
    A handle for removing a hook from a :obj:`.PostHooks`.
    """

    def __init__(self, *, hooks: _HooksBase, hook_id: int):
        self._hooks_ref = _weakref.ref(hooks)
        self._hook_id = hook_id

    @property
    def _hooks(self):
        return self._hooks_ref()

    def remove(self) -> None:
        """
        Removes the registered hook.  Raises a :obj:`KeyError` if the hook has already
        been removed.
        """
        if self._hooks is None:
            return
        self._hooks._hooks.pop(self._hook_id)  # pylint: disable=protected-access

    def __enter__(self) -> "HookHandle":
        return self

    def __exit__(self, type, value, tb):  # pylint: disable=redefined-builtin
        self.remove()


class DataclassedCallable(CallableWithHooks):
    """
    A base class for dataclass objects that are also callable.  One intended use case
    for this is implementing configurable factory objects.  The class provides hook
    mechanisms for extending the behavior of :meth:`__call__`.

    Example:

        .. code-block:: python

            class RandIntFactory(DataclassedCallable):
                range_start: int
                range_end: int

                def _call_impl(self):
                    return random.randrange(self.range_start, self.range_end)

            rng = RandIntFactory(0, 10)

            print(rng())  # 3

            rng.range_start = 100
            rng.range_end = 105
            print(rng())  # 102

            print(rng(range_end=10000))  # 7217

            rng.post_hooks.register(lambda x: -x)
            print(rng())  # -104
    """

    def __init_subclass__(cls, init: bool = True, kw_only: bool = False):
        _dataclasses.dataclass(init=init, repr=False, kw_only=kw_only)(cls)

    def __post_init__(self):
        CallableWithHooks.__init__(
            self
            # call this in __post_init__ since @dataclass automatically generates __init__
        )

    def __call__(self, *override_args, **override_kwargs):
        """
        Calls :meth:`._call_impl` (a method that subclasses must implement)
        with hooks applied.  The function takes the same arguments as
        :meth:`.update_fields`.

        Args:
            override_args: Optional positional arguments that override the dataclass
                fields for the call to :meth:`._call_impl`. Before returning, the
                method resets these fields to their original values.
            override_kwargs: Optional keyword arguments that override the dataclass
                fields for the call to :meth:`._call_impl`. Before returning, the
                method resets these fields to their original values.

        Returns:
            The result of ``_call_impl(*args, **kwargs)`` with hooks and overrides applied.
        """
        original_fields = _helpers.dataclass_to_dict(self)
        try:
            self.update_fields(*override_args, **override_kwargs)
            result = super().__call__()
        finally:
            _helpers.update_dataclass_fields(self, **original_fields)
        return result

    def update_fields(self, *args, **kwargs):
        """
        A method for updating (possibly many) values of the dataclass.  The
        signature mimics the default :meth:`__init__` method of dataclasses.

        Args:
            *args: Optional positional arguments corresponding to non-keyword-only
                dataclass fields.
            **kwargs: Optional keyword arguments corresponding to dataclass fields,
                excluding the fields specified by ``*args``.
        """
        _helpers.update_dataclass_fields(self, *args, **kwargs)

    def _call_impl(self):
        """
        The underlying implementation of :meth:`.__call__`.  Each subclass must implement this method.
        The method takes no argument.

        .. caution::
            This method should not mutate any state within ``self``, and the class's behavior is
            undefined in this case.
        """
        raise NotImplementedError

    def __repr__(self):
        obj = _helpers.dataclass_to_dict(self)
        key_ordering = self._order_fields_for_repr(list(obj.keys()))
        items = [(key, obj[key]) for key in key_ordering]

        if len(self.post_hooks) > 0:
            items.append(("post_hooks", self.post_hooks))
        if len(self.context_hooks) > 0:
            items.append(("context_hooks", self.context_hooks))
        if len(self.extended_context_hooks) > 0:
            items.append(("extended_context_hooks", self.extended_context_hooks))
        reprs = [f"{key}={repr(value)}," for key, value in items]
        joined = "\n".join(reprs)
        joined = _textwrap.indent(joined, prefix=" " * 4)
        return f"{self.__class__.__name__}(\n{joined}\n)"

    def _order_fields_for_repr(self, fields: _List[str]) -> _List[str]:
        """
        A helper function that enables subclasses to customize the ordering
        of field names for :meth:`__repr__`.
        """
        return fields
