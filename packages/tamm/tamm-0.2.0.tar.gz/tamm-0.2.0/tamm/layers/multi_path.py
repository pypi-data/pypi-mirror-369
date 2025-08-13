"""
layers.multi_path
^^^^^^^^^^^^^^^^^

This module implements a configurable :class:`.MultiPath` layer for implementing
multiple branches within an architecture.

.. autoclass:: tamm.layers.MultiPath
    :members:
    :exclude-members: forward, Builder

.. autoclass:: tamm.layers.multi_path.MultiPathDispatchOption
    :members:

.. autoclass:: tamm.layers.multi_path.MultiPathCombineOption
    :members:
"""

import enum as _enum
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch

from tamm import _helpers
from tamm.layers import common as _layers_common
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder


class MultiPathDispatchOption(str, _enum.Enum):
    """
    An :obj:`Enum` for controlling the dispatch behavior during
    :meth:`.MultiPath.forward`.
    """

    SHARE = "SHARE"
    """
    Each path receives the same input, which is the input to
    :meth:`.MultiPath.forward`.
    """

    ARGS = "ARGS"
    """
    The :meth:`.MultiPath.forward` input is multiple positional args,
    and each path receives one arg based on the ordering of paths.
    """

    TUPLE = "TUPLE"
    """
    The :meth:`.MultiPath.forward` input is a :obj:`tuple`, and each path receives
    one element of the :obj:`tuple`.
    """

    DICT = "DICT"
    """
    The :meth:`.MultiPath.forward` input is a :obj:`dict` that maps each path name
    to the input for each path.
    """


class MultiPathCombineOption(str, _enum.Enum):
    """
    An :obj:`Enum` for controlling the combine behavior during
    :meth:`.MultiPath.forward`.
    """

    TUPLE = "TUPLE"
    """Return a :obj:`tuple` that contains the path outputs in the order of paths."""

    DICT = "DICT"
    """Return a :obj:`dict` that maps path names to the output of each path."""


