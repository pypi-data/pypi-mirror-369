"""
utils.partial
=============

This module implements the :class:`.DataclassedPartial` concept.  This is a base class
for some config-like classes in |tamm|, such as :class:`.LayerBuilder`.

The purpose of a :class:`.DataclassedPartial` is to organize the configuration of a
callable's arguments without actually calling the callable.  The callable is typically
a complex class, such as a |tamm| layer.

:class:`.DataclassedPartial` is very similar to Python's :func:`functools.partial`
concept.  The main difference is that :class:`.DataclassedPartial` provides a
dataclass-style user experience for updating arguments to the target callable.  Unlike
the basic partial, we also create an explicit subclass of :class:`.DataclassedPartial`
for each target callable.

:class:`.DataclassedPartial` provides a Pythonic solution for object configuration.
It avoids config-related boilerplate code, since :class:`.DataclassedPartial`
automatically derives each config class from the function or class being configured.
This also preserves the regular user experience of the callable---if desired, users
may still instantiate objects or call functions directly with normal arguments,
avoiding config objects altogether.

**Examples:**

Configure a class instance prior to instantiation:

.. code-block:: python

    class Square:
        def __init__(self, side_length, color=None):
            self.side_length = side_length
            self.color = color

        def __str__(self):
            return f"Square(side_length={self.side_length}, color={self.color})"


    SquareConfig = DataclassedPartial.create_subclass(Square, name="SquareConfig")
    config = SquareConfig(8)
    config.color = "blue"
    square = config()
    print(square)  # 'Square(side_length=8, color=blue)'


Configure a class instance when the class initializer takes varargs and kwargs:

.. code-block:: python

    class Polygon:
        def __init__(self, *side_lengths, **metadata):
            self.side_lengths = side_lengths
            self.metadata = metadata

        def __str__(self):
            return (
                f"Polygon(side_lengths={self.side_lengths}, metadata={self.metadata})"
            )


    PolygonConfig = DataclassedPartial.create_subclass(Polygon, name="PolygonConfig")
    config = PolygonConfig(color="purple")
    config.side_lengths = [3, 4, 5]
    config.metadata["weight"] = 7
    polygon = config()
    print(polygon)
    # 'Polygon(side_lengths=(3, 4, 5), metadata={'color': 'purple', 'weight': 7})'


Use hooks to modify the result of a partial:

.. code-block:: python

        class TensorHolder:
            def __init__(self, value: float):
                self.tensor = torch.tensor(value, dtype=torch.float)

            def __str__(self):
                return f"TensorHolder(tensor={repr(self.tensor)})"


        TensorHolderPartial = DataclassedPartial.create_subclass(
            TensorHolder, name="TensorHolderPartial"
        )
        partial = TensorHolderPartial(value=0)

        print(partial())  # "TensorHolder(tensor=tensor(0.))"


        def use_gpu_context_hook():
            ""\"
            A context hook that adds a ``with torch.device("cuda"):`` context when
            creating the TensorHolder in ``partial.__call__()``.  Within the context,
            this sets the ``torch`` default device to a GPU.
            ""\"
            return torch.device("cuda")


        def return_tensor_post_hook(result):
            ""\"
            A post hook that causes the partial to return the ``tensor`` from the
            TensorHolder rather than the TensorHolder itself.
            ""\"
            return result.tensor


        def add_7_post_hook(tensor):
            ""\"A post hook that adds 7 to the resulting tensor.""\"
            tensor.add_(7)


        partial.context_hooks.register(use_gpu_context_hook)
        partial.post_hooks.register(return_tensor_post_hook)
        partial.post_hooks.register(add_7_post_hook)  # hooks fire in registration order
        print(partial())  # "tensor(7., device='cuda:0')"


Configure only some arguments of a function (similar to :func:`functools.partial`):

.. code-block:: python

    def y(x, m=1, b=0):
        return m * x + b

    PartialY = DataclassedPartial.create_subclass(y, name="PartialY")
    partial_y = PartialY(m=2, b=2)
    print(partial_y(0))  # '2'
    print(partial_y(2))  # '6'
    partial_y.m = 0
    print(partial_y(2))  # '2'


.. autoclass:: tamm.utils.partial.DataclassedPartial
    :members:
    :special-members: __call__, __init_subclass__
"""

