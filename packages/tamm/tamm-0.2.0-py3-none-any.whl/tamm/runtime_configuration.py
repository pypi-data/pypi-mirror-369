"""
tamm.runtime_configuration
--------------------------

.. data:: tamm.rc

    The global :obj:`.RuntimeConfiguration` instance.

.. autoclass:: tamm.runtime_configuration.RuntimeConfiguration
    :members:

.. autoclass:: tamm.runtime_configuration.PluginExtrasEntrypointNames
    :members:
"""

import dataclasses as _dataclasses
import functools as _functools
import os as _os
import pathlib as _pathlib
from typing import Any as _Any
from typing import Callable as _Callable
from typing import List as _List
from typing import Optional as _Optional


def _to_str(value: _Any) -> str:
    """Small helper for formatting values in docstrings."""
    if isinstance(value, str):
        value = f'"{value}"'
    return f"``{value}``"


class RCConstant:
    """
    A helper class for creating constant properties in :class:`.RuntimeConfiguration`.
    The class is expected to be used through the :method:`create_property` class method.

    Args:
        value: The constant value of the property.
        doc: A description for the property's docstring.
    """

    def __init__(self, *, value: _Any, doc: str):
        self.value = value
        if not doc.endswith("."):
            doc = doc + "."
        self.doc = doc

    @classmethod
    def create_property(cls, *, value: _Any, doc: str) -> property:
        obj = cls(value=value, doc=doc)
        return property(fget=obj.create_getter(), doc=obj.create_doc())

    def create_getter(self):
        def getter(_):
            return self.value

        return getter

    def create_doc(self):
        return f"{self.doc} This is a constant with value {_to_str(self.value)}."


class RCVariable:
    """
    A helper class for creating variable properties in :class:`.RuntimeConfiguration`.
    These are configuration options that can modified, either through environment variable
    or by setting them on the :obj:`.RuntimeConfiguration` instance. The class is expected
    to be used through the :method:`create_property` class method.

    Args:
        name: The name of the property.
        default: The property's default value.
        doc: A description for the property's docstring.
        parse_hook (:obj:`callable`, optional): An optional function for parsing the
            variable's value when it is specified as an environment variable.
        choices (:obj:`list`, optional): An optional list of possible values for the
            variable.  If specified, the property raises a :obj:`ValueError` if the
            user sets it to a value not included in the list.
        runtime_changeable (:obj:`bool`, optional): A flag that controls whether the
            variable can be modified after creation.  If ``False``, the variable can
            only be specified via environment variable.
    """

    def __init__(
        self,
        *,
        name: str,
        default: _Any,
        doc: str,
        parse_hook: _Optional[_Callable[[_Any], _Any]] = None,
        choices: _Optional[_List[_Any]] = None,
        runtime_changeable: bool = True,
    ):
        self.name = name
        self.default = default
        if not doc.endswith("."):
            doc = doc + "."
        self.doc = doc
        self.parse_hook = parse_hook
        self.choices = choices
        self.is_runtime_changeable = runtime_changeable

    @classmethod
    def create_property(
        cls,
        *,
        name: str,
        default: _Any,
        doc: str,
        parse_hook: _Optional[_Callable[[_Any], _Any]] = None,
        choices: _Optional[_List[_Any]] = None,
        runtime_changeable: bool = True,
    ):
        obj = cls(
            name=name,
            default=default,
            doc=doc,
            parse_hook=parse_hook,
            choices=choices,
            runtime_changeable=runtime_changeable,
        )
        return property(
            fget=obj.create_getter(),
            fset=obj.create_setter(),
            fdel=obj.create_deleter(),
            doc=obj.create_doc(),
        )

    @property
    def env_var_name(self):
        return f"TAMM_{self.name}".upper()

    @property
    def attr_name(self):
        return f"_{self.name}"

    @property
    def updated_default(self):
        if self.env_var_name not in _os.environ:
            return self.default
        result = _os.environ[self.env_var_name]
        if self.parse_hook is not None:
            return self.parse_hook(result)
        return result

    def _validate_choice(self, value):
        if self.choices is None:
            return
        if value not in self.choices:
            raise ValueError(f"Value '{value}' is not a choice from {self.choices}")

    def create_getter(self):
        def getter(self2):
            if not hasattr(self2, self.attr_name):
                value = self.updated_default
                self._validate_choice(value)
                if not self.is_runtime_changeable:
                    setattr(
                        self2,
                        self.attr_name,
                        value
                        # recording the value of updated_default ensures the
                        # value does not change if the env is later modified
                    )
                return value
            return getattr(self2, self.attr_name)

        return getter

    def create_setter(self):
        def setter(self2, new_value):
            if not self.is_runtime_changeable:
                raise NotRuntimeChangeableException(
                    name=self.name, env_var_name=self.env_var_name
                )
            self._validate_choice(new_value)
            setattr(self2, self.attr_name, new_value)
            self.setter_post_hook(new_value)

        return setter

    def create_deleter(self):
        def deleter(self2):
            if hasattr(self2, self.attr_name):
                delattr(self2, self.attr_name)
            self.setter_post_hook(self.updated_default)

        return deleter

    def setter_post_hook(self, value: _Any) -> None:
        """
        A hook that runs whenever the property's value changes.  Subclasses
        can override this method to introduce callback behavior.
        """

    def create_doc(self):
        full_doc = [self.doc]
        if self.is_runtime_changeable:
            full_doc.append(
                f"Configure using :attr:`tammm.rc` or the ``{self.env_var_name}`` env var."
            )
        else:
            full_doc.append(
                f"Only configurable using the ``{self.env_var_name}`` env var."
            )

        if self.choices is not None:
            choices = [_to_str(c) for c in self.choices]
            if len(choices) == 1:
                choices_str = f"{choices[0]} only"
            elif len(choices) == 2:
                choices_str = f"{choices[0]} and {choices[1]}"
            else:
                choices_strings = [f"{c}" for c in choices]
                choices_strings[-1] = f"and {choices_strings[-1]}"
                choices_str = ", ".join(choices_strings)
            full_doc.append(f"Choices are {choices_str}.")

        full_doc.append(f"Defaults to {_to_str(self.default)}.")
        return " ".join(full_doc)


