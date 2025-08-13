"""
layers.basic
^^^^^^^^^^^^

This submodule contains simple miscellaneous layers.

.. autoclass:: tamm.layers.ChannelsFirstToLast
    :show-inheritance:

.. autoclass:: tamm.layers.ChannelsLastToFirst
    :show-inheritance:

.. autoclass:: tamm.layers.ExpandDim

.. autoclass:: tamm.layers.Flatten

.. autoclass:: tamm.layers.Index
    :show-inheritance:

.. autoclass:: tamm.layers.Interpolation
    :show-inheritance:
    :members: forward

.. autoclass:: tamm.layers.InversePermute

.. autoclass:: tamm.layers.Mean
    :show-inheritance:

.. autoclass:: tamm.layers.MoveDim

.. autoclass:: tamm.layers.MultiplyByScale
    :members: forward

.. autoclass:: tamm.layers.Permute

.. autoclass:: tamm.layers.SelectByKey
    :show-inheritance:
    :members: forward

.. autoclass:: tamm.layers.SoftCap
    :members: forward

.. autoclass:: tamm.layers.Transpose

.. autoclass:: tamm.layers.Unflatten

.. autoclass:: tamm.layers.Union
    :show-inheritance:
"""

from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

from tamm import _helpers, _warnings
from tamm.layers import activation as _activation
from tamm.layers import functional as _tamm_F
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class MoveDim(_nn.Module, _LayerMixin):
    """
    A layer that swaps two dimensions of an input using :func:`torch.movedim`.

    Args:
        source (:obj:`int` or :obj:`tuple` of :obj:`int`): Original positions
            of the dimensions to move.
        destination (:obj:`int` or :obj:`tuple` of :obj:`int`): Corresponding
            destinations of the positions.
    """

    def __init__(
        self,
        source: _Union[int, _Tuple[int, ...]],
        destination: _Union[int, _Tuple[int, ...]],
    ):
        super().__init__()
        self.source = source
        self.destination = destination

    def extra_repr(self):
        return f"{self.source}, {self.destination}"

    def forward(self, tensor: _torch.Tensor) -> _torch.Tensor:
        return tensor.movedim(self.source, self.destination)


class Transpose(_nn.Module, _LayerMixin):
    """
    A layer that swaps two dimensions of an input using :func:`torch.transpose`.

    Args:
        dim0 (:obj:`int`): The first dimension to transpose.
        dim1 (:obj:`int`): The second dimension to transpose.
    """

    def __init__(self, dim0: int, dim1: int):
        super().__init__()
        self.dim0 = dim0
        self.dim1 = dim1

    def extra_repr(self):
        return f"{self.dim0}, {self.dim1}"

    def forward(self, tensor: _torch.Tensor) -> _torch.Tensor:
        return tensor.transpose(self.dim0, self.dim1)


class Permute(_nn.Module, _LayerMixin):
    """
    A layer that permutes dimensions of an input using :func:`torch.permute`.

    Args:
        dims (:obj:`tuple` of :obj:`int`): The updated ordering of dimensions.
    """

    def __init__(self, dims: _Tuple[int, ...]):
        super().__init__()
        self.dims = tuple(dims)

    def extra_repr(self):
        return ", ".join([str(d) for d in self.dims])

    def forward(self, tensor: _torch.Tensor) -> _torch.Tensor:
        return tensor.permute(self.dims)


class InversePermute(_nn.Module, _LayerMixin):
    """
    A layer that performs the inverse of a :obj:`.Permute` layer.

    Args:
        permute_dims (:obj:`tuple` of :obj:`int`): The dims used for
            a permutation.  This layer's forward pass restores a
            permuted tensor's dimensions to their original ordering.
    """

    def __init__(self, permute_dims: _Tuple[int, ...]):
        super().__init__()
        self.permute_dims = tuple(permute_dims)

    def extra_repr(self):
        return f"permute_dims={self.permute_dims}"

    def forward(self, tensor: _torch.Tensor) -> _torch.Tensor:
        return _tamm_F.inverse_permute(tensor, self.permute_dims)


