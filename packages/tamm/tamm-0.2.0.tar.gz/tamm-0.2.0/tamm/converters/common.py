"""
This module implements the base converter type as well as some reusable components for
building converters.
"""

import abc as _abc
import collections as _collections
import functools as _functools
import re as _re
import warnings as _warnings
from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch

from tamm import _helpers
from tamm.typing import StateDictType as _StateDictType


class StateDictConverter(_abc.ABC):
    """
    An abstract interface for converting a |tamm| state dict to or from an
    "other" format.
    """

    @_abc.abstractmethod
    def is_tamm_key(self, key: str) -> bool:
        """Returns ``True`` if ``key`` is a |tamm| key and ``False`` otherwise."""

    @_abc.abstractmethod
    def is_other_key(self, key: str) -> bool:
        """
        Returns ``True`` if ``key`` is a key for the non-|tamm| format and ``False``
        otherwise.
        """

    def convert_from_tamm(self, state_dict: _StateDictType) -> _StateDictType:
        """Converts ``state_dict`` from |tamm| format to the other format."""
        unrecognized_keys = [key for key in state_dict if not self.is_tamm_key(key)]
        if len(unrecognized_keys) > 0:
            _warnings.warn(
                f"{self.__class__.__name__}.convert_from_tamm() called with "
                f"unrecognized keys: {unrecognized_keys}"
            )
        return self._convert_from_tamm_impl(state_dict)

    @_abc.abstractmethod
    def _convert_from_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        """Converts ``state_dict`` from |tamm| format to the other format."""

    def convert_to_tamm(self, state_dict: _StateDictType) -> _StateDictType:
        """Converts ``state_dict`` to |tamm| format from the other format."""
        unrecognized_keys = [key for key in state_dict if not self.is_other_key(key)]
        if len(unrecognized_keys) > 0:
            _warnings.warn(
                f"{self.__class__.__name__}.convert_to_tamm() called with unrecognized "
                f"keys: {unrecognized_keys}"
            )
        return self._convert_to_tamm_impl(state_dict)

    @_abc.abstractmethod
    def _convert_to_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        """Converts ``state_dict`` to tamm format from the other format."""


class UnionConverter(StateDictConverter):
    """
    A class for composing multiple independent :obj:`StateDictConverter` instances
    into a single converter.  Each converter takes responsibility for converting
    the subset of keys that match (according to :meth:`is_tamm_key` or
    :meth:`is_other_key`).

    If multiple converters output a converted weight with the same name, the merging
    mechanism takes the weight from the last converter in the converters list.

    Args:
        *converters: One or more converters of type :class:`StateDictConverter`.
    """

    def __init__(self, *converters):
        if len(converters) == 0:
            raise ValueError("UnionConverter requires at least one converter")
        self._converters = converters

    def is_tamm_key(self, key: str) -> bool:
        return any(c.is_tamm_key(key) for c in self._converters)

    def is_other_key(self, key: str) -> bool:
        return any(c.is_other_key(key) for c in self._converters)

    def _convert_from_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        sub_dicts = [
            {key: val for key, val in state_dict.items() if c.is_tamm_key(key)}
            for c in self._converters
        ]
        converted_sub_dicts = [
            c.convert_from_tamm(sub_dict)
            for c, sub_dict in zip(self._converters, sub_dicts)
        ]
        return _helpers.merge_dicts(*converted_sub_dicts)

    def _convert_to_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        sub_dicts = [
            {key: val for key, val in state_dict.items() if c.is_other_key(key)}
            for c in self._converters
        ]
        converted_sub_dicts = [
            c.convert_to_tamm(sub_dict)
            for c, sub_dict in zip(self._converters, sub_dicts)
        ]
        return _helpers.merge_dicts(*converted_sub_dicts)