class MultiPath(_torch.nn.Module, _layers_common.LayerMixin):
    """
    A layer for composing multiple branches (paths) within a model.

    The inputs are first dispatched to each path.  The dispatching behavior is
    configurable via the ``dispatch`` option.  Each path then separately
    computes its output.  Finally, the layer combines the path outputs into the
    layer's output.  The combine behavior is also configurable via the ``combine``
    option.

    Args:
        named_layers (:obj:`dict`): A dictionary that maps :obj:`str` path names to
            :obj:`LayerBuilder`, :obj:`nn.Module`, or ``None`` objects.  A value
            of ``None`` specifies the identify function for a path. The size of the
            :obj:`dict` is the number of paths.  The :obj:`dict` cannot contain
            the keys ``"dispatch"`` or ``"combine"``.
        dispatch (:obj:`str` or :obj:`.LayerBuilder`): Option to configure the
            dispatch behavior.  If a :obj:`str`, the value should correspond
            to a member of :obj:`.MultiPathDispatchOption`.  The argument defaults
            to ``"share"``, in which case each path shares the same input.  If
            a :obj:`.LayerBuilder`, the ``dispatch`` layer is responsible for
            mapping the parent layer's input to a :obj:`tuple` of inputs for each
            path.
        combine (:obj:`str` or :obj:`.LayerBuilder`): Option to configure the
            combine behavior.  If a :obj:`str`, the value should correspond
            to a member of :obj:`.MultiPathCombineOption`.  The argument defaults
            to ``"tuple"``, in which case the layer returns a :obj:`tuple` of
            outputs from each path.  If a :obj:`.LayerBuilder`, the ``combine``
            layer is responsible for mapping a :obj:`tuple` of path outputs to
            the parent layer's return value.

    Example:

        .. code-block:: python

            from tamm import layers
            import torch

            layer = layers.MultiPath(
                {
                    "mul2": layers.MultiplyByScale(constant_scale=2),
                    "mul4": layers.MultiplyByScale(constant_scale=4),
                    "identity": None,
                },
                combine="dict",
            )
            x = torch.tensor(3)
            y = layer(x)  # {'mul2': tensor(6), 'mul4': tensor(12), 'identity': tensor(3)}
    """

    def __init__(
        self,
        named_layers,
        *,
        dispatch: _Union[str, MultiPathDispatchOption, _ModuleOrBuilder] = "share",
        combine: _Union[str, MultiPathCombineOption, _ModuleOrBuilder] = "tuple",
    ):
        super().__init__()
        if "dispatch" in named_layers:
            raise ValueError("named_layers cannot contain the key 'dispatch'")
        if "combine" in named_layers:
            raise ValueError("named_layers cannot contain the key 'combine'")

        if isinstance(dispatch, str):
            self.dispatch = _helpers.get_enum_member_from_name(
                MultiPathDispatchOption, dispatch
            )
        else:
            self.dispatch = _helpers.maybe_build_module(dispatch)

        _helpers.append_children(self, **named_layers, register_none_children=True)
        self._path_names = list(named_layers)

        if isinstance(combine, str):
            self.combine = _helpers.get_enum_member_from_name(
                MultiPathCombineOption, combine
            )
        else:
            self.combine = _helpers.maybe_build_module(combine)

    @property
    def num_paths(self) -> int:
        """The number of paths in the layer."""
        return len(self._path_names)

    @property
    def path_names(self) -> _Tuple[str, ...]:
        """A :obj:`tuple` containing the layer's path names."""
        return tuple(self._path_names)

    @property
    def paths(self) -> _Tuple[_Union[_torch.nn.Module, None], ...]:
        """
        A :obj:`tuple` containing the paths.  Each path is either a
        :obj:`nn.Module` or ``None``.
        """
        return tuple(getattr(self, name) for name in self._path_names)

    @property
    def named_paths(self) -> _Dict[str, _Union[_torch.nn.Module, None]]:
        """A :obj:`dict` that maps path names to paths."""
        return {name: getattr(self, name) for name in self._path_names}

    def extra_repr(self) -> str:
        pieces = []
        if isinstance(self.dispatch, MultiPathDispatchOption):
            pieces.append(f"dispatch={self.dispatch.value}")
        if isinstance(self.combine, MultiPathCombineOption):
            pieces.append(f"combine={self.combine.value}")
        return ", ".join(pieces)

    def forward(self, *args) -> _Any:  # pylint: disable=redefined-builtin
        inputs = self._dispatch_input(*args)
        if len(inputs) != self.num_paths:
            raise ValueError(
                f"MultiPath layer received {len(inputs)} inputs for {self.num_paths} paths"
            )
        outputs = tuple(
            path(x) if path is not None else x for path, x in zip(self.paths, inputs)
        )
        return self._combine_outputs(outputs)

    # pylint: disable-next=redefined-builtin
    def _dispatch_input(self, *args) -> _Tuple[_Any, ...]:
        if self.dispatch is MultiPathDispatchOption.ARGS:
            return tuple(args)

        if len(args) != 1:
            raise ValueError(
                "MultiPath.forward() expects 1 argument (except when in ARGS "
                f"mode) but received {len(args)}"
            )
        arg = args[0]

        if self.dispatch is MultiPathDispatchOption.SHARE:
            return (arg,) * self.num_paths

        if self.dispatch is MultiPathDispatchOption.TUPLE:
            if not isinstance(arg, (tuple, list)):
                raise ValueError(f"Expected tuple input but received {repr(arg)}")
            return tuple(arg)

        if self.dispatch is MultiPathDispatchOption.DICT:
            if not isinstance(arg, dict):
                raise ValueError(f"Expected dict input but received {repr(arg)}")
            return tuple(arg[key] for key in self.path_names)

        if isinstance(self.dispatch, _torch.nn.Module):
            return tuple(self.dispatch(arg))

        raise ValueError(f"dispatch mode {repr(self.dispatch)} not recognized")

    # pylint: disable-next=redefined-builtin
    def _combine_outputs(self, outputs: _Tuple[_Any, ...]) -> _Any:
        if len(outputs) != self.num_paths:
            raise ValueError(
                f"MultiPath layer has {len(outputs)} for {self.num_paths} paths"
            )

        if self.combine is MultiPathCombineOption.TUPLE:
            return outputs

        if self.combine is MultiPathCombineOption.DICT:
            return dict(zip(self.path_names, outputs))

        if isinstance(self.combine, _torch.nn.Module):
            return self.combine(outputs)

        raise ValueError(f"combine mode {self.combine} not recognized")
