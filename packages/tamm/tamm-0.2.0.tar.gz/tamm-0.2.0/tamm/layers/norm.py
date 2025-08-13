"""
layers.norm
-----------

This module provides norm layers and a factory function for creating norm layers.

.. autoclass:: tamm.layers.BatchNorm

.. autoclass:: tamm.layers.CausalGroupNorm

.. autoclass:: tamm.layers.LayerNorm

.. autoclass:: tamm.layers.RMSNorm

.. autofunction:: tamm.layers.norm.create_norm_builder

.. autofunction:: tamm.layers.norm.create_vectorized_norm_builder
"""

import abc as _abc
import contextlib as _contextlib
from typing import Iterable as _Iterable
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
from torch import nn as _nn
from torch.nn.modules.batchnorm import _BatchNorm as _PyTorchBatchNorm

from tamm import _helpers
from tamm.layers import functional as _tamm_F
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.functional import NormScaleMode
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class _BaseNorm(_nn.Module, _abc.ABC):
    """
    A Base class for norm layers.

    Args:
        features_shape (:obj:`tuple` of :obj:`int`, optional): The shape of the
            feature (channel) dimension(s).  Set to ``None`` to omit the weight
            (scale) parameter.
        bias (:obj:`bool`): A flag for including a bias parameter.  Defaults to
            ``False``.  If ``True``, the bias parameter takes the same shape as
            the ``weight`` parameter.
        dim (:obj:`int` or :obj:`tuple` of :obj:`int`, optional): The feature
            dimension index (or indices) to scale using the ``weight`` parameter.
            Defaults to the last ``len(features_shape)`` dimensions (or ``-1``
            if ``features_shape`` is `` None``), corresponding to channels-last
            inputs.  Use ``1`` for channels-first inputs or use a tuple for multiple
            channel dimensions.
        cast_dtype (:obj:`torch.dtype, optional): An optional dtype for the norm
            computation.  If not ``None``, the layer casts inputs to this dtype
            before normalization and casts outputs to the input dtype.  Defaults
            to ``torch.float32``.
        eps (:obj:`float`): The epsilon parameter for preventing division by zero.
            Defaults to ``1e-5``.
        device: The device of the parameters.
        dtype: The dtype of the parameters.
    """

    def __init__(
        self,
        features_shape: _Optional[_Iterable[int]] = None,
        *,
        bias: bool = False,
        dim: _Optional[_Union[int, _Iterable[int]]] = None,
        cast_dtype: _Optional[_torch.dtype] = _torch.float32,
        eps: float = 1e-5,
        device=None,
        dtype=None,
    ):
        _nn.Module.__init__(self)

        if features_shape is not None:
            features_shape = tuple(features_shape)
        self._features_shape = features_shape

        if dim is None:
            if features_shape is None or len(features_shape) == 1:
                dim = -1
            else:
                dim = tuple(range(-len(features_shape), 0))
        if not isinstance(dim, int):
            dim = tuple(dim)
        self.dim = dim

        self.cast_dtype = cast_dtype
        self.eps = eps

        if self._features_shape is not None:
            self.weight = _nn.Parameter(
                _torch.empty(self._features_shape, device=device, dtype=dtype)
            )
        else:
            self.weight = None

        if bias:
            self.bias = _nn.Parameter(
                _torch.empty(self._features_shape, device=device, dtype=dtype)
            )
        else:
            self.bias = None

        self.reset_parameters()

    def reset_parameters(self) -> None:
        if self.weight is not None:
            _nn.init.ones_(self.weight)
        if self.bias is not None:
            _nn.init.zeros_(self.bias)

    @property
    def _ndim(self):
        if isinstance(self.dim, int):
            return 1
        return len(self.dim)

    def _permute(
        self, x: _torch.Tensor
    ) -> _Tuple[_torch.Tensor, _Optional[_List[int]]]:
        """
        Permutes the normalization dimensions to the last dimensions.
        Returns a tuple with the permuted tensors and a list of indices
        which indicate how the permutation was performed. Returns ``None``
        as the second value if ``self.dim`` is an integer.
        """
        if isinstance(self.dim, int):
            if self.dim % x.ndim != x.ndim - 1:
                x = x.movedim(self.dim, -1)
            return x, None

        dims = {d % x.ndim: True for d in self.dim}
        perm = [d for d in range(x.ndim) if d not in dims]
        perm.extend(dims)
        return _torch.permute(x, perm), perm

    def _unpermute(
        self, x: _torch.Tensor, perm: _Optional[_Iterable[int]] = None
    ) -> _torch.Tensor:
        if perm is not None:
            return _tamm_F.inverse_permute(x, perm)
        if self.dim == -1:
            return x
        return x.movedim(-1, self.dim)

    @_abc.abstractmethod
    def _forward_impl(self, x: _torch.Tensor) -> _torch.Tensor:
        """
        Normalize x assuming the features dimension(s) of x is (are) the
        last dimension(s)."""

    # pylint: disable=redefined-builtin
    def forward(self, input: _torch.Tensor) -> _torch.Tensor:
        input_dtype = input.dtype

        if self.cast_dtype is not None:
            input = input.type(self.cast_dtype)
            context = _helpers.autocast_disabled(input.device)
        else:
            context = _contextlib.nullcontext()

        with context:
            x, perm = self._permute(input)
            x = self._forward_impl(x)
            x = self._unpermute(x, perm)

        return x.type(input_dtype)

    def _get_extra_repr_substrings(self):
        if self._features_shape is not None:
            shape = tuple(self._features_shape)
        else:
            shape = None
        has_bias = self.bias is not None
        return [
            f"normalized_shape={shape}",
            f"bias={has_bias}",
            f"dim={self.dim}",
            f"cast_dtype={self.cast_dtype}",
            f"eps={self.eps}",
        ]

    def extra_repr(self) -> str:
        return ", ".join(self._get_extra_repr_substrings())