class ChannelsFirstToLast(_nn.Module, _LayerMixin):
    """
    A layer that converts channels-first tensors with shape
    ``(batch_size, num_channels, *spatial_dims)`` to tensors with shape
    ``(batch_size, *spatial_dims, num_channels)``.

    Args:
        flatten_spatial_dims (:obj:`bool`): A flag for flattening the spatial dimensions
            into a single dimension when ``True``.  Defaults to ``False``.
    """

    def __init__(self, flatten_spatial_dims: bool = False):
        super().__init__()
        self.flatten_spatial_dims = flatten_spatial_dims

    def extra_repr(self):
        return f"flatten_spatial_dims={self.flatten_spatial_dims}"

    def forward(self, tensor: _torch.Tensor) -> _torch.Tensor:
        if self.flatten_spatial_dims:
            tensor = tensor.flatten(start_dim=2)
        return tensor.movedim(1, -1)


class ChannelsLastToFirst(_nn.Module, _LayerMixin):
    """
    A layer that converts channels-last tensors with shape
    ``(batch_size, *spatial_dims, num_channels)`` to tensors with shape
    ``(batch_size, num_channels, *spatial_dims)``.
    """

    def __init__(self):
        super().__init__()

    def forward(self, tensor: _torch.Tensor) -> _torch.Tensor:
        return tensor.movedim(-1, 1)


class Flatten(_nn.Module, _LayerMixin):
    """
    A layer that flattens dimensions of a tensor using :func:`torch.flatten`.

    Args:
        start_dim (:obj:`int`): The first dimension to flatten.
        end_dim (:obj:`int`): The last dimension to flatten.
    """

    def __init__(self, start_dim: int = 0, end_dim: int = -1):
        super().__init__()
        self.start_dim = start_dim
        self.end_dim = end_dim

    def extra_repr(self):
        pieces = []
        if self.start_dim != 0:
            pieces.append(f"start_dim={self.start_dim}")
        if self.end_dim != -1:
            pieces.append(f"end_dim={self.end_dim}")
        return ", ".join(pieces)

    def forward(self, tensor: _torch.Tensor) -> _torch.Tensor:
        return tensor.flatten(start_dim=self.start_dim, end_dim=self.end_dim)


class ExpandDim(_nn.Module, _LayerMixin):
    """
    A layer for repeating a tensor along a specific dimension using
    :meth:`torch.Tensor.expand` (which does not copy the underlying data).

    Args:
        repeat (:obj:`int`): The expansion factor.
        dim (:obj:`int`, optional): The dimension to expand.  Defaults to ``-1``.
        unsqueeze (:obj:`bool`, optional): A flag for inserting a new dimension
            using :func:`torch.unsqueeze` before the expansion.  Defaults to ``False``.
        interleave (:obj:`bool`, optional): A flag for interleaving the expanded values,
            similar to :func:`torch.repeat_interleave`.  Defaults to ``False``.
    """

    def __init__(
        self,
        repeat: int,
        *,
        dim: int = -1,
        unsqueeze: bool = False,
        interleave: bool = False,
    ):
        super().__init__()
        self.repeat = repeat
        self.dim = dim
        self.unsqueeze = unsqueeze
        self.interleave = interleave

    def forward(self, tensor: _torch.Tensor) -> _torch.Tensor:
        return _tamm_F.expand_dim(
            tensor,
            repeat=self.repeat,
            dim=self.dim,
            unsqueeze=self.unsqueeze,
            interleave=self.interleave,
        )

    def extra_repr(self):
        pieces = [f"repeat={self.repeat}", f"dim={self.dim}"]
        if self.unsqueeze:
            pieces.append("unsqueeze=True")
        if self.interleave:
            pieces.append("interleave=True")
        return ", ".join(pieces)


class Index(_nn.Module, _LayerMixin):
    """
    A layer for indexing tensors with predetermined indices, slices, etc.

    Args:
        expressions: A sequence of expressions for indexing inputs to the layer with the
            ``[]`` operator.  This can include slices, integers, lists of integers,
            ``None``, ``...``, etc.

    Example:

        .. code-block:: python

            layer = Index(slice(1, None), ..., -1, None)
            out = layer(tensor)   # equivalent to out = tensor[1:, ..., -1, None]
    """

    def __init__(self, *expressions):
        super().__init__()
        self.expressions = expressions

    def extra_repr(self):
        pieces = [_helpers.maybe_slice_to_string(expr) for expr in self.expressions]
        return ", ".join(pieces)

    def forward(self, x: _torch.Tensor) -> _torch.Tensor:
        return x[self.expressions]