class SequentialConverter(StateDictConverter):
    """
    A class for composing multiple independent :obj:`StateDictConverter` instances
    sequentially.  When converting from ``tamm``, the converter sequentially applies
    the ``from-tamm`` transformation of each subconverter, following the order of
    the subconverters during initialization of the parent converter.  When
    converting to ``tamm``, the converter applies the ``to-tamm`` transformation
    of each subconverter  in reverse order.

    Args:
        *converters: One or more converters of type :class:`StateDictConverter`.
    """

    def __init__(self, *converters):
        if len(converters) == 0:
            raise ValueError("SequentialConverter requires at least one converter")
        self._converters = converters

    def is_tamm_key(self, key: str) -> bool:
        return self._converters[0].is_tamm_key(key)

    def is_other_key(self, key: str) -> bool:
        return self._converters[-1].is_other_key(key)

    def _convert_from_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        for converter in self._converters:
            state_dict = converter.convert_from_tamm(state_dict)
        return state_dict

    def _convert_to_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        for converter in reversed(self._converters):
            state_dict = converter.convert_to_tamm(state_dict)
        return state_dict


class LayerwiseConverter(StateDictConverter):
    """
    A converter for state dicts with repeated layers.  For example, this class could
    help convert an "other" state dict with keys::

        [block0.weight0, block0.weight1, block1.weight0, block1.weight1]

    to a tamm state dict with keys::

        [layer_0.a.weight, layer_0.b.weight, layer_1.a.weight, layer_0.b.weight]

    Args:
        layer_converter (:obj:`StateDictConverter`): A converter for the repeated layer.
            For the example described above, this should convert an other state dict
            with keys ``["weight0", "weight1"]`` to one with keys
            ``["a.weight", "b.weight"]``.
        tamm_layer_prefix (:obj:`str`): The prefix for tamm layers, but with
            ``"<layer_idx>"`` substituted for the layer index.  This would be
            ``"layer_<layer_idx>."`` for the example above.
        other_layer_prefix (:obj:`str`): The prefix for "other" layers.  This would be
            ``"block<layer_idx>."`` for the example above.
        other_layer_idx_offset (:obj:`int`): An offset for the layer indexing of the
            other model.  Set to 1 if the other model uses 1-based indexing.
        max_other_layer_idx (:obj:`int`, optional): Matches until this layer index of
            the other model. Set to ``None`` if there's no matching limit.
        min_other_layer_idx (:obj:`int`, optional): Matches starting from this layer
            index of the other model.  Set to ``None`` to match from the smallest
            index.  Defaults to ``None``.
    """

    LAYER_IDX_PATTERN = "<layer_idx>"

    def __init__(
        self,
        layer_converter: StateDictConverter,
        tamm_layer_prefix: str,
        other_layer_prefix: str,
        other_layer_idx_offset: int = 0,
        max_other_layer_idx: _Optional[int] = None,
        min_other_layer_idx: _Optional[int] = None,
    ):
        self._layer_converter = layer_converter
        self._tamm_layer_prefix = tamm_layer_prefix
        self._other_layer_prefix = other_layer_prefix
        self._other_layer_idx_offset = other_layer_idx_offset
        self._max_other_layer_idx = max_other_layer_idx
        self._min_other_layer_idx = min_other_layer_idx

    @_functools.cached_property
    def _tamm_layer_prefix_regex(self):
        return self._get_regex_from_layer_prefix(self._tamm_layer_prefix)

    @_functools.cached_property
    def _other_layer_prefix_regex(self):
        return self._get_regex_from_layer_prefix(self._other_layer_prefix)

    @classmethod
    def _get_regex_from_layer_prefix(cls, layer_prefix):
        escaped_prefix = _re.escape(layer_prefix)
        escaped_layer_idx_pattern = _re.escape(cls.LAYER_IDX_PATTERN)
        pattern = escaped_prefix.replace(escaped_layer_idx_pattern, r"([\d]+)")
        return _re.compile(pattern)

    def is_tamm_key(self, key: str) -> bool:
        match = self._match_prefix(self._tamm_layer_prefix_regex, key)
        if match is None:
            return False
        _, remaining_key = match
        return self._layer_converter.is_tamm_key(remaining_key)

    def is_other_key(self, key: str) -> bool:
        match = self._match_prefix(self._other_layer_prefix_regex, key)
        if match is None:
            return False
        _, remaining_key = match
        return self._layer_converter.is_other_key(remaining_key)

    @staticmethod
    def _match_prefix(compiled_prefix_regex, key):
        """
        Returns (layer_idx, remaining_key) if key matches the regex and None otherwise.
        Here remaining_key is everything that comes after the prefix.
        """
        match = compiled_prefix_regex.match(key)
        if match is None:
            return None
        layer_idx = match.group(1)
        remaining_key = key[match.end() :]
        return layer_idx, remaining_key

    def _convert_to_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        state_subdicts_by_layer = self._get_state_subdicts_by_layer(
            self._other_layer_prefix_regex, state_dict
        )
        result = {}
        for layer_idx, state_subdict in state_subdicts_by_layer.items():
            if self._min_other_layer_idx is not None:
                if int(layer_idx) < self._min_other_layer_idx:
                    continue
                layer_idx = str(
                    int(layer_idx)
                    - self._other_layer_idx_offset
                    - self._min_other_layer_idx
                )
            else:
                layer_idx = str(int(layer_idx) - self._other_layer_idx_offset)
            converted_state = self._layer_converter.convert_to_tamm(state_subdict)
            prefix = self._tamm_layer_prefix.replace(self.LAYER_IDX_PATTERN, layer_idx)
            converted_state = {prefix + k: v for k, v in converted_state.items()}
            result.update(converted_state)
        return result

    def _convert_from_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        state_subdicts_by_layer = self._get_state_subdicts_by_layer(
            self._tamm_layer_prefix_regex, state_dict
        )
        result = {}
        for layer_idx, state_subdict in state_subdicts_by_layer.items():
            if self._min_other_layer_idx is not None:
                layer_idx = str(
                    int(layer_idx)
                    + self._other_layer_idx_offset
                    + self._min_other_layer_idx
                )
            else:
                layer_idx = str(int(layer_idx) + self._other_layer_idx_offset)
            converted_state = self._layer_converter.convert_from_tamm(state_subdict)
            prefix = self._other_layer_prefix.replace(self.LAYER_IDX_PATTERN, layer_idx)
            converted_state = {prefix + k: v for k, v in converted_state.items()}
            result.update(converted_state)
        return result

    def _get_state_subdicts_by_layer(self, compiled_prefix_regex, state_dict):
        """
        Returns a dictionary that maps the layer index for each layer to the state dict
        for that layer.  The keys in each state dict no longer contain the prefix.
        """
        result = _collections.defaultdict(dict)
        for key, param in state_dict.items():
            match = self._match_prefix(compiled_prefix_regex, key)
            if match is None:
                raise ValueError(f"{key} did not match {compiled_prefix_regex}")
            layer_idx, remaining_key = match
            if (
                self._max_other_layer_idx is not None
                and int(layer_idx) > self._max_other_layer_idx
            ):
                continue
            result[layer_idx][remaining_key] = param
        return result