class LayerNorm(_BaseNorm, _LayerMixin):
    """
    LayerNorm layer.  This layer normalizes the input to have zero mean
    and unit variance (including an epsilon term) along the input's feature
    dimension(s).

    Args:
        normalized_shape (:obj:`tuple` of :obj:`int`, optional): The shape of the
            weight (scale) parameter.  Typically this is the expected input shape
            along the ``dim`` dimension(s).  Set to ``None`` to omit the weight.
        bias (:obj:`bool`): A flag for including a bias parameter.  Defaults to
            ``False``.  If ``True``, the bias parameter takes the same shape as
            the ``weight`` parameter.
        dim (:obj:`int` or :obj:`tuple` of :obj:`int`, optional): The feature
            dimension index (or indices) to compute the norm over. Defaults to the
            last ``len(normalized_shape)`` dimensions (or ``-1`` if
            ``normalized_shape`` is `` None``), corresponding to channels-last
            inputs.  Use ``1`` for channels-first inputs or use a tuple for multiple
            channel dimensions.
        cast_dtype (:obj:`torch.dtype, optional): An optional dtype for the norm
            computation.  If not ``None``, the layer casts inputs to this dtype
            before normalization and casts outputs to the input dtype.  Defaults
            to ``torch.float32``.
        eps (:obj:`float`): An epsilon parameter for preventing division by zero.
            Defaults to ``1e-5``.
        device: The device of the parameters.
        dtype: The dtype of the parameters.
    """

    def __init__(
        self,
        normalized_shape: _Iterable[int],
        *,
        bias: bool = False,
        dim: _Optional[_Union[int, _Iterable[int]]] = None,
        cast_dtype: _Optional[_torch.dtype] = _torch.float32,
        eps: float = 1e-5,
        device=None,
        dtype=None,
    ):
        super().__init__(
            features_shape=normalized_shape,
            bias=bias,
            dim=dim,
            cast_dtype=cast_dtype,
            eps=eps,
            device=device,
            dtype=dtype,
        )

    def _forward_impl(self, x: _torch.Tensor) -> _torch.Tensor:
        return _tamm_F.layer_norm(
            x,
            normalized_shape=x.shape[-self._ndim :],
            weight=self.weight,
            bias=self.bias,
            eps=self.eps,
            cast_dtype=None,  # cast_dtype handled by base layer class
        )