class Interpolation(_nn.Module, _LayerMixin):
    """
    A layer for resizing spatial tensors using :func:`torch.nn.functional.interpolate`.
    The layer expects inputs in channels-first format.

    Args:
        mode (:obj:`str`): The interpolation mode, such as ``"nearest"`` or
            ``"bicubic"``.  In addition to the options provided by
            :func:`torch.nn.functional.interpolate`, this layer also supports
            ``"pillow-style-bilinear"`` and ``"pillow-style-bicubic"``, which match the
            behavior of Pillow (the ``recompute_scale_factor`` and ``antialias`` options
            are ignored in these cases).
        cast_dtype (:obj:`torch.dtype`, optional): The dtype to perform the
            interpolation in.  Set to ``None`` to use the input dtype.  Defaults to
            ``float32``.

    Please see :func:`torch.nn.functional.interpolate` for descriptions of the remaining
    options.
    """

    PILLOW_BICUBIC = "pillow-style-bicubic"
    PILLOW_BILINEAR = "pillow-style-bilinear"

    def __init__(
        self,
        mode: str = "nearest",
        size: _Union[_Tuple[int, ...], int, None] = None,
        scale_factor: _Union[_Tuple[float, ...], float, None] = None,
        align_corners: _Union[bool, None] = None,
        recompute_scale_factor: _Union[bool, None] = None,
        antialias: bool = False,
        cast_dtype: _Union[_torch.dtype] = _torch.float32,
    ):
        super().__init__()
        self.mode = mode
        self.size = size
        self.scale_factor = scale_factor
        self.align_corners = align_corners
        self.recompute_scale_factor = recompute_scale_factor
        self.antialias = antialias
        self.cast_dtype = cast_dtype

    @property
    def _options(self):
        return {
            "mode": self.mode,
            "size": self.size,
            "scale_factor": self.scale_factor,
            "align_corners": self.align_corners,
            "recompute_scale_factor": self.recompute_scale_factor,
            "antialias": self.antialias,
        }

    @property
    def _interpolate_kwargs(self):
        kwargs = self._options
        mode = kwargs["mode"]
        if mode in (self.PILLOW_BICUBIC, self.PILLOW_BILINEAR):
            kwargs["antialias"] = True
            kwargs["align_corners"] = False
            if mode == self.PILLOW_BILINEAR:
                kwargs["mode"] = "bilinear"
            elif mode == self.PILLOW_BICUBIC:
                kwargs["mode"] = "bicubic"
            else:
                raise RuntimeError(f"Pillow-style mode '{mode}' not recognized")
        return kwargs

    def extra_repr(self):
        options = self._options
        if not options["antialias"]:
            options.pop("antialias")
        if self.mode in (self.PILLOW_BICUBIC, self.PILLOW_BILINEAR):
            options.pop("antialias", None)  # these are ignored in this case
            options.pop("align_corners")
        strings = [
            f"{key}={repr(val)}" for key, val in options.items() if val is not None
        ]
        return ", ".join(strings)

    def forward(
        self,
        inputs: _torch.Tensor,
        size: _Union[_Tuple[int, ...], int, None] = None,
        scale_factor: _Union[_Tuple[float, ...], float, None] = None,
    ) -> _torch.Tensor:
        """
        Args:
            inputs (:obj:`torch.Tensor`): The input tensor to interpolate.  This must
                have shape ``(batch_size, dim, *spatial_shape)``.
            size (:obj:`tuple` of :obj:`int`, optional): The spatial shape of the
                output tensor.  Defaults to ``None``.
            scale_factor (:obj:`tuple` of :obj:`float`, optional): The spatial shape of
                the output tensor relative to that of ``inputs``.  Defaults to ``None``.

        .. note::
            If both ``size`` and ``scale_factor`` are ``None``, then these arguments
            default to the layer's ``size`` and ``scale_factor`` attributes.

        Returns:
            An interpolation of ``inputs``.
        """

        input_dtype = inputs.dtype
        if self.cast_dtype is not None:
            inputs = inputs.type(self.cast_dtype)

        kwargs = self._interpolate_kwargs
        if size is not None or scale_factor is not None:
            kwargs["size"] = size
            kwargs["scale_factor"] = scale_factor

        with _helpers.autocast_disabled(inputs.device):
            return _torch.nn.functional.interpolate(inputs, **kwargs).type(input_dtype)


