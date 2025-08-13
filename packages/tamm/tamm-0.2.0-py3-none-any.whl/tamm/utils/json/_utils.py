"""
This module provides helpers for extending the :mod:`json` module for |tamm|.  Please
see the unit tests for usage examples.
"""

import abc
import logging
from collections import defaultdict
from typing import Any, Callable, ClassVar, Dict
from typing import List as _List
from typing import Mapping, Protocol, Union

import torch

from tamm._plugin.utils import import_named_plugin
from tamm.runtime_configuration import rc as _rc
from tamm.utils import registry as _registry
from tamm.utils.json._hooks import (
    PackageRequirementsHook,
    ReadabilityHook,
    UnusedAttributeHook,
)

logger = logging.getLogger(__name__)

JSONRegistries: Mapping[str, _registry.Registry] = defaultdict(_registry.Registry)


def global_default(obj):
    try:
        # pylint: disable=protected-access
        return obj._to_json_dict()
    except AttributeError as exc:
        raise TypeError from exc


def global_object_hook(obj: dict):
    if not isinstance(obj, dict):
        return obj
    tamm_type_info = obj.get("__tamm_type__", None)
    if not tamm_type_info:
        return obj
    namespace, tamm_type = tamm_type_info.rsplit(":", maxsplit=1)

    if namespace not in JSONRegistries:
        plugin_required = namespace.split(":", maxsplit=1)[0]
        if plugin_required != _rc.PROJECT_SLUG:
            import_named_plugin(plugin_required)

    registry = JSONRegistries[namespace]
    cls = registry.get_factory_fn(tamm_type)
    # pylint: disable=protected-access
    try:
        return cls._from_json_dict(**obj)
    except TypeError as e:
        module_name = tamm_type_info.split(":", maxsplit=1)[0]
        raise TypeError(
            f"Error encountered while deserializing a '{tamm_type_info}': {e}. "
            "Either (1) the object's JSON representation changed in an "
            "unrecognizable way, (2) the deserialization requires a newer "
            f"version of the {module_name} module, or (3) something unexpected "
            "went wrong."
        ) from e


def _resolve_json_namespace(
    bases, explicit_namespace=None, default_namespace="default"
) -> str:
    """
    Helper method to resolve json namespace from multiple inheritance
    Args:
        bases: Base classes which may or may not have _JSON_NAMESPACE attribute
        explicit_namespace: Explicit namespace provided by class Signature
        default_namespace: Default namespace

    Returns: Resolved JSON namespace or default namespace

    """
    if explicit_namespace is not None:
        return explicit_namespace
    resolved_namespace = None
    for base in bases:
        try:
            # pylint: disable=protected-access
            if base._JSON_NAMESPACE not in {
                None,
                default_namespace,
            }:
                resolved_namespace = base._JSON_NAMESPACE
        except AttributeError:
            pass
    if resolved_namespace is None:
        return default_namespace
    return resolved_namespace


def _get_module_prefix(class_name: str):
    """Helper function to return the prefix for a base class."""
    return class_name.split(".", maxsplit=1)[0]


def _retrieve_prefixed_namespace(
    module_prefix: str, resolved_namespace: str, delimiter=":"
):
    """
    Helper function to return the prefixed full namespace.
    Format is of type module_prefix:entity.

    Example:

    .. code-block:: python

        namespace = _retrieve_prefixed_namespace(
            module_prefix="tamm",
            resolved_namespace="models"
        )
        print(namespace)
        "tamm:models"
    """
    return module_prefix + delimiter + resolved_namespace.split(delimiter)[-1]


class JSONSerializableMeta(type):
    def __new__(mcs, clsname, bases, attrs, /, json_namespace=None, **kwargs):
        newclass = super(JSONSerializableMeta, mcs).__new__(
            mcs, clsname, bases, attrs, **kwargs
        )

        module_prefix = _get_module_prefix(attrs["__module__"])

        resolved_namespace = _resolve_json_namespace(bases, json_namespace)

        # pylint:disable=invalid-name
        newclass._JSON_NAMESPACE = _retrieve_prefixed_namespace(
            module_prefix, resolved_namespace
        )

        # pylint:enable=invalid-name
        JSONRegistries[newclass._JSON_NAMESPACE].register(newclass, clsname)
        JSONRegistries[newclass._JSON_NAMESPACE]._name = newclass._JSON_NAMESPACE
        return newclass