class ParamMapper:
    """
    Defines a reversible mapping of a parameter.  The ``to_tamm_fn``
    and ``from_tamm_fn`` functions should be inverses of one another.

    Args:
        to_tamm_fn: The function for mapping the param from "other" to |tamm| format.
        from_tamm_fn: The function for mapping the param from |tamm| to "other" format.
    """

    def __init__(
        self,
        to_tamm_fn: _Callable[
            [_torch.Tensor], _Union[_torch.Tensor, _List[_torch.Tensor]]
        ],
        from_tamm_fn: _Callable[
            [_torch.Tensor], _Union[_torch.Tensor, _List[_torch.Tensor]]
        ],
    ):
        self._to_tamm_fn = to_tamm_fn
        self._from_tamm_fn = from_tamm_fn

    def to_tamm(self, *args):
        """Map the parameter to |tamm| format."""
        return self._to_tamm_fn(*args)

    def from_tamm(self, *args):
        """Map the parameter from |tamm| format."""
        return self._from_tamm_fn(*args)


class StringMatchingConverter(StateDictConverter):
    """
    Converts state dicts by mapping keys from one string to another
    optionally transforming the params.

    This class manages multiple sets of one-to-one parameter mappings. For
    more complex scenarios, consider using
    :class:`ManyToManyStringMatchingConverter`.

    Args:
        tamm_to_other_keys (:obj:`dict`): A dictionary that maps |tamm| keys to
            other keys.
        tamm_prefix (:obj:`str`, optional): A prefix to prepend to all keys in
            ``tamm_to_other_keys`` when matching strings.  Defaults to the empty string.
        other_prefix (:obj:`str`, optional): A suffix to prepend to all values in
            ``tamm_to_other_keys`` when matching strings.  Defaults to the empty string.
        param_mappers (:obj:`dict`): An optional dictionary that maps a subset of
            tamm keys (excluding the ``tamm_prefix``) to :obj:`ParamMapper` objects
            for transforming weights.
    """

    def __init__(
        self,
        tamm_to_other_keys: _Dict[str, str],
        *,
        tamm_prefix: str = "",
        other_prefix: str = "",
        param_mappers: _Dict[str, "ParamMapper"] = None,
    ):
        self._tamm_to_other_keys = tamm_to_other_keys
        self._tamm_prefix = tamm_prefix
        self._other_prefix = other_prefix
        self._param_mappers = {} if param_mappers is None else param_mappers

    @property
    def _tamm_keys(self):
        return self._tamm_to_other_keys.keys()

    @property
    def _other_keys(self):
        return self._tamm_to_other_keys.values()

    def is_tamm_key(self, key: str) -> bool:
        if not key.startswith(self._tamm_prefix):
            return False
        key = key.removeprefix(self._tamm_prefix)
        return key in self._tamm_keys

    def is_other_key(self, key: str) -> bool:
        if not key.startswith(self._other_prefix):
            return False
        key = key.removeprefix(self._other_prefix)
        return key in self._other_keys

    def _convert_to_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        tamm_state_dict = {}
        for other_key, other_param in state_dict.items():
            if not other_key.startswith(self._other_prefix):
                continue
            other_key = other_key.removeprefix(self._other_prefix)
            tamm_keys = [
                k for k, v in self._tamm_to_other_keys.items() if v == other_key
            ]
            for tamm_key in tamm_keys:
                mapper = self._param_mappers.get(tamm_key)
                tamm_param = other_param
                if mapper is not None:
                    tamm_param = mapper.to_tamm(other_param)
                tamm_state_dict[f"{self._tamm_prefix}{tamm_key}"] = tamm_param
        return tamm_state_dict

    def _convert_from_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        other_state_dict = {}
        for tamm_key, tamm_param in state_dict.items():
            if not tamm_key.startswith(self._tamm_prefix):
                continue
            tamm_key = tamm_key.removeprefix(self._tamm_prefix)
            other_key = self._tamm_to_other_keys[tamm_key]

            mapper = self._param_mappers.get(tamm_key)
            other_param = tamm_param
            if mapper is not None:
                other_param = mapper.from_tamm(tamm_param)
            other_state_dict[f"{self._other_prefix}{other_key}"] = other_param
        return other_state_dict


