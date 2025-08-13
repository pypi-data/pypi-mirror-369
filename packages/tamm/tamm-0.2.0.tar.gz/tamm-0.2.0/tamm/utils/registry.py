"""
Provides a registry class for organizing a library of factory functions.
"""

import collections as _collections
import dataclasses as _dataclasses
import typing as _typing
import warnings as _warnings
from typing import Any as _Any
from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

from tamm import _helpers

RegistrySpec = _collections.namedtuple(
    "RegistrySpec", ["key", "args", "kwargs"], defaults=["default", (), {}]
)


@_dataclasses.dataclass
class RegistryEntry:
    """Data for each entry in the registry"""

    factory_fn: _Callable
    description: str
    is_deprecated: bool = False


class Registry:
    """
    Organizes a library of factory functions, providing a one-stop spot to create
    instances of objects from the library and to discover members of the library.

    Args:
        name (:obj:`str`): A name for the registry.
    """

    def __init__(self, name: str = ""):
        self._name = name
        self._entries: _Dict[str, _Tuple[_Callable, str]] = {}

    @property
    def name(self) -> str:
        """The registry's name."""
        return self._name

    def register(
        self,
        factory_fn: _Optional[_Callable] = None,
        key: str = "default",
        description: _Optional[str] = None,
        is_deprecated: bool = False,
    ) -> None:
        """
        Adds an entry to the registry.

        Args:
            factory_fn (a :obj:`Callable` or `None`): If a :obj:`Callable`, the method
                saves this function to the registry.  If `None`, the method returns
                a decorator that saves the wrapped :obj:`Callable` to the registry.
            key (:obj:`str`): A key for accessing the `factory_fn` in the registry.
                Logs a warning if an entry already has this key.
            description (:obj:`str`): A text description of the entry.
            is_deprecated (:obj:`bool`): Flag for deprecating the entry.  Defaults to
                ``False``.

        Returns:
            `None` except when `factory_fn` is `None`, in which case the method returns
            a decorator.

        Examples:

            Basic usage:

                .. code-block:: python

                    class VisionTransformer:
                        def __init__(self, num_layers: int = 48):
                            ...

                    registry.register(
                        factory_fn=VisionTransformer,
                        key="vit",
                        description="VisionTransformer model."
                    )

            Decorator usage:

                .. code-block:: python

                    @registry.register(key="vit", description="Vision transformer model.")
                    def vit_factory(num_layers: int = 48) -> VisionTransformer:
                        return VisionTransformer(num_layers=num_layers)

        """
        if factory_fn is None:
            return self._get_decorator_for_register(
                key=key, description=description, is_deprecated=is_deprecated
            )

        self._validate_name_string(calling_function_name=str(factory_fn), name=key)
        if key in self._entries:
            _warnings.warn(
                f"Overwriting existing entry for key {key} in registry {self.name}"
            )
        if not callable(factory_fn):
            raise ValueError(
                f"Registry {self.name} received a non-callable factory function for "
                f"key '{key}'"
            )

        if description is None:
            description = _helpers.get_cleaned_docstring(factory_fn)
        else:
            description = _helpers.clean_docstring(description)

        self._entries[key] = RegistryEntry(
            factory_fn=factory_fn, description=description, is_deprecated=is_deprecated
        )
        return None

    def _get_decorator_for_register(
        self, *, key: str, description: str, is_deprecated: bool
    ) -> _Callable:
        """
        Returns a decorator that takes a factory_fn as input, adds the factory_fn to
        the registry, and the returns the unmodified factory_fn.
        """

        def decorator(factory_fn):
            self.register(
                factory_fn,
                key=key,
                description=description,
                is_deprecated=is_deprecated,
            )
            return factory_fn

        return decorator

    @staticmethod
    def _validate_name_string(
        calling_function_name: str, name: _Optional[str] = None
    ) -> None:
        """
        Validates that the provided name is of type string.

        Args:
            calling_function_name (str): Name of the function from where this
            method is being called. This is used to generate the error message.
            name (Optional[str]): Name to validate.

        Raises ValueError: If `name` is not of type str.
        """
        if not isinstance(name, str):
            raise ValueError(
                f"{calling_function_name} expects a str for the name argument "
                f"but received a {type(name)} instead."
            )

    @_typing.overload
    def get_factory_fn(self, key: _Union[list, tuple]) -> _Callable:
        ...

    def get_factory_fn(self, key: str) -> _Callable:
        """
        Retrieves a factory function from the registry.

        Args:
            key (:obj:`str` or obj:`tuple`): The key specified when adding the entry to
            the registry.  If a :obj:`tuple`, the first element must be the ``key`` as
            a :obj:`str` and optional second and/or third elements may be an ``arg``
            tuple and/or ``kwarg`` dictionary for the factory function.

        Returns:
            The factory function associated with `key`.
        """
        key, *_ = self._unpack_key(key)
        if key not in self._entries:
            raise KeyError(
                f"Registry {self.name} has no entry with key {key} "
                f"(existing keys: {sorted([*self._entries])})"
            )
        return self._entries[key].factory_fn

    def _unpack_key(self, key: _Union[str, list, tuple]) -> tuple:
        if not isinstance(key, (tuple, list)):
            return key, (), {}
        if len(key) not in (1, 2, 3):
            raise ValueError(
                f"Registry {self.name} received a tuple input of length {len(key)}, "
                "but tuple keys must have length 1, 2, or 3."
            )
        new_key = key[0]
        args = key[1] if len(key) > 1 else ()
        if isinstance(args, _collections.abc.Mapping):
            kwargs, args = args, ()
        else:
            kwargs = key[2] if len(key) > 2 else {}
        return new_key, args, kwargs

    @_typing.overload
    def create(self, key: _Union[list, tuple]) -> _Any:
        ...

    def create(self, key: str, *args: _Any, **kwargs: _Any) -> _Any:
        """
        Returns a new object created with the factory function associated with `key`.

        Args:
            key (:obj:`str` or :obj:`tuple`): The key (a :obj:`str`) corresponding to
                the registered factory function for creating the return object.
                Alternatively, this can also be a :obj:`tuple`---in this case, the first
                element must be the ``key`` as a :obj:`str` and optional second and/or
                third elements may be a packed ``arg`` tuple and/or ``kwarg`` dictionary
                for the factory function.
            *args, **kwargs: Positional and keyword arguments for the factory function
                associated with `key`.

        Returns:
            The result of `factory_fn(*args, **kwargs)`, where `factory_fn` is the
            factory function associated with `key`.
        """
        key, args_from_key, kwargs_from_key = self._unpack_key(key)
        if not args:
            args = args_from_key
        kwargs = {**kwargs_from_key, **kwargs}
        factory_fn = self.get_factory_fn(key)
        return factory_fn(*args, **kwargs)  # pylint: disable=not-callable

    def is_valid_key(self, obj: _Any) -> bool:
        """
        Returns ``True`` if ``obj`` corresponds to an entry in the registry when passed
        as a ``key`` argument to :meth:`.create`.  Returns ``False`` otherwise.
        """
        try:
            key, *_ = self._unpack_key(obj)
            return key in self._entries
        except Exception:
            return False

    def get_entries(self) -> _Dict[str, RegistryEntry]:
        """
        Returns entries of the registry as a dictionary that maps each key to a
        corresponding :obj:`RegistryEntry`.
        """
        return self._entries.copy()

    def list(
        self,
        include_descriptions: bool = False,
        filter_deprecated: bool = False,
    ) -> _Union[_List[str], _Dict[str, str]]:
        """
        List the keys in the registry.

        Args:
            include_descriptions (bool): Whether to include descriptions for each key.

        Returns:
            List of keys if `include_descriptions` is False.
            Dictionary of keys and their descriptions if `include_descriptions` is True.
        """
        entries = self.get_entries()
        if filter_deprecated:
            entries = {k: v for k, v in entries.items() if not v.is_deprecated}
        keys_and_entries = sorted(entries.items())
        if not include_descriptions:
            return [key for key, _ in keys_and_entries]
        return {key: entry.description for key, entry in keys_and_entries}

    def print(
        self,
        *,
        include_descriptions: bool = False,
        filter_deprecated: bool = False,
        wide: bool = False,
    ):
        """
        Print the keys and descriptions in the registry.

        Args:
            include_descriptions: Whether to include descriptions for each key.
            filter_deprecated: Whether to remove deprecated entries.
            wide: Flag to disable output truncation.
        """
        entries = self.list(
            include_descriptions=include_descriptions,
            filter_deprecated=filter_deprecated,
        )
        if include_descriptions:
            max_len_names = max(len(name) for name in entries)
            paddings = (" " * (max_len_names + 4 - len(name)) for name in entries)
            lines = [
                name + padding + descr
                for padding, (name, descr) in zip(paddings, entries.items())
            ]
        else:
            lines = entries
        if not wide:
            lines = _helpers.truncate_lines_for_terminal(*lines)
        print("\n".join(lines))
