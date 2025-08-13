import contextlib
import copy
import dataclasses
import enum as enum_module
import functools
import inspect
import itertools
import logging
import operator
import os
import pathlib
import shutil
import textwrap
import time
import weakref
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Collection,
    ContextManager,
    Dict,
    Iterable,
    List,
    Optional,
    Union,
    cast,
)

import filelock
import torch
import torch.nn as _nn
from packaging.version import parse as parse_version

if TYPE_CHECKING:
    from tamm.typing import (
        OptionalDeviceOrString,
        OptionalDtypeOrString,
        PathLike,
        StateDictType,
    )
logger = logging.getLogger(__name__)


def case_insensitive_lookup(enum_class, value):
    value = value.lower()
    for member in enum_class:
        if member.lower() == value:
            return member
    return None


def get_item_by_index(iterable: "Iterable[Any]", idx: int) -> Any:
    """
    Returns the idx-th item of an iterable.  This function also supports negative
    indexing if the iterable has a __len__() method.

    Example: Get the last key in a dictionary d: get_item_by_index(d.keys(), -1)
    """
    idx = operator.index(idx)
    if idx > 0:
        new_idx = idx
    elif idx >= -len(iterable):
        new_idx = idx % len(iterable)
    else:
        raise IndexError(f"Index {idx} out of range")

    try:
        return next(itertools.islice(iterable, new_idx, None))
    except StopIteration:
        # pylint: disable=raise-missing-from
        raise IndexError(f"Index {idx} out of range")


def count_iterable(itr: Iterable[Any]) -> int:
    return sum(1 for el in itr)


def maybe_slice_to_string(obj):
    if not isinstance(obj, slice):
        return str(obj)
    start = str(obj.start) if obj.start is not None else ""
    stop = str(obj.stop) if obj.stop is not None else ""
    pieces = [start, stop]
    if obj.step is not None:
        pieces.append(str(obj.step))
    return ":".join(pieces)


# pylint: disable-next=inconsistent-return-statements
def make_key_unique(key: str, existing_keys: Collection[str]) -> str:
    """
    Returns the key if it is not in existing_keys.  Otherwise finds a new key that is
    not in existing_keys and returns that.
    """
    for attempt in itertools.count():
        candidate = key if attempt == 0 else f"{key}_{attempt}"
        if candidate not in existing_keys:
            return candidate


def copy_if_not_none(obj: Any) -> Any:
    """Returns None if the object is None and otherwise a shallow copy of the object."""
    return None if obj is None else copy.copy(obj)


def cumsum(numbers: Iterable[Union[int, float]]) -> List[Union[int, float]]:
    """Returns the cumulative sum of an iterable."""
    result = [0] * len(numbers)
    for idx, num in enumerate(numbers):
        result[idx] = result[idx - 1] + num
    return result


def get_dict_key_from_value(dictionary, value):
    for key, keys_value in dictionary.items():
        if keys_value == value:
            return key
    return None


def merge_dicts(*dicts):
    """
    Merges dictionaries into a single dictionary. If a key appears multiple times in
    *dicts, the resulting value comes from the last dict with that key.
    """
    return dict(itertools.chain.from_iterable(d.items() for d in dicts))


def get_enum_member_from_name(
    enum: enum_module.EnumMeta, member_or_name: Union[enum_module.Enum, str]
) -> enum_module.Enum:
    """
    Helper to lookup Enums by [].
    Handle string enums in a special way for torch.compile().

    Context:

        Enum lookup by instantiation, i.e., ``ColorEnum("red")``, generally works in
        Python. However, if ``forward()`` implementation of compiled module involves
        Enum resolution, it will fail ``torch.compile()`` with the following error:

            'Enum variable is constructed with non-constant values'

    Args:
        enum: Enum type (i.e., EnumMeta)
        member_or_name: string or Enum

    Returns: Enum member
    """

    if isinstance(member_or_name, enum):
        return cast(enum_module.Enum, member_or_name)

    if isinstance(member_or_name, str):
        name = member_or_name.upper()
        try:
            return enum[name]  # do not change this, see docstring
        except KeyError as exception:
            valid_choices = [el.name for el in enum]  # type: ignore
            raise ValueError(
                f"Name '{name}' not found in {enum}. "
                f"Valid choices include {valid_choices}."
            ) from exception
    raise TypeError(
        f"Please pass a member of {enum} or a string corresponding to the name of one "
        "of its members."
    )