class ManyToManyStringMatchingConverter(StateDictConverter):
    """
    This class serves as an addition to :class:`StringMatchingConverter` to handle
    one-to-many, many-to-one, or many-to-many parameter relationships between |tamm|
    and other formats.

    Note that this class only manages one type of mapping relationship at a time,
    whereas :class:`StringMatchingConverter` handles multiple mappings
    simultaneously.

    Args:
        tamm_keys (:obj:`list` of :obj:`str`): A list of |tamm| keys to map.
        other_keys (:obj:`list` of :obj:`str`): A list of keys in other formats
            to map.
        param_mapper: A :class:`ParamMapper` that accepts the |tamm| weights
            and outputs the other weights (and vice versa).

    Example:

        Use ``fused_qkv_converter`` to combine separate query, key, and value
        weights into a single ``fused_qkv`` weight.

        .. code-block:: python

            param_mapper = ParamMapper(
                to_tamm_fn=lambda *tensors: torch.stack(tensors),
                from_tamm_fn=torch.unbind,
            )

            fused_qkv_converter = ManyToManyStringMatchingConverter(
                ["fused_qkv"], ["Q", "K", "V"], param_mapper
            )
    """

    def __init__(
        self,
        tamm_keys: _List[str],
        other_keys: _List[str],
        param_mapper: _Optional[ParamMapper] = None,
    ):
        self._tamm_keys = tamm_keys
        self._other_keys = other_keys
        self._param_mapper = param_mapper
        if len(self._tamm_keys) != len(self._other_keys) and self._param_mapper is None:
            raise ValueError(
                f"Lengths of tamm_keys ({len(self._tamm_keys)}) and "
                f"other_keys {len(self._other_keys)}) do not match. Please provide a "
                f"mapper when they are not of equal length."
            )

    def is_tamm_key(self, key: str) -> bool:
        return key in self._tamm_keys

    def is_other_key(self, key: str) -> bool:
        return key in self._other_keys

    def _convert_to_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        other_params = [state_dict[key] for key in self._other_keys]
        if self._param_mapper is not None:
            tamm_params = self._param_mapper.to_tamm(*other_params)
            if not isinstance(tamm_params, (list, tuple)):
                tamm_params = [tamm_params]
        else:
            tamm_params = other_params
        if len(self._tamm_keys) != len(tamm_params):
            raise ValueError(
                f"Lengths of tamm_keys ({len(self._tamm_keys)}) and the converted "
                f"tamm_params ({len(tamm_params)}) do not match."
            )
        return dict(zip(self._tamm_keys, tamm_params))

    def _convert_from_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        tamm_params = [state_dict[key] for key in self._tamm_keys]
        if self._param_mapper is not None:
            other_params = self._param_mapper.from_tamm(*tamm_params)
            if not isinstance(other_params, (list, tuple)):
                other_params = [other_params]
        else:
            other_params = tamm_params
        if len(self._other_keys) != len(other_params):
            raise ValueError(
                f"Lengths of other_keys ({len(self._other_keys)}) and the converted "
                f"other_params ({len(other_params)}) do not match."
            )
        return dict(zip(self._other_keys, other_params))


