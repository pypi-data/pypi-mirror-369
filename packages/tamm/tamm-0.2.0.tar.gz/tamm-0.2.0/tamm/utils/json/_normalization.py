import abc
import enum
import json
import logging as _logging
import re
from typing import Any, Dict, Protocol, Union

from tamm import _helpers
from tamm.runtime_configuration import rc as _rc

_logger = _logging.getLogger(__name__)

_USER_DEFINED_NORMALIZERS = []


class SupportsObjectHook(Protocol):
    """
    A protocol for objects that apply normalization before
    :func:`tamm.utils.json.loads` or denormalization after
    :func:`tamm.utils.json.dumps`.
    """

    @abc.abstractmethod
    def object_hook(self, json_obj: Any) -> Any:
        """
        A hook for modifying a JSON-compatible object (a collection of
        ``dict``, ``list``, ``str``, ``int``, ``float``, ``bool``, and
        ``None``).

        Args:
            json_obj: A JSON-compatible object.

        Returns:
            A possibly modified version of the input ``json_obj`` that
            is still JSON-compatible.
        """


def register_load_normalizer(normalizer: SupportsObjectHook) -> None:
    """
    A function that modifies :func:`tamm.utils.json.loads` by registering a
    normalizer.  The ``loads()`` function will map every JSON object with the
    normalizer's ``object_hook()`` method prior to |tamm| deserialization.

    Args:
        normalizer (:obj:`SupportsObjectHook`): The normalizer to register.
    """
    _USER_DEFINED_NORMALIZERS.append(normalizer)


class BackwardCompatibilityTypeNormalizerMode(str, enum.Enum):
    """
    An :obj:`Enum` for controlling the behavior of
    :class:`BackwardCompatibilityTypeNormalizer` objects.
    """

    FULLMATCH = "FULLMATCH"
    """
    Only update types that fully match a key in ``old_to_new_types``. This mode
    is recommended whenever possible because it is efficient.
    """

    STARTSWITH = "STARTSWITH"
    """Update any types that starts with a key in ``old_to_new_types``."""


class BackwardCompatibilityTypeNormalizer(SupportsObjectHook):
    """
    A normalizer for supporting backward compatibility of loading |tamm|
    types that have been renamed or relocated.  The normalizer updates
    ``__tamm_type__`` based on string matching.

    Args:
        old_to_new_types (:obj:`dict`): A :obj:`dict` that maps old
            ``__tamm_type__`` prefixes to new ones.  The
            :meth:`.object_hook` method applies string substitution
            to ``json_obj["__tamm_type__"]`` if this string exists and
            matches with a key in ``old_to_new_types``.  The substitution
            process executes in the order of the ``old_to_new_types``
            entries, and it may result in multiple substitutions.
        mode (:obj:`BackwardCompatibilityTypeNormalizerMode` or :obj:`str`): A
            mode that controls the string replacement behavior.  If a
            :obj:`str`, the argument should match a member name from the enum
            (case-insensitive).  Defaults to ``"fullmatch"``.

    """

    def __init__(
        self,
        old_to_new_types: Dict[str, str],
        *,
        mode: Union[BackwardCompatibilityTypeNormalizerMode, str] = "fullmatch",
    ):
        self._old_to_new_types = old_to_new_types
        self.mode = _helpers.get_enum_member_from_name(
            BackwardCompatibilityTypeNormalizerMode, mode
        )

    def object_hook(self, json_obj: Any) -> Any:
        if not isinstance(json_obj, dict) or "__tamm_type__" not in json_obj:
            return json_obj

        tamm_type = json_obj["__tamm_type__"]

        if not isinstance(tamm_type, str):
            _logger.debug("json_obj contains a non-str __tamm_type__: %s", json_obj)
            return json_obj

        if self.mode is BackwardCompatibilityTypeNormalizerMode.FULLMATCH:
            self._update_obj_fullmatch(json_obj, tamm_type=tamm_type)
        elif self.mode is BackwardCompatibilityTypeNormalizerMode.STARTSWITH:
            self._update_obj_startswith(json_obj, tamm_type=tamm_type)

        return json_obj

    def _update_obj_fullmatch(self, json_obj, *, tamm_type):
        while True:
            new_type = self._old_to_new_types.get(tamm_type, None)
            if new_type is None:
                return
            if new_type == tamm_type:
                return
            json_obj["__tamm_type__"] = new_type
            _logger.debug(
                "Migrated %s type to %s for deserializing JSON obj: %s",
                tamm_type,
                new_type,
                json_obj,
            )
            tamm_type = new_type

    def _update_obj_startswith(self, json_obj, *, tamm_type):
        for old_type, new_type in self._old_to_new_types.items():
            if tamm_type.startswith(old_type):
                tamm_type = tamm_type.replace(old_type, new_type, 1)
                json_obj["__tamm_type__"] = tamm_type
                _logger.debug(
                    "Migrated %s type to %s for deserializing JSON obj: %s",
                    old_type,
                    new_type,
                    json_obj,
                )