def maybe_build_module(
    obj: Union[Callable[[], _nn.Module], _nn.Module, None], *args, **kwargs
) -> Union[_nn.Module, None]:
    """
    Helper function for creating layers from objects that may be a LayerBuilder or
    possibly None or a nn.Module already.

    Args:
        obj: Any callable that returns a nn.Module -- or a nn.Module or None.
        args, kwargs: Optional args and kwargs for the callable.

    Returns:
        The nn.Module returned by the callable -- or the existing nn.Module or None if
        the input is already one of those.
    """
    return maybe_build_object(obj, _nn.Module, *args, **kwargs)


def maybe_build_object(obj, target_cls, *args, **kwargs):
    if obj is None:
        return None
    if isinstance(obj, target_cls):
        return obj
    return obj(*args, **kwargs)


def append_children(
    module, /, register_none_children: bool = False, **child_names_and_modules
):
    """
    Appends new nn.Modules to the end of the list of module's children.

    Args:
        module (:obj:`nn.Module`): The parent module that will receive the children.
        register_none_children (:obj:`bool`): Whether to register a child on
            ``module`` when the child is ``None``.  Defaults to ``False``.  This
            mainly affects whether the child appears in the module's ``repr()``.
        child_names_and_modules: Names and LayerBuilders for the children.
    """
    _assert_module_does_not_have_attributes(module, child_names_and_modules.keys())
    for name, child in child_names_and_modules.items():
        child = maybe_build_module(child)
        if hasattr(module, name):
            delattr(module, name)
        if register_none_children:
            module.register_module(name, child)
        else:
            setattr(module, name, child)


def prepend_children(
    module, /, register_none_children: bool = False, **child_names_and_modules
):
    """
    The same as :func:`append_children` but adds the new children at the start of the
    list.  Adding at the start is sometimes helpful for organizing the module's repr.
    """
    _assert_module_does_not_have_attributes(module, child_names_and_modules.keys())
    child_names_and_modules.update(module.named_children())
    for name, child in child_names_and_modules.items():
        child = maybe_build_module(child)
        if hasattr(module, name):
            delattr(module, name)
        if register_none_children:
            module.register_module(name, child)
        else:
            setattr(module, name, child)


def get_all_named_children(module):
    """
    Returns the names of all a module's children, not just the unique children from
    module.named_children().
    """
    for name, submodule in module.named_modules(remove_duplicate=False):
        if name != "" and "." not in name:
            yield name, submodule


def _assert_module_does_not_have_attributes(module, attribute_names):
    for name in attribute_names:
        if hasattr(module, name):
            raise RuntimeError(
                f"{module.__class__.__name__} already has an attribute named {name}"
            )


def are_views_identical(view1, view2):
    if view1.data_ptr() != view2.data_ptr():
        return False
    if view1.shape != view2.shape:
        return False
    if view1.stride() != view2.stride():
        return False
    return True


def get_dtype_from_maybe_string(obj: Union[str, torch.dtype, None]) -> torch.dtype:
    if obj is None:
        return None
    if isinstance(obj, str):
        return getattr(torch, obj)
    return obj


def get_str_from_maybe_dtype(obj: Union[str, torch.dtype, None]) -> Union[str, None]:
    if obj is None:
        return None
    if isinstance(obj, torch.dtype):
        return str(obj)[6:]  # 6: removes the torch. prefix
    return obj


def get_dtype_after_autocast(dtype: torch.dtype, device: torch.device) -> torch.dtype:
    # pylint: disable=import-outside-toplevel
    from tamm.utils import _torch_compatibility

    if not dtype.is_floating_point:
        return dtype
    if _torch_compatibility.is_autocast_enabled(device.type):
        return _torch_compatibility.get_autocast_dtype(device.type)
    return dtype


def autocast_disabled(device: torch.device):
    """Returns a context manager that disabled autocast within the context."""
    if device.type == "mps" and is_torch_base_version_less_than("2.5"):
        return contextlib.nullcontext()  # mps does not support autocast as of torch 2.4
    return torch.autocast(device.type, enabled=False)


def maybe_cast_state_dict_(
    state_dict: "StateDictType", *, dtype: "OptionalDtypeOrString" = None
):
    """
    If dtype is not None, this function casts tensors in state_dict.values() to dtype.
    This modifies the state dict *in place*.
    """
    dtype = get_dtype_from_maybe_string(dtype)
    if dtype is None:
        return
    for key, value in state_dict.items():
        if not torch.is_tensor(value) or not value.is_floating_point():
            continue
        state_dict[key] = value.type(dtype)