import dataclasses as _dataclasses
import inspect as _inspect
import logging as _logging
import textwrap as _textwrap
import typing as _typing
from typing import Any as _Any
from typing import Callable as _Callable
from typing import Optional as _Optional

from tamm import _compat, _helpers
from tamm.utils import callable as _callable

_logger = _logging.getLogger(__name__)


class DataclassedPartial(_callable.CallableWithHooks):
    """
    A base class for configs.  For each subclass of :class:`.DataclassedPartial`,
    the constructor's signature matches the signature of the target callable.
    """

    _CALLABLE: _Optional[_Callable[..., _Any]] = None

    def __init_subclass__(
        cls, /, target_callable: _Optional[_Callable[..., _Any]] = None, **kwargs
    ):
        """
        This method is called when :class:`.DataclassedPartial` is subclassed.  It
        sets up functionality for configuring the callable.

        Args:
            target_callable (:obj:`callable`):  The function or class that the new
                :class:`.DataclassedPartial` will configure.
        """
        if target_callable is None:
            return
        if not callable(target_callable):
            raise TypeError(f"target_callable {target_callable} must be callable")

        cls._CALLABLE = staticmethod(target_callable)
        cls._ARG_SPEC = cls._get_target_callable_arg_spec(target_callable)
        cls._ARGS_DATACLASS = cls._make_dataclass_for_arg_spec(
            cls._ARG_SPEC, name=cls.__name__ + "Args"
        )
        cls._attach_arg_forwarding_properties()
        cls.__signature__ = _inspect.signature(target_callable)

    @staticmethod
    def _get_target_callable_arg_spec(
        target_callable: _Callable,
    ) -> _inspect.FullArgSpec:
        """
        Returns an argspec for ``target_callable`` that is aligned with the
        result of :func:`inspect.signature`.
        """

        # We would like to call inspect.getfullargspec() because the return arg spec
        # is easy to work with.  However, getfullargspec() is not always aligned with
        # inspect.signature()... see the inspect module for details.  In order to
        # force this alignment, we create a wrapper function with the desired signature
        # and then call getfullargspec() on it.

        def wrapper(*args, **kwargs):
            return target_callable(*args, **kwargs)

        wrapper.__signature__ = _inspect.signature(target_callable)
        return _inspect.getfullargspec(wrapper)

    @staticmethod
    def _make_dataclass_for_arg_spec(
        arg_spec: _inspect.FullArgSpec, *, name: str
    ) -> _typing.Type:
        """
        Creates a dataclass type for holding a function's arguments.

        Args:
            arg_spec (:obj:`inspect.FullArgSpec`): The arg spec for the function.
            name (:obj:`str`): The name for the dataclass type.

        Returns:
            The new dataclass type with fields corresponding to the args, varargs,
            kwonlyargs, and kwargs paramter names from the argspec.  The defaults for
            each field also match the defaults from ``arg_spec``.
        """
        defaults = {}
        if arg_spec.defaults is not None:
            matching_args = arg_spec.args[-len(arg_spec.defaults) :]
            defaults.update(zip(matching_args, arg_spec.defaults))
        if arg_spec.kwonlydefaults is not None:
            defaults.update(arg_spec.kwonlydefaults)

        fields = []
        for arg in arg_spec.args + arg_spec.kwonlyargs:
            arg_type = arg_spec.annotations.get(arg, _typing.Any)
            default = defaults.get(arg, None)
            field = (arg, arg_type, default)
            fields.append(field)

        if arg_spec.varargs is not None:
            default = _dataclasses.field(default_factory=tuple)
            field = (arg_spec.varargs, _typing.Tuple[_typing.Any], default)
            fields.append(field)

        if arg_spec.varkw is not None:
            default = _dataclasses.field(default_factory=dict)
            field = (arg_spec.varkw, _typing.Dict[str, _typing.Any], default)
            fields.append(field)

        return _dataclasses.make_dataclass(name, fields)

    @classmethod
    def _attach_arg_forwarding_properties(cls):
        """
        Attaches properties that forward arg values from the configured_args dataclass
        to the parent DataclassedPartial object if there is no name conflict
        """
        for name in cls._ARGS_DATACLASS.__dataclass_fields__:
            if name in dir(cls):
                continue  # name conflict
            forwarder = _ConfiguredArgForwarder(name)
            prop = property(forwarder.get, forwarder.set)
            prop.__doc__ = f"The ``{name}`` configured argument."
            setattr(cls, name, prop)

    def __init__(self, *args, **kwargs):
        super().__init__()
        if self._CALLABLE is None:
            cls = self.__class__
            raise RuntimeError(
                f"Cannot init {cls} because it does not have a target callable."
            )
        self._configured_args = self._convert_callable_args_to_dataclass(
            *args, **kwargs
        )

    @classmethod
    def create_subclass(
        cls,
        target_callable: _Callable[..., _Any],
        *,
        name: str,
        module_path: _Optional[str] = None,
    ) -> _typing.Type["DataclassedPartial"]:
        """
        Creates a new :class:`DataclassedPartial` subclass for a target callable.  The
        purpose of this type is to help configure arguments for the callable prior to
        calling it.

        Args:
            target_callable (:obj:`callable`): A class or other callable.
            name (:obj:`str`): The name of the new type.
            module_path (:obj:`str`, None): Optional module path of the target_callable
                to be registered.

        Returns:
            The new type.
        """
        return type(
            name,
            (cls,),
            {
                "__module__": target_callable.__module__
                if module_path is None
                else module_path
            },
            target_callable=target_callable,
        )

    @property
    def configured_args(self):
        """
        The configured arguments as a dataclass.  The fields of the dataclass match the
        signature of the target callable.

        .. tip::
            Except in cases of name conflicts, we can also access attributes of
            :attr:`configured_args` directly on the :obj:`.DataclassedPartial`.  For
            example, if an arg is named ``dim``, then ``config.dim`` forwards to
            ``config.configured_args.dim``.
        """
        return self._configured_args

    def update_configured_args(self, *new_args, **new_kwargs):
        """
        Updates :attr:`.configured_args` with values from arguments to the target
        callable.  For fields not specified by ``*new_args, **new_kwargs``, the
        value in :attr:`.configured_args` does not change.

        Args:
            new_args: Optional positional arguments to overwrite args specified in
                :attr:`configured_args`.  These args replace the first
                ``len(new_args)`` positional args (and *all* varargs if
                ``new_args`` contains varargs).
            new_kwargs: Optional keyword arguments.  These arguments replace additional
                named arguments not replaced by ``new_args``.
        """

        args, kwargs = self._merge_override_args_with_configured_args(
            *new_args, **new_kwargs
        )
        self._configured_args = self._convert_callable_args_to_dataclass(
            *args, **kwargs
        )

    def _convert_callable_args_to_dataclass(self, *args, **kwargs):
        """
        Given *args, **kwargs for the target callable, this helper creates a
        ``cls._ARGS_DATACLASS`` dataclass instance that holds these arguments.  The
        signature for dataclass creation is different from that of the target callable,
        and this conversion requires mapping everything in *args, **kwargs to the right
        parameter name of the callable.
        """

        # First map args to positional params (excluding varargs):
        result = self._ARGS_DATACLASS(
            **dict(zip(self._ARG_SPEC.args, args))
            # note: args may only cover some of ARG_SPEC.args (zip stops once any
            # sequence is exhausted). kwargs may cover additional positional args, and
            # any remaining entries in ARG_SPEC.args receive None as default
        )

        # Fill any positional args passed with keywords in **kwargs:
        for idx, name in enumerate(self._ARG_SPEC.args):
            if name not in kwargs:
                continue
            if idx < len(args):
                raise TypeError(f"got multiple values for argument '{name}'")
            setattr(result, name, kwargs.pop(name))

        if self._ARG_SPEC.varargs is not None:
            # Assign any remaining args to varargs:
            setattr(result, self._ARG_SPEC.varargs, args[len(self._ARG_SPEC.args) :])
        elif len(args) > len(self._ARG_SPEC.args):
            raise TypeError(
                f"{self._CALLABLE}() takes {len(self._ARG_SPEC.args)} positional "
                f"arguments but {len(args)} were given"
            )

        # Assign keyword-only args:
        for name in self._ARG_SPEC.kwonlyargs:
            if name in kwargs:
                setattr(result, name, kwargs.pop(name))

        if self._ARG_SPEC.varkw is not None:
            # Assign any remaining kwargs to varkw:
            setattr(result, self._ARG_SPEC.varkw, kwargs)
        elif len(kwargs) > 0:
            raise TypeError(f"Received unexpected keyword arguments {list(kwargs)}")

        return result

    def __call__(self, *override_args, **override_kwargs) -> _Any:
        """
        Calls the target callable with the configured args.

        Args:
            override_args: Optional positional arguments to override args specified in
                :attr:`configured_args`.  These args replace the first
                ``len(override_args)``
                positional args (and *all* varargs if ``override_args`` contains
                varargs).
            override_kwargs: Optional keyword override arguments.  These arguments
                replace any additional named arguments not overriden by
                ``override_args``.

        Calling a :class:`DataclassPartial` roughly equals to

        .. code-block:: python

            with extended_context_hooks():  # enters a context defined by extended context hooks
                with context_hooks(): # enters a context defined by context hooks
                    results = self.callable(*args, **kwargs)
                return apply_post_hooks(results)

        Returns:
            The result of calling the target callable with _optional_ override arguments
            under _optional_ contexts and application of _optional_ post hook.
        """
        args, kwargs = self._merge_override_args_with_configured_args(
            *override_args, **override_kwargs
        )
        _logger.debug(
            "Calling %s with args=%s, kwargs=%s", self._CALLABLE, args, kwargs
        )
        return super().__call__(*args, **kwargs)

    def _call_impl(self, *args, **kwargs):
        return self._CALLABLE(*args, **kwargs)  # pylint: disable=not-callable

    def _merge_override_args_with_configured_args(
        self, *override_args, **override_kwargs
    ):
        """
        Converts the :attr:`confiugred_args` dataclass back to *args, **kwargs for
        calling the target callable.  Then updates these *args, **kwargs using values
        from *override_args, **override_kwargs, returning the updated *args, **kwargs.
        """

        args, kwargs = self._convert_dataclass_to_callable_args(self.configured_args)

        # Replace positional arguments (and possibly varargs) with override_args:
        if len(override_args) <= len(self._ARG_SPEC.args):
            args[: len(override_args)] = override_args
        elif self._ARG_SPEC.varargs is not None:
            args = override_args
        else:
            raise TypeError(
                f"Callable takes {len(self._ARG_SPEC.args)} positional arguments "
                f"but {len(override_args)} positional override arguments were given"
            )

        # Replace positional arguments with override_kwargs:
        for idx, name in enumerate(self._ARG_SPEC.args):
            if name not in override_kwargs:
                continue
            if idx < len(override_args):
                # override_args already replaced the arg for name
                raise TypeError(
                    f"Received multiple override values for argument '{name}'"
                )
            args[idx] = override_kwargs.pop(name)

        # Replace keyword-only arguments with override_kwargs:
        kwargs.update(override_kwargs)

        return args, kwargs

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return vars(self) == vars(other)
        return False

    @classmethod
    def _convert_dataclass_to_callable_args(cls, configured_args):
        """
        Given a ``configured_args`` dataclass of type ``cls._ARGS_DATACLASS``, this
        method maps the dataclass back to *args, **kwargs for calling the target
        callable.
        """
        args = [getattr(configured_args, name) for name in cls._ARG_SPEC.args]
        if cls._ARG_SPEC.varargs is not None:
            args.extend(getattr(configured_args, cls._ARG_SPEC.varargs))
        kwargs = {
            name: getattr(configured_args, name) for name in cls._ARG_SPEC.kwonlyargs
        }
        if cls._ARG_SPEC.varkw is not None:
            kwargs.update(getattr(configured_args, cls._ARG_SPEC.varkw))
        return args, kwargs

    def __repr__(self):
        # pylint: disable=duplicate-code
        # (minor duplication of DataclassedCallable.__repr__())

        configured_args = _helpers.dataclass_to_dict(self.configured_args)
        items = list(configured_args.items())
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


class _ConfiguredArgForwarder:
    """
    Helper class for defining properties on a DataclassedPartial that forward argument
    names to the ``configured_args`` dataclass.
    """

    def __init__(self, arg_name: str):
        self.arg_name = arg_name

    def get(self, partial: DataclassedPartial) -> _Any:
        return getattr(partial.configured_args, self.arg_name)

    def set(self, partial: DataclassedPartial, value: _Any):
        return setattr(partial.configured_args, self.arg_name, value)


_compat.register_backward_compatibility_import(
    __name__, "PartialPostHooks", "tamm.utils.callable.PostHooks"
)

_compat.register_backward_compatibility_import(
    __name__, "PartialContextHooks", "tamm.utils.callable.ContextHooks"
)

_compat.register_backward_compatibility_import(
    __name__, "PartialHookHandle", "tamm.utils.callable.HookHandle"
)