class TorchDtypeNormalizer(SupportsObjectHook):
    """
    Our serialization scheme for dtypes is robust, but it is unnatural for
    users editing dtype fields "by hand".  The natural thing is to add
    "dtype": "bfloat16", but so far our scheme above requires
    "dtype": {"__tamm_type__": "torch.dtype", "name": "bfloat16"}.
    This is a best-effort attempt to also support the natural way.
    """

    def object_hook(self, json_obj: Any) -> Any:
        """
        Scans through obj.items().  If the key ends with "dtype" and the value is a
        string dtype (such as "torch.float16" or "float16"), then we convert the value
        to the corresponding :obj:`torch.dtype`.

        Args:
            json_obj: Input JSON object.

        Returns: normalized obj if obj is recognized by normalizer

        """
        if not isinstance(json_obj, dict):
            return json_obj
        for key, val in json_obj.items():
            if not isinstance(key, str):
                continue
            if not isinstance(val, str):
                continue
            if not (key.startswith("dtype") or key.endswith("dtype")):
                continue
            json_obj[key] = {
                "__tamm_type__": "torch.dtype",
                "name": val[6:] if val.startswith("torch.") else val,
            }
        return json_obj


class CompositeJSON2JSONConverter:
    def __init__(self, *object_hooks: "SupportsObjectHook"):
        """
        Each ``object_hook`` processes a JSON object into another schema
        also in JSON. ``object_hook`` is responsible for filtering and transforming
        JSON objects.

        For example, the following object hook converts
        all string values in JSON to UPPER case:

        .. code-block:: python

        class UppercaseNormalizer(SupportsObjectHook):
            def object_hook(self, json_obj: dict):
                 if not isinstance(json_obj, str):
                    return json_obj
                 return json_obj.upper()

        Args:
            *object_hooks: instance of class that provides object_hook()
        """
        self._object_hooks = object_hooks

    def __call__(
        self,
        json_str: str,
        *,
        skipkeys=False,
        ensure_ascii=True,
        check_circular=True,
        allow_nan=True,
        cls=None,
        indent=None,
        separators=None,
        default=None,
        sort_keys=False,
        **kw,
    ) -> str:
        """
        Implements string-based JSON-JSON conversion by exploiting the
        ``object_hook`` mechanism provided by Python json standard library.
        A json string is loaded with object hooks applied in sequence and dumped again
        for subsequent uses.
        """
        for n in self._object_hooks:
            json_str = json.dumps(
                json.loads(json_str, object_hook=n.object_hook),
                skipkeys=skipkeys,
                ensure_ascii=ensure_ascii,
                check_circular=check_circular,
                allow_nan=allow_nan,
                cls=cls,
                indent=indent,
                default=default,
                separators=separators,
                sort_keys=sort_keys,
                **kw,
            )
        return json_str