def make_noop_when_recursing(fn):
    is_recursing = False

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        nonlocal is_recursing
        if is_recursing:
            return None
        is_recursing = True
        result = fn(*args, **kwargs)
        is_recursing = False
        return result

    return wrapper


CACHED_FUNCTIONS = weakref.WeakSet()


def cache(user_function: "Callable") -> Callable:
    caching_fn = functools.lru_cache(maxsize=None)(user_function)

    @functools.wraps(caching_fn)
    def wrapper(*args, **kwargs):
        # wrap again because lru_cache does not support weakref in Py3.8
        return caching_fn(*args, **kwargs)

    wrapper.cache_clear = caching_fn.cache_clear

    try:  # register cached functions so that we can reset them during testing
        CACHED_FUNCTIONS.add(wrapper)
    except Exception as e:  # pylint: disable=broad-except
        log_exception(e, context_name="adding weakref to cached function")
    return wrapper


def catch_and_log_exceptions(fn=None, context_name=None):
    if fn is None:
        return _catch_and_log_exceptions_context(context_name=context_name)

    if context_name is None:
        context_name = fn.__name__

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        context = _catch_and_log_exceptions_context(context_name=context_name)
        with context:
            fn(*args, **kwargs)

    return wrapper


@contextlib.contextmanager
def _catch_and_log_exceptions_context(context_name=None):
    try:
        yield
    except Exception as e:  # pylint: disable=broad-except
        log_exception(e, context_name=context_name)


def log_exception(exception, context_name: Optional[str] = None) -> None:
    name_str = f" during {context_name}" if context_name is not None else ""
    logger.debug("Caught exception%s: %s", name_str, exception, exc_info=True)


def get_all_params_and_buffers(module) -> List[torch.Tensor]:
    return list(itertools.chain(module.parameters(), module.buffers()))


def get_device_context(device: "OptionalDeviceOrString") -> "ContextManager":
    """
    Returns a context manager that changes the default device to ``device``.  If
    ``device`` is None, returns a null context.
    """
    if device is None:
        return contextlib.nullcontext()
    if isinstance(device, torch.device):
        return device
    return torch.device(device)


def move_meta_tensors_to_device(module, device=None):
    """
    Iterates over parameters and buffers in module (and its submodules), overwriting
    them with new tensors on device of the same shape and dtype.  Tied params or buffers
    remain tied.  If device is None, the function uses the default device.
    """
    meta_tensor_to_real_tensor = {}
    for submodule in module.modules():
        named_params_and_buffers = itertools.chain(
            submodule.named_parameters(recurse=False),
            submodule.named_buffers(recurse=False),
        )
        for name, tensor in list(named_params_and_buffers):
            if not tensor.is_meta:
                continue

            if tensor in meta_tensor_to_real_tensor:
                real_tensor = meta_tensor_to_real_tensor[tensor]
            else:
                real_tensor = torch.empty(
                    tensor.shape,
                    dtype=tensor.dtype,
                    device=device,
                    layout=tensor.layout,
                    requires_grad=tensor.requires_grad,
                    # don't use empty_like(tensor) here because if device is None, we
                    # want to use the default device, not tensor's device
                )
                if isinstance(tensor, torch.nn.Parameter):
                    real_tensor = torch.nn.Parameter(
                        real_tensor, requires_grad=tensor.requires_grad
                    )
                meta_tensor_to_real_tensor[tensor] = real_tensor

            if isinstance(real_tensor, torch.nn.Parameter):
                delattr(submodule, name)
                setattr(submodule, name, real_tensor)
            else:
                persistent = name in submodule.state_dict(keep_vars=True)
                delattr(submodule, name)
                submodule.register_buffer(name, real_tensor, persistent=persistent)


def get_timestamp_ms() -> int:
    return time.time_ns() // 1_000_000


@contextlib.contextmanager
def file_lock(lock_path: "PathLike"):
    """
    A simple wrapper around filelock.FileLock that adds logging and creates the parent
    dir for the lock file if it does not already exist.
    """
    lock_path = pathlib.Path(lock_path)
    os.makedirs(lock_path.parent, exist_ok=True)
    logger.debug("Acquiring file lock %s", lock_path)
    with filelock.FileLock(lock_path):
        yield
    logger.debug("File lock released")


def truncate_lines_for_terminal(*lines):
    terminal_size = shutil.get_terminal_size()
    max_width = terminal_size.columns
    return [x if len(x) < max_width else x[: max_width - 1] + "…" for x in lines]