class PrefixStringMatchingConverter(StateDictConverter):
    """
    A converter wrapper that handles prefixes in front of keys.  When converting
    to |tamm|, this converter:

    1. Creates a sub dictionary of all weights with names starting with
       ``other_prefix``.
    2. Replaces the sub dictionary keys with only their suffixes.
    3. Converts the sub dictionary with ``converter``.
    4. Prepends ``tamm_prefixes`` to the keys of the result.

    Args:
        converter (:obj:`StateDictConverter`): A converter for the sub
            dictionary.
        tamm_prefix (:obj:`str`): Prefix for the |tamm| keys.
        other_prefix (:obj:`str`): Prefix for the other keys.
    """

    def __init__(
        self, *, converter: StateDictConverter, tamm_prefix: str, other_prefix: str
    ):
        self._converter = converter
        self._tamm_prefix = tamm_prefix
        self._other_prefix = other_prefix

    def is_tamm_key(self, key: str) -> bool:
        if not key.startswith(self._tamm_prefix):
            return False
        suffix = key[len(self._tamm_prefix) :]
        return self._converter.is_tamm_key(suffix)

    def is_other_key(self, key: str) -> bool:
        if not key.startswith(self._other_prefix):
            return False
        suffix = key[len(self._other_prefix) :]
        return self._converter.is_other_key(suffix)

    def _convert_from_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        state_dict = {
            k: v for k, v in state_dict.items() if k.startswith(self._tamm_prefix)
        }
        state_dict = _helpers.strip_prefix_from_state_dict_keys(
            state_dict, self._tamm_prefix
        )
        converted_dict = self._converter.convert_from_tamm(state_dict)
        converted_dict = _helpers.add_prefix_to_state_dict_keys(
            converted_dict, self._other_prefix
        )
        return converted_dict

    def _convert_to_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        state_dict = {
            k: v for k, v in state_dict.items() if k.startswith(self._other_prefix)
        }
        state_dict = _helpers.strip_prefix_from_state_dict_keys(
            state_dict, self._other_prefix
        )
        converted_dict = self._converter.convert_to_tamm(state_dict)
        converted_dict = _helpers.add_prefix_to_state_dict_keys(
            converted_dict, self._tamm_prefix
        )
        return converted_dict