class RMSNorm(_BaseNorm, _LayerMixin):
    """
    RMSNorm layer.  This layer normalizes the input by the L2 norm (including an
    epsilon term) along the input's feature dimension(s).

    Args:
        normalized_shape (:obj:`tuple` of :obj:`int`, optional): The shape of the
            weight (scale) parameter.  Typically this is the expected input shape
            along the ``dim`` dimension(s).  Set to ``None`` to omit the weight.
        bias (:obj:`bool`): A flag for including a bias parameter.  Defaults to
            ``False``.  If ``True``, the bias parameter takes the same shape as
            the ``weight`` parameter.
        dim (:obj:`int` or :obj:`tuple` of :obj:`int`, optional): The feature
            dimension index (or indices) to compute the norm over. Defaults to the
            last ``len(normalized_shape)`` dimensions (or ``-1`` if
            ``normalized_shape`` is `` None``), corresponding to channels-last
            inputs.  Use ``1`` for channels-first inputs or use a tuple for multiple
            channel dimensions.
        cast_dtype (:obj:`torch.dtype, optional): An optional dtype for the norm
            computation.  If not ``None``, the layer casts inputs to this dtype
            before normalization and casts outputs to the input dtype.  Defaults
            to ``torch.float32``.
        eps (:obj:`float`): An epsilon parameter for preventing division by zero.
            Defaults to ``1e-5``.
        device: The device of the parameters.
        dtype: The dtype of the parameters.
    """

    def __init__(
        self,
        normalized_shape: _Optional[_Iterable[int]] = None,
        *,
        bias: bool = False,
        dim: _Optional[_Union[int, _Iterable[int]]] = None,
        cast_dtype: _Optional[_torch.dtype] = _torch.float32,
        eps: float = 1e-5,
        device=None,
        dtype=None,
    ):
        super().__init__(
            features_shape=normalized_shape,
            bias=bias,
            dim=dim,
            cast_dtype=cast_dtype,
            eps=eps,
            device=device,
            dtype=dtype,
        )

    def _forward_impl(self, x: _torch.Tensor) -> _torch.Tensor:
        x = _tamm_F.rms_norm(
            x,
            normalized_shape=x.shape[-self._ndim :],
            weight=self.weight,
            bias=self.bias,
            eps=self.eps,
            cast_dtype=None,  # cast_dtype handled by base layer class
        )
        return x