class JSONSerializableABCMeta(abc.ABCMeta, JSONSerializableMeta):
    # pylint: disable=line-too-long
    """
    Helper `metaclass <https://docs.python.org/3/reference/datamodel.html#metaclasses>`_
    for classes who inherit from both ``abc.ABC`` and
    ``JSONSerializableMixin``.

    For example,

    .. code-block:: python

        class MyClass(abc.ABC, JSONSerializableMixin): # WRONG, will raise TypeError

    the class signature *has* to be

    .. code-block:: python

        class MyClass(abc.ABC, JSONSerializableMixin, metaclass=JSONSerializableABCMeta):

    instead to avoid

        TypeError: metaclass conflict: the metaclass of a derived class must
        be a (non-strict) subclass of the metaclasses of all its bases

    Reference:
    `StackOverflow <https://stackoverflow.com/questions/11276037/resolving-metaclass-conflicts>`_
    """
    # pylint: enable=line-too-long


class JSONSerializableMixin(metaclass=JSONSerializableMeta):
    """
    A mixin to make ``tamm`` objects JSON serializable.
    """

    _JSON_NAMESPACE: ClassVar[str]

    def _package_requirements(self) -> _List[str]:
        """
        Children can provide a package requirements constraint to determine

        Returns:
            a ``list`` of package requirements in
            `PEP508 <https://peps.python.org/pep-0508/>`_
        """
        return []

    @classmethod
    def _from_json_dict_impl(cls, **raw_dict: dict):
        """
        Children overridable classmethod to instantiate an object of this class from
        raw JSON dictionary. Default unpack all attributes to class __init__()

        Args:
            **raw_dict: dictionary representation with all children nodes deserialized

        Returns:
            Deserialized object of this class, *i.e.,* ``cls(**raw_dict)``

        """
        return cls(**raw_dict)

    def _to_json_dict_impl(self) -> dict:
        """
        Children overridable instance method to generate a dictionary representation of
        object.

        .. note::

            Default implementation force cast the object to dict.
            i.e., assumes ``self`` conforms to
            `mapping protocol <https://docs.python.org/3/c-api/mapping.html>`_.

        Returns:
            (:obj:`dict`) JSON dictionary representation of this object

        """
        return dict(self)  # type: ignore[call-overload]

    @classmethod
    def _from_json_dict(cls, **raw_dict: dict):
        for hook in [PackageRequirementsHook(), UnusedAttributeHook()]:
            raw_dict = hook(raw_dict)

        return cls._from_json_dict_impl(**raw_dict)

    def _to_json_dict(self) -> dict:
        raw_dict = self._to_json_dict_impl()
        raw_dict["__tamm_type__"] = f"{self._JSON_NAMESPACE}:{self.__class__.__name__}"
        if self._package_requirements():
            raw_dict["__package_requirements__"] = self._package_requirements()
        for hook in [ReadabilityHook()]:
            raw_dict = hook(raw_dict)
        return raw_dict


class JSONSerializableABCMixin(
    abc.ABC, JSONSerializableMixin, metaclass=JSONSerializableABCMeta
):
    """
    A mixin to make ``tamm`` objects both JSON serializable and an :class:`abc.ABC`.
    Inheriting from this class avoids the :obj:`TypeError` that occurs when inheriting
    from both :class:`ABC` and :class:`JSONSerializableMixin` without specifying the
    :class:`JSONSerializableABCMeta` metaclass.
    """