class MultiPrefixStringMatchingConverter(UnionConverter):
    """
    A composition of :class:`PrefixStringMatchingConverter` converters
    to support multiple pairs of prefixes.  For example, this class could help
    convert an "other" state dict with keys::

        [block0.0.attention, block0.1.attention, block1.0.attention]

    to a |tamm| state dict with keys::

        [layer_0.attention, layer_1.attention, layer_2.attention]

    For this case, ``converter`` converts attention layers, while
    ``tamm_to_other_prefixes`` is the dictionary
    ``{"layer_0": "block0.0", "layer_1": "block0.1", "layer_2": "block1.0"}``.

    Args:
        converter (:obj:`StateDictConverter`): A converter for the selected
            weights.
        tamm_to_other_prefixes (:obj:`dict`): A dictionary that maps |tamm|
            prefixes to other prefixes.
    """

    def __init__(
        self, *, converter: StateDictConverter, tamm_to_other_prefixes: _Dict[str, str]
    ):
        converters = [
            PrefixStringMatchingConverter(
                tamm_prefix=tamm_prefix, other_prefix=other_prefix, converter=converter
            )
            for tamm_prefix, other_prefix in tamm_to_other_prefixes.items()
        ]
        super().__init__(*converters)


class RegExSubstitutionConverter(StateDictConverter):
    """
    A converter for mapping keys with regex substitutions, i.e., :func:`re.sub`.
    This converter is sometimes useful for modifying substrings in the middle
    of state dict keys.

    When converting from |tamm|, the converter computes other keys as follows:

    .. code-block:: python

       other_key = re.sub(tamm_pattern, from_tamm_repl, tamm_key)

    When converting to |tamm|, the converter maps the other keys similarly:

    .. code-block:: python

       tamm_key = re.sub(other_pattern, to_tamm_repl, other_key)

    Args:
        tamm_pattern: The regex pattern for |tamm| keys.
        from_tamm_repl: The ``repl`` argument for :func:`re.sub` when converting from
            |tamm|.
        other_pattern: The regex pattern for other keys.
        to_tamm_repl: The ``repl`` argument for :func:`re.sub` when converting to
            |tamm|.
    """

    def __init__(
        self,
        *,
        tamm_pattern: str,
        from_tamm_repl: str,
        other_pattern: str,
        to_tamm_repl: str,
    ):
        self._tamm_pattern = _re.compile(tamm_pattern)
        self._from_tamm_repl = from_tamm_repl
        self._other_pattern = _re.compile(other_pattern)
        self._to_tamm_repl = to_tamm_repl

    def is_tamm_key(self, key: str) -> bool:
        return self._tamm_pattern.search(key) is not None

    def is_other_key(self, key: str) -> bool:
        return self._other_pattern.search(key) is not None

    def _convert_from_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        return {
            self._tamm_pattern.sub(self._from_tamm_repl, key): val
            for key, val in state_dict.items()
            if self.is_tamm_key(key)
        }

    def _convert_to_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        return {
            self._other_pattern.sub(self._to_tamm_repl, key): val
            for key, val in state_dict.items()
            if self.is_other_key(key)
        }


class IdentityConverter(StateDictConverter):
    """
    A converter that passes through state dicts unchanged.  The :func:`is_tamm_key`
    and :func:`is_other_key` methods recognize a configurable set of keys, which
    makes this converter useful sometimes as part of a :class:`.UnionConverter`.

    Args:
        keys (:obj:`list` of :obj:`str`): The keys to recognize in
            :func:`is_tamm_key` and :func:`is_other_key`.
    """

    def __init__(self, keys: _List[str]):
        self._keys = set(keys)

    def is_tamm_key(self, key: str) -> bool:
        return key in self._keys

    def is_other_key(self, key: str) -> bool:
        return key in self._keys

    def _convert_from_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        return state_dict

    def _convert_to_tamm_impl(self, state_dict: _StateDictType) -> _StateDictType:
        return state_dict