class CausalGroupNorm(_BaseNorm, _LayerMixin):
    """
    A group norm layer that also enforces causality along a sequence dimension.
    When computing means and variances for normalization, the layer averages
    the means and variances across the current and past elements of the sequence
    (but not future elements).

    Args:
        weight_shape (:obj:`tuple` of :obj:`int`, optional): The shape of the
            weight (scale) parameter.  Typically this is a tuple with the number
            of features as the single entry.  Set to ``None`` to omit the weight.
        num_groups (:obj:`int`): The number of groups to split features into
            for normalization.  This value must evenly divide the layer's inputs
            along dimension ``dim``.
        sequence_dim (:obj:`int`): The dimension along which to enforce causality.
        bias (:obj:`bool`): A flag for including a bias parameter.  Defaults to
            ``False``.  If ``True``, the bias parameter takes the same shape as
            the ``weight`` parameter.
        dim (:obj:`int` or :obj:`tuple` of :obj:`int`, optional): The feature
            dimension index to compute the norm over. Defaults to the
            last ``len(normalized_shape)`` dimensions (or ``-1`` if
            ``normalized_shape`` is `` None``), corresponding to channels-last
            inputs.  If a :obj:`tuple`, ``dim`` must be length 1 for this layer.
        cast_dtype (:obj:`torch.dtype, optional): An optional dtype for the norm
            computation.  If not ``None``, the layer casts inputs to this dtype
            before normalization and casts outputs to the input dtype.  Defaults
            to ``torch.float32``.
        eps (:obj:`float`): An epsilon parameter for preventing division by zero.
            Defaults to ``1e-5``.
        device: The device of the parameters.
        dtype: The dtype of the parameters.
    """

    def __init__(
        self,
        weight_shape: _Optional[_Iterable[int]] = None,
        *,
        num_groups: int,
        sequence_dim: int,
        bias: bool = False,
        dim: _Optional[_Union[int, _Iterable[int]]] = None,
        cast_dtype: _Optional[_torch.dtype] = _torch.float32,
        eps: float = 1e-5,
        device=None,
        dtype=None,
    ):
        if not isinstance(sequence_dim, int):
            raise RuntimeError(
                "CausalGroupNorm requires an integer sequence_dim but received "
                f"sequence_dim={sequence_dim}"
            )

        super().__init__(
            features_shape=weight_shape,
            bias=bias,
            dim=dim,
            cast_dtype=cast_dtype,
            eps=eps,
            device=device,
            dtype=dtype,
        )
        self.num_groups = num_groups
        self.sequence_dim = sequence_dim

        if not isinstance(self.dim, int):
            if len(self.dim) != 1:
                raise RuntimeError(
                    f"CausalGroupNorm supports only 1 dim but received dim={self.dim}"
                )
            self.dim = self.dim[0]

    def _permute(
        self, x: _torch.Tensor
    ) -> _Tuple[_torch.Tensor, _Optional[_List[int]]]:
        """
        Permutes x such that the second-to-last dim is the features dim
        and the last dim is the sequence dim.
        """
        final_dims = (self.dim % x.ndim, self.sequence_dim % x.ndim)
        if final_dims[0] == final_dims[1]:
            raise RuntimeError(
                "CausalGroupNorm does not support identical values for "
                "dim and sequence_dim, but both resolved to dimension "
                f"{final_dims[0]} for input with shape {x.shape}"
            )
        perm = [d for d in range(x.ndim) if d not in final_dims]
        perm.extend(final_dims)
        return _torch.permute(x, perm), perm

    def _forward_impl(self, x: _torch.Tensor) -> _torch.Tensor:
        # Shorthand for shape comments:
        # B: batch size
        # G: num groups
        # D: hidden dim
        # S: sequence len

        # input x has shape B, ..., D, S  (after _permute())

        # unflatten the features dim into groups:
        x = x.unflatten(-2, (self.num_groups, -1))  # B, ..., G, D/G, S

        reduction_dims = (*range(1, x.ndim - 3), -2)
        x_mean = x.mean(dim=reduction_dims, keepdims=True)  # B, ..., G, 1, S
        counts = _torch.arange(start=1, end=x.size(-1) + 1, device=x.device)  # S
        x_cummean = _tamm_F.cumsum(x_mean, dim=-1) / counts  # B, ..., G, 1, S

        x_var = ((x - x_cummean) ** 2).mean(
            dim=reduction_dims, keepdims=True
        )  # B, ..., G, 1, S
        x_cumvar = _tamm_F.cumsum(x_var, dim=-1) / counts  # B, ..., G, 1, S
        scale = _torch.rsqrt(x_cumvar + self.eps)

        x = x - x_cummean  # B, ..., G, D/G, S
        if self.weight is not None:
            weight = self.weight.unflatten(-1, (self.num_groups, -1, 1))  # G, D/G, 1
            x = x * (weight * scale)
        else:
            x = x * scale

        if self.bias is not None:
            bias = self.bias.unflatten(-1, (self.num_groups, -1, 1))  # G, D/G, 1
            x = x + bias

        x = x.flatten(start_dim=-3, end_dim=-2)  # B, ..., D, S
        return x

    def _get_extra_repr_substrings(self):
        result = super()._get_extra_repr_substrings()
        result.insert(1, f"num_groups={self.num_groups}")
        result.insert(2, f"sequence_dim={self.sequence_dim}")
        return result


class VectorizedRMSNorm(RMSNorm):
    def __init__(
        self,
        normalized_shape: _Iterable[int],
        vec_dim: int,
        vec_indx: int,
        *,
        dim: _Optional[_Union[int, _Iterable[int]]] = None,
        eps: float = 1e-5,
        bias: bool = False,
        scale_mode: _Union[str, NormScaleMode] = "post_scale",
        cast_dtype: _Optional[_torch.dtype] = _torch.float32,
        device=None,
        dtype=None,
    ):
        # TODO: actually vectorize this function
        new_shape = (vec_dim,) + tuple(normalized_shape)
        super(RMSNorm, self).__init__(
            features_shape=new_shape,
            bias=bias,
            dim=dim,
            cast_dtype=cast_dtype,
            eps=eps,
            device=device,
            dtype=dtype,
        )

        self.scale_mode = _helpers.get_enum_member_from_name(NormScaleMode, scale_mode)
        self.vec_dim = vec_dim
        self.vec_indx = vec_indx

    def _get_extra_repr_substrings(self):
        result = super()._get_extra_repr_substrings()
        result.insert(1, f"vectorized_dim={self.vec_indx}")
        if self.scale_mode is not NormScaleMode.POST_SCALE:
            result.insert(4, f"scale_mode={self.scale_mode.value}")
        return result

    # pylint: disable=redefined-builtin
    def forward(self, input: _torch.Tensor) -> _torch.Tensor:
        num_prefix_dims = input.dim() - len(self._features_shape) + 1
        base_shape = (1,) * num_prefix_dims + self._features_shape[1:]
        to_shape = (
            base_shape[: self.vec_indx]
            + (self.vec_dim,)
            + base_shape[self.vec_indx + 1 :]
        )
        return _tamm_F.batched_rms_norms(
            input,
            self._features_shape[1:],
            weight=self.weight.reshape(to_shape),
            bias=None if self.bias is None else self.bias.reshape(to_shape),
            eps=self.eps,
            scale_mode=self.scale_mode,
            cast_dtype=None,  # cast_dtype handled by base layer class
        )