class ModulePrefixNormalizer(SupportsObjectHook):
    @classmethod
    def _get_prefixed_namespace(cls, namespace: str, delimiter=":"):
        return _rc.PROJECT_SLUG + delimiter + namespace

    def object_hook(self, json_obj: Any) -> Any:
        """
        Prepends the |tamm| module prefix to ``__tamm_type__`` object key for tamm-based
        serializable objects if not already prefixed to ensure backward compatibility
        with current |tamm| JSON registry schema notation
        ``tamm:<json_namespace>`:<registry_class>``.

        Args:
            json_obj: Input JSON object.

        Returns:
            Output dictionary with ``__tamm_type__`` values maybe prefixed with ``tamm``
                module prefix.
        """
        # pylint: disable=duplicate-code
        if not isinstance(json_obj, dict):
            return json_obj
        tamm_type_info = json_obj.get("__tamm_type__", None)
        if not tamm_type_info:
            return json_obj

        _delimiter = ":"

        if _delimiter not in tamm_type_info:
            # skip __tamm_type__ which does not contain colon (:),
            # e.g. {'__tamm_type__': 'torch.dtype', 'name': 'float16'}
            return json_obj

        # __tamm_type__ is typically of the format:
        # <module_prefix>:<json_namespace>:<serializable_registry_class>
        _, _, *args = tamm_type_info.split(_delimiter)

        if not args:
            json_obj["__tamm_type__"] = ModulePrefixNormalizer._get_prefixed_namespace(
                namespace=json_obj["__tamm_type__"], delimiter=_delimiter
            )
        return json_obj


class ModulePrefixDeNormalizer(SupportsObjectHook):
    def object_hook(self, json_obj: Any) -> Any:
        """
        Strip off tamm: prefix for backward compatibility
        """
        if not isinstance(json_obj, dict):
            return json_obj
        tamm_type_info = json_obj.get("__tamm_type__", None)
        if not tamm_type_info:
            return json_obj
        tamm_type_info = str(tamm_type_info)
        if tamm_type_info.startswith(f"{_rc.PROJECT_SLUG}:"):
            json_obj["__tamm_type__"] = tamm_type_info[len(f"{_rc.PROJECT_SLUG}:") :]
        return json_obj


class BackwardCompatibilityNamespaceNormalizer(SupportsObjectHook):
    def __init__(self):
        self._config_re_pattern = re.compile(":(layers|models)(?=:[^:]*Config$)")

    def object_hook(self, json_obj: Any) -> Any:
        if not isinstance(json_obj, dict) or "__tamm_type__" not in json_obj:
            return json_obj

        tamm_type = json_obj["__tamm_type__"]

        if not isinstance(tamm_type, str):
            return json_obj

        new_type = self._config_re_pattern.sub(":module_configs", tamm_type)

        if new_type != tamm_type:
            json_obj["__tamm_type__"] = new_type
            _logger.debug(
                "Migrated %s type to %s for deserializing JSON obj: %s",
                tamm_type,
                new_type,
                json_obj,
            )

        return json_obj


def get_normalizer():
    """
    Get the JSON-JSON converter which can be applied before de-serialization.
    Typical purpose of this normalization is to convert known legacy JSON schema
    generated by previous tamm releases to something compatible with this version.
    """

    normalizers = [
        ModulePrefixNormalizer(),
        BackwardCompatibilityTypeNormalizer(
            {"tamm:models:ModelMetadata": "tamm:module_metadata:ModuleMetadata"},
        ),
        BackwardCompatibilityNamespaceNormalizer(),
        TorchDtypeNormalizer(),
    ]
    return CompositeJSON2JSONConverter(*normalizers, *_USER_DEFINED_NORMALIZERS)


def get_denormalizer():
    """
    Get the JSON-JSON converter which can be applied after serialization. Typical
    purpose of this denormalization is to remove incompatible JSON schema for backward
    compatibility with older tamm releases.
    """
    return CompositeJSON2JSONConverter(ModulePrefixDeNormalizer())