class LogLevelRCVariable(RCVariable):
    def setter_post_hook(self, value: _Any) -> None:
        # pylint: disable-next=import-outside-toplevel,cyclic-import
        from tamm import _logger

        logger = _logger.get_logger()
        logger.setLevel(value)


class LogFormatRCVariable(RCVariable):
    def setter_post_hook(self, value: _Any) -> None:
        # pylint: disable-next=import-outside-toplevel,cyclic-import
        from tamm import _logger

        logger = _logger.get_logger()
        _logger.set_logger_formatter(logger)


def _parse_bool(value: str) -> bool:
    try:
        return bool(int(value))
    except ValueError as exc:
        if value.lower() in {"true", "yes", "y", "t"}:
            return True
        if value.lower() in {"false", "no", "n", "f"}:
            return False
        raise ValueError(f"Cannot parse value '{value}' to boolean") from exc


class NotRuntimeChangeableException(Exception):
    """
    When :class:`SessionVariable`().value is assigned, this exception will be raised
    if :attr:`runtime_changeable` is `False`
    """

    def __init__(self, name: str, env_var_name: str):
        super().__init__(
            f"Session variable '{name}' is not writable during runtime, "
            f"restart the session with environment variable "
            f"'{env_var_name}' instead."
        )


@_dataclasses.dataclass(frozen=True)
class PluginExtrasEntrypointNames:
    """A frozen dataclass for organizing entrypoint name constants for plugin extras."""

    core_import_callback: str = "core-import-callback"
    """The entrypoint name for callbacks that execute after |tamm| import."""

    core_transformers_import_callback: str = "core-transformers-import-callback"
    """The entrypoint name for callbacks that execute after :mod:`tamm.hf.transformers` import."""

    cli: str = "cli"
    """The entrypoint name for submodules that define |tamm| CLI commands."""

    tokenizer_registry: str = "tokenizer-registry"
    """The entrypoint name for plugins that define **a factory of** tokenizer registry."""

    preprocessor_registry: str = "preprocessor-registry"
    """The entrypoint name for plugins that define **a factory of** preprocessor registry."""


class RuntimeConfigurationBase:
    def reset(self, *names: str) -> None:
        """
        Reset RC variables to their defaults.

        Args:
            *names (:obj:`str`, optional):  The name of the property (or properties) to reset.
                If empty, the function resets all properties.
        """
        if len(names) == 0:
            names = tuple(
                key
                for key, val in vars(self.__class__).items()
                if isinstance(val, property)
            )
        for name in names:
            try:
                delattr(self, name)
            except AttributeError:
                pass


class RuntimeConfiguration(RuntimeConfigurationBase):
    """A class that organizes |tamm| global constants and variables."""

    flash_attn_max_num_segments = RCVariable.create_property(
        name="flash_attn_max_num_segments",
        default=8,
        doc="Max number of segments for flash attention (must be a multiple of 8)",
    )

    log_format = LogFormatRCVariable.create_property(
        name="log_format",
        default="%(asctime)s:%(name)s:%(lineno)s:%(levelname)s: %(message)s",
        doc="Log format of the root |tamm| :obj:`logging.Logger`",
    )

    log_level = LogLevelRCVariable.create_property(
        name="log_level",
        default="INFO",
        doc="Log level of the root |tamm| :obj:`logging.Logger`",
    )

    uri_handler = RCVariable.create_property(
        default="boto3",
        name="uri_handler",
        doc="Default URI handler",
        parse_hook=lambda x: x.lower(),
    )

    user_dir = RCVariable.create_property(
        default=str(_pathlib.Path().home() / ".tamm"),
        name="user_dir",
        doc="A local directory for caching downloads and storing tmp files",
    )

    PROJECT_SLUG = RCConstant.create_property(value="tamm", doc="Name of this project")

    BASE_ADAPTER_GROUP_NAME = RCConstant.create_property(
        value="base_adapter",
        doc="Name of the default adapter if model is adapted",
    )

    MARKER_ATTRIBUTE = RCConstant.create_property(
        value="_tamm_marker",
        doc="nn.Module attribute name to keep track of extra markers",
    )

    PLUGINS_ENTRYPOINT_GROUP = RCConstant.create_property(
        value="tamm.plugins", doc="The entrypoint group for |tamm| plugins"
    )

    PLUGINS_EXTRAS_ENTRYPOINT_GROUP = RCConstant.create_property(
        value="tamm.plugins.extras", doc="The entrypoint group for |tamm| plugin extras"
    )

    PLUGINS_EXTRAS_ENTRYPOINT_NAMES = RCConstant.create_property(
        value=PluginExtrasEntrypointNames(),
        doc="The :obj:`.PluginExtrasEntrypointNames` for |tamm| plugin extras",
    )

    adapters_implementation = RCVariable.create_property(
        name="adapters_implementation",
        default="v1",
        doc="Implementation of :mod:`tamm.adapters`",
        choices=["v1"],
        parse_hook=lambda x: x.lower(),
        runtime_changeable=False,
    )


@_functools.cache
def _get_rc() -> RuntimeConfiguration:
    return RuntimeConfiguration()


rc = _get_rc()