class BatchNorm(_BaseNorm, _LayerMixin, _PyTorchBatchNorm):
    """BatchNorm."""

    # Inherit from _PyTorchBatchNorm to extend functionality.
    #
    # Specifically, torch uses isinstance(module, _PyTorchBatchNorm),
    # in FSDP MixedPrecision to exclude some layers from low-precision
    # computation.
    #
    # We want this to return True for our BatchNorm layer too,
    # to exclude it from low precision computation.

    def __init__(
        self,
        features_shape: _Iterable[int],
        *,
        momentum: float = 0.1,
        bias: bool = False,
        dim: _Optional[_Union[int, _Iterable[int]]] = None,
        cast_dtype: _Optional[_torch.dtype] = _torch.float32,
        eps: float = 1e-5,
        device=None,
        dtype=None,
    ):
        super().__init__(
            features_shape=features_shape,
            bias=bias,
            dim=dim,
            cast_dtype=cast_dtype,
            eps=eps,
            device=device,
            dtype=dtype,
        )
        self.momentum = momentum
        self.register_buffer("running_mean", _torch.zeros_like(self.weight))
        self.register_buffer("running_var", _torch.ones_like(self.weight))
        self.register_buffer("num_batches_tracked", _torch.tensor(0, device=device))

    def _forward_impl(self, x: _torch.Tensor) -> _torch.Tensor:
        dim = (self.dim,) if not isinstance(self.dim, tuple) else self.dim

        # Flatten features then move features to dimension 1
        x, shape = x.flatten(start_dim=-len(dim)), x.shape[-len(dim) :]
        running_mean = self.running_mean.flatten()
        running_var = self.running_var.flatten()
        weight = self.weight.flatten()
        bias = self.bias.flatten() if self.bias is not None else None
        x = x.transpose(-1, 1)

        # Batch norm
        if self.training:
            self.num_batches_tracked.add_(1)
        normed_x = _tamm_F.batch_norm(
            x,
            running_mean=running_mean,
            running_var=running_var,
            weight=weight,
            bias=bias,
            training=self.training,
            momentum=self.momentum,
            eps=self.eps,
            cast_dtype=None,  # cast_dtype handled by base layer class
        )

        # Move features back to last dimension and unflatten features
        normed_x = normed_x.transpose(-1, 1)
        return normed_x.unflatten(-1, shape)

    def _get_extra_repr_substrings(self):
        result = super()._get_extra_repr_substrings()
        result.insert(1, f"momentum={self.momentum}")
        return result

    @property
    def track_running_stats(self):
        return True

    @property
    def affine(self):
        return True


class L2Norm(_BaseNorm, _LayerMixin):
    def __init__(
        self,
        *,
        dim: _Optional[int] = -1,
        eps: float = 1e-5,
        cast_dtype: _Optional[_torch.dtype] = _torch.float32,
    ):
        super().__init__(dim=dim, eps=eps)
        self.cast_dtype = cast_dtype

    def _forward_impl(self, x: _torch.Tensor):
        return _tamm_F.l2_norm(x, eps=self.eps, cast_dtype=self.cast_dtype)

    def extra_repr(self) -> str:
        return f"eps={self.eps}, cast_dtype={self.cast_dtype}, dim={self.dim}"