def strip_prefix_from_state_dict_keys(state_dict, prefix):
    new_state_dict = {}
    for key, val in state_dict.items():
        if key.startswith(prefix):
            key = key[len(prefix) :]
        new_state_dict[key] = val
    return new_state_dict


def add_prefix_to_state_dict_keys(state_dict, prefix):
    return {prefix + k: v for k, v in state_dict.items()}


def parse_base_version(version_str: str) -> str:
    """
    Function to parse base version from a given version string.

    Example: version_str of "2.0.1+cu117" provides "2.0.1"
    """
    return parse_version(parse_version(version_str).base_version)


def is_torch_base_version_less_than(version_str: str) -> bool:
    """
    Function to check whether the runtime torch version
    is less than a given base version.
    """
    return parse_base_version(torch.__version__) < parse_base_version(version_str)


def passthrough_decorator(fn):
    """
    This is a decorator that wraps a function but otherwise does nothing.  One use case
    is to create a "copy" of a function for the purpose of setting its __doc__ or
    __signature__ attributes.
    """

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapped


def get_function_from_maybe_method(fn):
    if inspect.ismethod(fn):
        return fn.__func__
    return fn


class hybridmethod:  # pylint: disable=invalid-name
    """
    A decorator similar to @classmethod except the resulting method works both as a
    class method and an instance method.  Depending on how the user calls the method,
    the typical ``cls`` or ``self`` argument may be either the class or the instance.

    Example:

        .. code-block:: python

            class MyClass:
                def __init__(self, value: int = 5):
                    self.value = value

                @hybridmethod
                def get_value(self_or_cls) -> int:
                    if isinstance(self_or_cls, MyClass):  # called as an instance method
                        obj = self_or_cls
                    else:
                        obj = self_or_cls()  # called as a class method
                    return obj.value

            print(MyClass.get_value())  # 5

            instance = MyClass(value=7)
            print(instance.get_value())  # 7
    """

    def __init__(self, func):
        self.__wrapped__ = func

    def __get__(self, obj, objtype=None):
        @functools.wraps(self.__wrapped__)
        def wrapped(*args, **kwargs):
            if obj is None:
                return self.__wrapped__(objtype, *args, **kwargs)
            return self.__wrapped__(obj, *args, **kwargs)

        return wrapped


def add_kw_only_params_to_signature(
    signature: inspect.Signature, kw_only_params: List[inspect.Parameter]
) -> inspect.Signature:
    """
    Creates a new signature, which is the same as ``signature`` but with extra
    keyword-only params from ``kw_only_params``.
    """
    new_params = [
        p for p in signature.parameters.values() if p.kind is not p.VAR_KEYWORD
    ]
    new_params.extend(kw_only_params)
    new_params.extend(
        p for p in signature.parameters.values() if p.kind is p.VAR_KEYWORD
    )
    return signature.replace(parameters=new_params)


def dataclass_to_dict(dataclass, *, omit_defaults: bool = False) -> Dict[str, Any]:
    result = {}
    for field in dataclasses.fields(dataclass):
        if not hasattr(dataclass, field.name):
            continue
        value = getattr(dataclass, field.name)
        if omit_defaults:
            if field.default is not dataclasses.MISSING and value == field.default:
                continue
            if (
                field.default_factory is not dataclasses.MISSING
                and value == field.default_factory()
            ):
                continue
        result[field.name] = value
    return result


def update_dataclass_fields(dataclass, *args, **kwargs):
    """
    Updates many fields at once. The structure of *args, **kwargs should align
    with the default dataclass __init__().
    """
    if len(args) > 0:
        positional_fields = [
            f for f in dataclasses.fields(dataclass) if f.init and not f.kw_only
        ]
        if len(args) > len(positional_fields):
            raise TypeError(
                f"update_dataclass_fields() takes {len(positional_fields)} positional arguments "
                f"but {len(args)} were given for {dataclass.__class__}"
            )

        for field, arg in zip(positional_fields, args):
            if field.name in kwargs:
                raise TypeError(
                    f"update_dataclass_fields() got multiple values for field '{field.name}' "
                    f"when updating a {dataclass.__class__} instance"
                )
            kwargs[field.name] = arg

    field_names = map(operator.attrgetter("name"), dataclasses.fields(dataclass))
    extra_keys = kwargs.keys() - field_names
    if extra_keys:
        raise RuntimeError(
            f"arguments contain keys that are not fields of the dataclass: {extra_keys}"
        )

    for name, value in kwargs.items():
        setattr(dataclass, name, value)