class JSONHook(Protocol):
    """
    This class defines a Protocol for serializing/desrializing custom types with JSON.
    """

    @abc.abstractmethod
    def default(self, obj: Any) -> Any:
        """
        This method may be called by :func:`json.dumps` for any ``obj`` that is not
        JSON-serializable.  The method should return a JSON-serializable :obj:`dict`
        representing ``obj`` or raise a ``TypeError`` if it is unable to do so.  See
        :func:`json.dumps` for more info.
        """

    @classmethod
    @abc.abstractmethod
    def object_hook(cls, obj: Dict[str, Any]) -> Any:
        """
        This method is called by :func:`json.loads` as an object hook, where ``obj`` is
        the result of any object literal decode.  This method should either (1) perform
        the inverse of :meth:`to_json_serializable` and return a new object represented
        by ``obj``, or (2) return ``obj`` unmodified if it is unrecognized.  See
        :func:`json.loads` for more info.
        """


class DeviceJSONHook(JSONHook):
    """
    This class implements a JSON hook for serializing :class:`torch.device` objects.
    """

    def default(self, obj: Any) -> Any:
        if not isinstance(obj, torch.device):
            raise TypeError(f"cannot serialize {obj} which is not a torch.device")
        return {"__tamm_type__": "torch.device", "type": obj.type, "index": obj.index}

    @classmethod
    def object_hook(cls, obj: Dict[str, Any]) -> Union[torch.device, Dict[str, Any]]:
        if not isinstance(obj, dict):
            return obj
        if obj.get("__tamm_type__") == "torch.device":
            index = obj.get("index", None)
            if index is not None:
                return torch.device(f"{obj['type']}:{index}")
            return torch.device(f"{obj['type']}")
        return obj


class DTypeJSONHook(JSONHook):
    """
    This class implements a JSON hook for serializing :class:`torch.dtype` objects.
    """

    def default(self, obj: Any) -> Any:
        if not isinstance(obj, torch.dtype):
            raise TypeError(f"cannot serialize {obj} which is not a torch.dtype")
        name = str(obj).rsplit(".", maxsplit=1)[-1]
        return {"__tamm_type__": "torch.dtype", "name": name}

    @classmethod
    def object_hook(cls, obj: Dict[str, Any]) -> Union[torch.dtype, Dict[str, Any]]:
        if not isinstance(obj, dict):
            return obj
        if obj.get("__tamm_type__") == "torch.dtype":
            return getattr(torch, obj["name"])
        return obj


class CompositeObjectHooks:
    """
    This class combines multiple ``object_hooks`` arguments for :func:`json.loads`.

    Args:
        *callables (:obj:`callable`):  An arbitrary number of
            callable ``object_hooks`` functions for
            :func:`json.loads`.
    """

    def __init__(
        self,
        *callables: Callable[..., Any],
    ):
        self.callables = callables

    def __call__(self, obj: Any) -> Any:
        """
        Calls all default functions in sequence, returning the result of the first
        call that does not raise a ``TypeError``.  Raises a ``TypeError`` if every
        default raises a ``TypeError``.
        """
        for _callable in self.callables:
            obj = _callable(obj)
        return obj


class CompositeDefault:
    """
    This class combines multiple ``default`` arguments for :func:`json.dumps`.

    Args:
        *callables (:obj:`JSONHook` or :obj:`callable`):  An arbitrary number of
            :obj:`JSONHook` instances or callable ``default`` functions for
            :func:`json.dumps`.
    """

    def __init__(
        self,
        *callables: Callable[..., Any],
    ):
        self.callables = callables

    # pylint: disable-next=inconsistent-return-statements
    def __call__(self, obj: Any) -> Any:
        """
        Calls all default functions in sequence, returning the result of the first
        call that does not raise a ``TypeError``.  Raises a ``TypeError`` if every
        default raises a ``TypeError``.
        """

        for _callable in self.callables:
            try:
                return _callable(obj)
            except TypeError as e:
                logger.debug(
                    "'%s' cannot serialize '%s' due to: '%s'",
                    _callable.__name__,
                    obj.__class__.__name__,
                    e,
                )
        _callables_qualname = ", ".join(
            f"{_callable.__qualname__}()" for _callable in self.callables
        )
        raise TypeError(
            f"Object of type '{type(obj).__name__}' is not "
            f"JSON serializable by CompositeDefaults with callables"
            f" ({_callables_qualname})"
        )