def create_norm_builder(
    features_shape: _Tuple[int, ...],
    spec: _Union[str, _OptionalModuleOrBuilder] = "layer_norm",
    *,
    bias: bool = False,
    dim: int = -1,
    cast_dtype: _Optional[_torch.dtype] = _torch.float32,
    eps: float = 1e-5,
    device=None,
    dtype=None,
):
    """
    Creates and returns a builder for a norm layer.

    Args:
        features_shape (:obj:`tuple` of :obj:`int`): The shape of the feature (channel)
            dimension(s).
        spec:
            Typically a :obj:`str` from the choices ``"layer_norm"``, ``"rms_norm"``,
            or ``"batch_norm"``.  This can also be ``None`` or a module builder,
            in which case the function returns ``spec`` directly.
        bias (:obj:`bool`): A flag for including a bias parameter.  Defaults to
            ``False``.
        dim (:obj:`int` or :obj:`tuple` of :obj:`int`): The feature dimension index
            (or indices) to scale using the ``weight`` parameter.  Defaults to ``-1``,
            corresponding to channels-last inputs.  Use ``1`` for channels-first inputs.
        cast_dtype (:obj:`torch.dtype, optional): An optional dtype for the norm
            computation.  If not ``None``, the layer casts inputs to this dtype
            before normalization and casts outputs to the input dtype.  Defaults
            to ``torch.float32``.
        eps (:obj:`float`): The norm's epsilon parameter.  Defaults to ``1e-5``.
        device: The device for parameters.
        dtype: The dtype for parameters.
    """
    if not isinstance(spec, str):
        return spec

    kwargs = {
        "bias": bias,
        "dim": dim,
        "cast_dtype": cast_dtype,
        "eps": eps,
        "device": device,
        "dtype": dtype,
    }
    if spec == "batch_norm":
        return BatchNorm.Builder(features_shape, **kwargs)
    if spec == "layer_norm":
        return LayerNorm.Builder(features_shape, **kwargs)
    if spec == "rms_norm":
        return RMSNorm.Builder(features_shape, **kwargs)
    raise ValueError(f"spec {spec} not recognized")


def create_vectorized_norm_builder(
    features_shape: _Tuple[int, ...],
    spec: _Union[str, _OptionalModuleOrBuilder],
    *,
    vectorized_dim: int,
    bias: bool = False,
    dim: int = -1,
    cast_dtype: _Optional[_torch.dtype] = _torch.float32,
    eps: float = 1e-5,
    device=None,
    dtype=None,
):
    """
    Creates and returns a builder for a vectorized norm layer.  A vectorized
    norm stacks multiple norms into a single layer.  It is equivalent to

    .. code-block:: python

        x = x.unbind(dim=vectorized_dim)
        x = [norm_i(x_i) for x_i, norm_i in zip(x, norms)]
        return torch.stack(x, dim=vectorized_dim)

    Args:
        features_shape (:obj:`tuple` of :obj:`int`): The shape of the vectorized
            and feature (channel) dimension(s).  The first entry corresponds to the
            vectorized dimension.
        spec:
            Typically a :obj:`str` from the choices ``"rms_norm"`` and
            ``"pre_scale_rms_norm"``. This can also be ``None`` or a module builder,
            in which case the function returns ``spec`` directly.
        vectorized_dim (:obj:`int`): The vectorized dim (axis) in the layer's inputs.
        bias (:obj:`bool`): A flag for including a bias parameter.  Defaults to
            ``False``.
        dim (:obj:`int` or :obj:`tuple` of :obj:`int`): The feature dimension index
            (or indices) to scale using the ``weight`` parameter.  Defaults to ``-1``,
            corresponding to channels-last inputs.  Use ``1`` for channels-first inputs.
        cast_dtype (:obj:`torch.dtype, optional): An optional dtype for the norm
            computation.  If not ``None``, the layer casts inputs to this dtype
            before normalization and casts outputs to the input dtype.  Defaults
            to ``torch.float32``.
        eps (:obj:`float`): The norm's epsilon parameter.  Defaults to ``1e-5``.
        device: The device for parameters.
        dtype: The dtype for parameters.
    """
    if not isinstance(spec, str):
        return spec

    kwargs = {
        "bias": bias,
        "dim": dim,
        "cast_dtype": cast_dtype,
        "eps": eps,
        "device": device,
        "dtype": dtype,
    }
    if spec in ("rms_norm", "pre_scale_rms_norm"):
        scale_mode = (
            NormScaleMode.PRE_SCALE
            if spec == "pre_scale_rms_norm"
            else NormScaleMode.POST_SCALE
        )
        vec_dim = features_shape[0]
        features_shape = features_shape[1:]
        return VectorizedRMSNorm.Builder(
            features_shape,
            vec_dim=vec_dim,
            vec_indx=vectorized_dim,
            scale_mode=scale_mode,
            **kwargs,
        )
    raise ValueError(f"spec {spec} not recognized")
