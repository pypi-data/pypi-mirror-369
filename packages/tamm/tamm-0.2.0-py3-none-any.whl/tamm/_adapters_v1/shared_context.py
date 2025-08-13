# pylint: disable=unused-argument

from typing import Any as _Any
from typing import Callable as _Callable
from typing import Dict as _Dict

import torch.nn as _nn
from torch.utils.hooks import RemovableHandle as _RemovableHandle


class SharedContext:
    """
    An object for enabling context sharing between modules.

    Provides pre and post forward hooks which create a shared context
    dictionary, populate it with data, consume the data and delete the
    shared dictionary.

    In a typical use case, :py:meth:`register_context_creation_hook` and
    :py:meth:`register_context_deletion_hook` are called on ``ModuleA``
    and :py:meth:`register_context_population_hook` and
    :py:meth:`register_context_retrieval_hook` are called on its submodules.
    """

    def __init__(self):
        self._context = None

    def _create_context(self):
        """
        Create shared context dictionary.
        """
        self._context = {}

    def _delete_context(self):
        """
        Delete shared context dictionary.
        """
        del self._context
        self._context = None

    def register_context_creation_hook(
        self, module: _nn.Module, *input_keys: str
    ) -> _RemovableHandle:
        """
        Register a pre-forward hook on the module which creates
        the shared context dictionary.

        Args:
            module (:py:class:`_nn.Module`): Module on which hook is registered
        """

        def context_creation_pre_forward_hook(
            mod: _nn.Module, args: _Any, kwargs: _Any
        ):
            self._create_context()

        return module.register_forward_pre_hook(
            context_creation_pre_forward_hook, prepend=True, with_kwargs=True
        )

    def register_context_population_hook(
        self, module: _nn.Module, hook_fn: _Callable, prepend: bool = False
    ) -> _RemovableHandle:
        """
        Register a pre-forward hook on a module which populates the shared context
        dictionary with data that is consumed by other modules.

        Args:
            module (:py:class:`_nn.Module`): Module on which hook is registered
            hook_fn (:obj:`callable`): A callable with the signature
                ``hook(module, context, args, kwargs)``, where context is the shared
                context dictionary, and args and kwargs are inputs to the forward method
                of the module. This callable populates the context dictionary
                with data and optionally changes the args and kwargs which are
                passed to module.
            prepend (:obj:`bool`):  If true, the provided hook will be fired
                before all existing forward_pre hooks on module. Otherwise, the
                provided hook will be fired after all existing forward_pre hooks.
                Defaults to ``False``.
        """

        def context_population_pre_forward_hook(
            mod: _nn.Module, args: _Any, kwargs: _Any
        ):
            return hook_fn(mod, self._context, args, kwargs)

        return module.register_forward_pre_hook(
            context_population_pre_forward_hook, prepend=prepend, with_kwargs=True
        )

    @staticmethod
    def get_input_forwarding_hook(*input_keys: str) -> _Callable:
        """
        Returns a hook with the signature ``hook(module, context, args, kwargs)``
        which extracts inputs identified by ``input_keys`` from the kwargs passed to
        module and adds them to the context dictionary.

        This hook can be passed to :py:meth:`register_context_population_hook`
        for enabling a module to forward inputs passed to it to other submodules.

        Args:
            *input_keys: Variable number of names of extra inputs which are extracted
                from kwargs passed to module
        """

        def input_forwarding_hook(
            mod: _nn.Module, context: _Dict[str, _Any], args: _Any, kwargs: _Any
        ):
            new_kwargs = {}
            for key, val in kwargs.items():
                if key in input_keys:
                    context[key] = val
                else:
                    new_kwargs[key] = val
            return args, new_kwargs

        return input_forwarding_hook

    def register_context_deletion_hook(self, module: _nn.Module) -> _RemovableHandle:
        """
        Register a forward hook on the module which deletes the shared context
        dictionary, created by the context creation hook.

        This hook should be registered on a module which is guaranteed to be executed
        after all the modules which depend on the shared context for data
        have been executed.

        For a typical use case, both context creation hook and deletion
        hook are installed on a top level module, which forwards some extra
        inputs passed to it to some of its submodules, which expect these
        extra inputs.

        Args:
            module (:py:class:`_nn.Module`): Module on which hook is registered
        """

        def context_deletion_forward_hook(mod: _nn.Module, args: _Any, output: _Any):
            self._delete_context()

        return module.register_forward_hook(context_deletion_forward_hook, prepend=True)

    def register_context_retrieval_hook(
        self, module: _nn.Module, *input_keys: str
    ) -> _RemovableHandle:
        """
        Register hook on a submodule which retrieves data, identified by
        ``input_keys`` from the shared context dictionary.

        Args:
            module (:py:class:`_nn.Module`): Module on which hooks are registered
            *input_keys: Variable number of names of extra inputs which are retrieved
                from the shared context dictionary
        """

        def context_retrieval_hook(mod: _nn.Module, args: _Any, kwargs: _Any):
            for key in input_keys:
                if key in self._context:
                    kwargs[key] = self._context[key]
            return args, kwargs

        return module.register_forward_pre_hook(
            context_retrieval_hook, prepend=True, with_kwargs=True
        )