class Map(_nn.Module, _LayerMixin):
    """
    A layer that applies a child layer separately to every tensor in the layer's inputs.

    Args:
        func:  A :obj:`.LayerBuilder` or :obj:`nn.Module` that specifies the mapping
            function.

    Example:

        .. code-block:: python

            func = tamm.layers.Lambda(lambda x: x + 10)
            layer = Map(func)

            x = {"a": torch.tensor(1.0), "b": torch.tensor(-1.0)}
            y = layer(x)  # {'a': tensor(11.), 'b': tensor(9.)}
            z = layer(list(y.values()))  # [tensor(21.), tensor(19.)]
    """

    def __init__(self, func: _OptionalModuleOrBuilder):
        super().__init__()
        _helpers.append_children(self, func=func)

    def forward(self, inputs: _Any) -> _Dict[str, _Any]:
        from torch.utils import _pytree  # pylint: disable=import-outside-toplevel

        return _pytree.tree_map_only(_torch.Tensor, self.func, inputs)


class Mean(_nn.Module, _LayerMixin):
    """
    A layer that applies :func:`torch.mean` to its inputs.

    Args:
        dim (:obj:`int` or :obj:`tuple`, optional): The ``dim`` arg for
            :func:`torch.mean`.  By default, the mean is across the last dimension
            (``-1``).
        keepdim (:obj:`bool`, optional): The ``keepdim`` arg for
            :func:`torch.mean`.  Defaults to ``False``.
    """

    def __init__(self, dim=-1, keepdim=False):
        super().__init__()
        self.dim = dim
        self.keepdim = keepdim

    def forward(self, x):
        return _torch.mean(x, dim=self.dim, keepdim=self.keepdim)

    def extra_repr(self):
        return f"dim={self.dim}, keepdim={self.keepdim}"


class MultiplyByScale(_nn.Module, _LayerMixin):
    """
    A layer that multiplies its input by learnable scale values and/or an
    optional constant scalar.

    Args:
        weight_shape (:obj:`tuple` of :obj:`int`, optional): The shape of the
            learnable weight parameter.  This shape must broadcast with the layer's
            inputs. Defaults to ``None``, which results in no learnable parameter.
        weight_activation (:obj:`str` or other arg for \
            :func:`.create_activation_layer`, optional): Optional specification
            of a weight activation layer, which is helpful for ensuring that the
            weight remains a positive value.  If provided, the layer passes its
            weight through this activation layer prior to scaling the inputs.
        constant_scale (:obj:`float`, optional): An optional constant
            value for scaling the layer's inputs.
    """

    def __init__(
        self,
        *,
        weight_shape: _Tuple[int, ...] = None,
        weight_activation: _activation.ActivationSpecType = None,
        constant_scale: _Optional[float] = None,
        device=None,
        dtype=None,
    ):
        super().__init__()
        if weight_shape is not None:
            self.weight_shape = tuple(weight_shape)
            self.weight = _torch.nn.Parameter(
                _torch.ones(weight_shape, device=device, dtype=dtype)
            )
        else:
            self.weight_shape = self.weight = None
        self.constant_scale = constant_scale
        self.weight_activation = _activation.create_activation_layer(weight_activation)

    def extra_repr(self):
        pieces = []
        if self.weight_shape is not None:
            pieces.append(f"weight_shape={self.weight_shape}")
        if self.constant_scale is not None:
            pieces.append(f"constant_scale={self.constant_scale}")
        return ", ".join(pieces)

    def forward(self, tensor: _torch.Tensor) -> _torch.Tensor:
        """
        Args:
            tensor (:obj:`torch.Tensor`): The tensor input.

        Returns:
            The product of ``tensor``, the layer's weight (if not ``None``),
            and the constant scale (if not ``None``).
        """
        if self.weight is None:
            if self.constant_scale is None:
                return tensor
            return tensor * self.constant_scale

        weight = self.weight
        if self.weight_activation is not None:
            weight = self.weight_activation(weight)
        if self.constant_scale is not None:
            weight = self.constant_scale * weight

        return tensor * weight


class Sum(_nn.Module, _LayerMixin):
    """
    A layer that applies :func:`torch.sum` to its inputs.

    Args:
        dim (int): Dimension to sum across.
    """

    def __init__(self, dim=-1, keepdim=False):
        super().__init__()
        self.dim = dim
        self.keepdim = keepdim

    def forward(self, x):
        return _torch.sum(x, dim=self.dim, keepdim=self.keepdim)

    def extra_repr(self):
        return f"dim={self.dim}, keepdim={self.keepdim}"


class SelectByKey(_nn.Module, _LayerMixin):
    """
    A layer that returns a specific value from an input :obj:`dict`.

    Args:
        key: A dictionary key.
    """

    def __init__(self, key: _Any):
        super().__init__()
        self.key = key

    def extra_repr(self):
        return repr(self.key)

    def forward(self, inputs: _Dict[_Any, _Any]) -> _Any:
        """
        Args:
            inputs (:obj:`dict`): A dictionary that contains ``key`` as a key.

        Returns:
            The value ``inputs[key]``.

        Raises:
            KeyError: If ``inputs`` does not contain the key.
        """
        return inputs[self.key]