def set_annotated_class_attr(cls, attr, value, annotation):
    """
    Sets an attribute of cls and also updates cls.__annotations__ with an annotation.
    """
    setattr(cls, attr, value)
    annotations = getattr(cls, "__annotations__", {})
    annotations = copy.copy(annotations)
    annotations[attr] = annotation
    setattr(cls, "__annotations__", annotations)


def maybe_get_enum_member_for_all_str_enums(dictionary: dict, dataclass_type):
    """
    This method converts literals to Enum in a ``dictionary`` of ``dataclass_type``
    Enum datatypes are determined from types annotation *without* forward reference.

    .. code-block:: python

        from tamm.utils import OptionalBool
        from tamm.utils.json._utils import JSONSerializableMixin

        @dataclasses.dataclass
        class MyDataclass(JSONSerializableMixin):

            # **[INCOMPATIBLE IMPLEMENTATION]**
            # Declaration style 1: will NOT deserialize to OptionalBool from
            # {"freeze_params": "TRUE"}
            freeze_params: "OptionalBool" = OptionalBool.NOTSET

             # Declaration style 2: WILL deserialize to OptionalBool from
            # {"freeze_params": "TRUE"}
            freeze_params: OptionalBool = OptionalBool.NOTSET

            @classmethod
            def _from_json_dict_impl(cls, **raw_dict: dict):
                raw_dict = maybe_get_enum_member_for_all_str_enums(raw_dict, cls)
                return super()._from_json_dict_impl(**raw_dict)

    Args:
        dictionary: raw dictionary for dataclass attribute
        dataclass_type: dataclass to initialize

    Returns: Dataclass instance of ``dataclass_type``

    """
    enum_fields = {
        f.name: f.type
        for f in dataclasses.fields(dataclass_type)
        if isinstance(f.type, enum_module.EnumMeta)
    }
    try:
        for enum_field, enum_class in enum_fields.items():
            dictionary[enum_field] = enum_class(dictionary[enum_field])
    except KeyError:
        # if dictionary[enum_field] is not found (i.e., some attribute of a
        # enum type not specified in the dictionary) this should still go through.
        pass
    except (ValueError, TypeError) as e:
        raise e
    return dictionary


def dataclass_init_drop_missing_keys(kwargs: Dict[str, Any], *, dataclass_type):
    """
    Returns the result of ``dataclass_type(**kwargs)`` but first filters any keys from
    kwargs that are not in the dataclass field names.

    .. warning::

        Use this *ONLY* on dataclasses like `ModuleMetadata` which can leniently
        ignore newer keys.

    This method also converts literals to Enum for attributes of
    Enum types annotated *without* forward reference.

    Args:
        kwargs: raw dictionary for dataclass attribute
        dataclass_type: dataclass to initialize

    Returns: Dataclass instance of ``dataclass_type``

    """
    field_names = set(field.name for field in dataclasses.fields(dataclass_type))
    incompatible_keys = [key for key in kwargs if key not in field_names]
    kwargs = maybe_get_enum_member_for_all_str_enums(kwargs, dataclass_type)

    if len(incompatible_keys) > 0:
        kwargs = {key: val for key, val in kwargs.items() if key in field_names}
        logger.debug(
            "Ignoring incompatible keys %s when instantiating dataclass %s",
            incompatible_keys,
            dataclass_type,
        )
    return dataclass_type(**kwargs)


class DataClassReprMixin:
    def __repr__(self):
        obj = dataclass_to_dict(self)
        reprs = [f"{key}={repr(value)}," for key, value in obj.items()]
        joined = "\n".join(reprs)
        joined = textwrap.indent(joined, prefix=" " * 4)
        return f"{self.__class__.__name__}(\n{joined}\n)"


def clean_docstring(doc: Optional[str]) -> Union[str, None]:
    if doc is None:
        return None
    doc = inspect.cleandoc(doc)
    return doc.replace("\n", " ").replace("\r", " ")


def get_cleaned_docstring(func: Callable[..., Any]) -> Union[str, None]:
    doc = inspect.getdoc(func)
    return clean_docstring(doc)


def get_expanded_abspath(path):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    return os.path.abspath(path)


def size_in_bytes_to_string(num_bytes):
    # pylint: disable=invalid-name
    KiB = 1024
    MiB = KiB**2
    GiB = KiB**3
    if num_bytes > GiB:
        return f"{num_bytes / GiB:.1f} GiB"
    if num_bytes > MiB:
        return f"{num_bytes / MiB:.1f} MiB"
    if num_bytes > KiB:
        return f"{num_bytes / KiB:.1f} KiB"
    return f"{num_bytes} bytes"