class SoftCap(_nn.Module, _LayerMixin):
    """
    Computes ``cap * tanh(x / cap)``, which is a smooth and differentiable way
    to cap the values of a tensor.

    Args:
        cap (:obj:`float`): The value to cap inputs to.
    """

    def __init__(self, cap: float):
        super().__init__()
        self.cap = cap

    def extra_repr(self):
        return f"cap={self.cap}"

    def forward(self, tensor: _torch.Tensor) -> _torch.Tensor:
        return _tamm_F.soft_cap(tensor, cap=self.cap)


class Unflatten(_nn.Module, _LayerMixin):
    """
    A layer that unflattens dimensions of a tensor using :func:`torch.unflatten`.

    Args:
        dim (:obj:`int`): The dimension to unflatten.
        sizes (:obj:`tuple` of :obj:`int`): The new shape of the unflattened
            dimension.
    """

    def __init__(self, dim: int, sizes: _Tuple[int, ...]):
        super().__init__()
        self.dim = dim
        self.sizes = tuple(sizes)

    def extra_repr(self):
        return f"dim={self.dim}, sizes={self.sizes}"

    def forward(self, tensor: _torch.Tensor) -> _torch.Tensor:
        return tensor.unflatten(self.dim, self.sizes)


@_warnings.deprecate("tamm.layers.MultiPath")
class Union(_nn.Module, _LayerMixin):
    """
    A layer for composing child layers that take the same inputs and produce different
    outputs.  The layer returns a :obj:`dict` that maps the name of each child layer
    to its output.

    .. warning::
        :class:`Union` is deprecated.  Please instead use :class:`.MultiPath` with
        ``combine="dict"``.

    Args:
        named_layers (:obj:`dict`): A dictionary that maps the name of each segmentation
            layer to a :obj:`.LayerBuilder` or :obj:`nn.Module`.
    """

    def __init__(self, named_layers: _Dict[str, _OptionalModuleOrBuilder]):
        super().__init__()
        _helpers.append_children(self, **named_layers)

    def forward(self, inputs: _Any) -> _Dict[str, _Any]:
        return {name: child(inputs) for name, child in self.named_children()}


class PadToMultiple(_nn.Module, _LayerMixin):
    """
    A layer that pads the specified dimension(s) of a tensor with a given value so that its size becomes
    a multiple of a specified number. The padding is applied to the end (right side) of the specified dimensions.

    Args:
        multiple (:obj:`int`): The number to which the specified dimension(s) should be a multiple of.
        dim (:obj: `Union[int, Tuple[int, ...]]`): The dimension(s) to pad. Defaults to ``-1``.
        pad_value (:obj: `float`): The value to use for padding. Defaults to ``0``.


    Example:
        >>> layer = PadToMultiple(multiple=3, dim=(-2, -1), pad_value=0)
        >>> x = torch.randn(1, 3, 14, 14)
        >>> y = layer(x)
        >>> print(y.shape)  # Output shape will be (1, 3, 15, 15) since 15 is the next multiple of 3
    """

    def __init__(
        self,
        multiple: int,
        *,
        dim: _Union[int, _Tuple[int, ...]] = -1,
        pad_value: float = 0,
    ):
        super().__init__()
        self.multiple = multiple
        self.dim = dim if isinstance(dim, tuple) else (dim,)
        self.pad_value = pad_value

    def extra_repr(self):
        return f"multiple={self.multiple}, dim={self.dim}, pad_value={self.pad_value}"

    def forward(self, x: _torch.Tensor) -> _torch.Tensor:
        pad = []

        normalized_dims = set(dim % x.ndim for dim in self.dim)
        min_dim = min(normalized_dims)

        any_pad = False
        # Ensure we pad in reversed order when multiple dims are given since nn.functional.pad applies in reverse order
        for d in reversed(range(min_dim, x.ndim)):
            if d in normalized_dims:
                pad_num = (-x.size(d)) % self.multiple
            else:
                pad_num = 0

            if pad_num > 0:
                pad.extend([0, pad_num])  # Right padding
                any_pad = True
            else:
                pad.extend([0, 0])

        if any_pad:
            x = _nn.functional.pad(x, pad, value=self.pad_value)

        return x
