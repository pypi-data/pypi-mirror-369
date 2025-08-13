import enum as _enum
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
from torch.nn import functional as _F

from tamm import _helpers
from tamm._ops import segment_matmul  # noqa: F401 pylint: disable=unused-import
from tamm.utils import _torch_compatibility


def rms_norm(
    tensor: _torch.Tensor,
    normalized_shape: _Tuple[int, ...],
    *,
    weight: _torch.Tensor = None,
    bias: _torch.Tensor = None,
    eps: float = 1e-05,
    cast_dtype: _Optional[_torch.dtype] = _torch.float32,
) -> _torch.Tensor:
    """Applies RMS normalization."""
    input_dtype = tensor.dtype
    with _helpers.autocast_disabled(tensor.device):
        if cast_dtype is not None:
            tensor = tensor.type(cast_dtype)
        tensor = _torch_compatibility.rms_norm(
            tensor, normalized_shape=normalized_shape, weight=weight, eps=eps
        )
        if bias is not None:
            tensor = tensor + bias
        return tensor.type(input_dtype)


class NormScaleMode(_enum.Enum):
    """
    An :class:`Enum` for controlling the scaling behavior in norm layers.
    """

    POST_SCALE = "POST_SCALE"
    """
    Multiply outputs by the weight and add the bias after normalization.  This is the
    standard mode.
    """

    PRE_SCALE = "PRE_SCALE"
    """
    Multiply inputs by the weight prior to normalization, and add the bias after
    normalization.
    """


def batched_rms_norms(
    tensor: _torch.Tensor,
    normalized_shape: _Tuple[int],
    *,
    weight: _Union[_torch.Tensor, None] = None,
    bias: _Union[_torch.Tensor, None] = None,
    eps: float = 1e-05,
    scale_mode: NormScaleMode = NormScaleMode.POST_SCALE,
    cast_dtype: _Optional[_torch.dtype] = _torch.float32,
) -> _torch.Tensor:
    """
    Applies RMS normalization.  This the same a :func:`rms_norm`, but the weight
    and bias tensors can have more dimensions than ``len(normalized_shape)``.
    """
    input_dtype = tensor.dtype
    if scale_mode not in [NormScaleMode.PRE_SCALE, NormScaleMode.POST_SCALE]:
        raise ValueError(f"scale_mode {scale_mode} not recognized")
    with _helpers.autocast_disabled(tensor.device):
        if cast_dtype is not None:
            tensor = tensor.type(cast_dtype)
        if scale_mode is NormScaleMode.PRE_SCALE:
            tensor = _apply_scale(tensor, weight=weight, bias=None)

        tensor = _torch_compatibility.rms_norm(
            tensor, normalized_shape=normalized_shape, eps=eps
        )

        if scale_mode is NormScaleMode.PRE_SCALE:
            tensor = _apply_scale(tensor, weight=None, bias=bias)
        elif scale_mode is NormScaleMode.POST_SCALE:
            tensor = _apply_scale(tensor, weight=weight, bias=bias)
        return tensor.type(input_dtype)


def _apply_scale(
    tensor: _torch.Tensor,
    *,
    weight: _Union[_torch.Tensor, None],
    bias: _Union[_torch.Tensor, None],
) -> _torch.Tensor:
    if weight is not None and bias is not None:
        return _torch.addcmul(bias, tensor, weight)
    if weight is not None:
        return tensor * weight
    if bias is not None:
        return tensor + bias
    return tensor


def layer_norm(
    tensor: _torch.Tensor,
    normalized_shape: _Tuple[int, ...],
    *,
    weight: _Union[_torch.Tensor, None] = None,
    bias: _Union[_torch.Tensor, None] = None,
    eps: float = 1e-05,
    cast_dtype: _Optional[_torch.dtype] = _torch.float32,
) -> _torch.Tensor:
    with _helpers.autocast_disabled(tensor.device):
        input_dtype = tensor.dtype
        if cast_dtype is not None:
            tensor = tensor.type(cast_dtype)
        if weight is not None:
            weight = weight.type_as(tensor)
        if bias is not None:
            bias = bias.type_as(tensor)
        result = _torch.nn.functional.layer_norm(
            tensor, normalized_shape=normalized_shape, weight=weight, bias=bias, eps=eps
        )
        return result.type(input_dtype)


def batch_norm(
    tensor: _torch.Tensor,
    *,
    running_mean: _Union[_torch.Tensor, None],
    running_var: _Union[_torch.Tensor, None],
    weight: _Union[_torch.Tensor, None] = None,
    bias: _Union[_torch.Tensor, None] = None,
    training: bool = False,
    momentum: float = 0.1,
    eps: float = 1e-05,
    cast_dtype: _Optional[_torch.dtype] = _torch.float32,
) -> _torch.Tensor:
    with _helpers.autocast_disabled(tensor.device):
        input_dtype = tensor.dtype
        if cast_dtype is not None:
            tensor = tensor.type(cast_dtype)
        result = _torch.nn.functional.batch_norm(
            tensor,
            running_mean=running_mean,
            running_var=running_var,
            weight=weight,
            bias=bias,
            training=training,
            momentum=momentum,
            eps=eps,
        )
        return result.type(input_dtype)


# pylint: disable-next=redefined-builtin
def reglu(gate_input, input):
    """
    GLU variant that uses ReLU nonlinear function in place of sigmoid.

    Args:
        gate_input (:obj:`torch.Tensor`): The input to the ReLU function.
        input (:obj:`torch.Tensor`): The input to scale by the ReLU output.

    Returns:
        The activation tensor.
    """
    return input * _F.relu(gate_input)


# pylint: disable-next=redefined-builtin
def swiglu(gate_input, input):
    """
    GLU variant that uses Swish nonlinear function in place of sigmoid.

    Args:
        gate_input (:obj:`torch.Tensor`): The input to the SiLU function.
        input (:obj:`torch.Tensor`): The input to scale by the SiLU output.

    Returns:
        The activation tensor.
    """
    return input * _F.silu(gate_input)


def l2_norm(
    tensor: _torch.Tensor,
    eps: float = 1e-05,
    cast_dtype: _Optional[_torch.dtype] = _torch.float32,
) -> _torch.Tensor:
    if cast_dtype is not None:
        cast_tensor = tensor.type(cast_dtype)
    else:
        cast_tensor = tensor

    return _F.normalize(cast_tensor, dim=-1, eps=eps)


def rearrange_embeddings_to_channels_first(embeddings, *, unflattened_shape):
    embeddings = embeddings.movedim(1, -1)
    return embeddings.reshape(*embeddings.shape[:-1], *unflattened_shape)


def rearrange_embeddings_from_channels_first(tensor):
    return tensor.flatten(start_dim=2).movedim(1, -1)


def geglu(gate_input, input, approximate="tanh"):  # pylint: disable=redefined-builtin
    """
    GLU variant that uses GELU function in place of sigmoid.

    Args:
        gate_input (:obj:`torch.Tensor`): The input to the GELU function.
        input (:obj:`torch.Tensor`): The input to scale by the GELU output.

    Returns:
        The activation tensor.
    """
    # pylint: disable=not-callable
    return input * _F.gelu(gate_input, approximate=approximate)


def add_batch_dim(tensor: _torch.Tensor, batch_size: int = 1) -> _torch.Tensor:
    """
    Adds a new first dimension to ``tensor`` and then repeats it ``batch_size`` times
    along that dimension.
    """
    tile_shape = (batch_size,) + (1,) * tensor.ndim
    return tensor.tile(tile_shape)


def maybe_flatten_sequence(
    sequence: _Union[_torch.Tensor, _Dict[str, _torch.Tensor]], end_dim: int = -1
) -> _torch.Tensor:
    """
    If ``sequence`` is a tensor, this function flattens the dimensions between ``1``
    and ``end_dim``.  If ``sequence`` is a :obj:`dict`, this function flattens each
    of its values and then concatenates the flat tensors along dimension 1 in the order
    that they appear in the :obj:`dict`.  If ``sequence`` is neither a tensor nor a
    :obj:`dict`, this function simply returns the ``sequence`` unchanged.
    """
    if _torch.is_tensor(sequence):
        end_dim = end_dim % sequence.ndim
        if end_dim > 1:
            return sequence.flatten(start_dim=1, end_dim=end_dim)
        return sequence

    if not isinstance(sequence, dict):
        return sequence

    sequence = [
        maybe_flatten_sequence(tensor, end_dim=end_dim) for tensor in sequence.values()
    ]
    return _torch.cat(sequence, dim=1)


def maybe_unflatten_sequence(sequence, *, original, end_dim: int = -1):
    """
    This function performs the inverse of :func:`maybe_flatten_sequence`.  It unflattens
    ``sequence`` to match the structure of ``original``.  Here ``original`` may be
    a :obj:`dict` or tensor.
    """
    if _torch.is_tensor(original):
        spatial_shape = original.shape[1 : (end_dim % original.ndim) + 1]
        if len(spatial_shape) == 1:
            return sequence
        return sequence.reshape(sequence.shape[0], *spatial_shape, *sequence.shape[2:])

    if not isinstance(original, dict):
        return sequence

    original_tensors = list(original.values())
    flat_original_tensors = [
        maybe_flatten_sequence(tensor, end_dim=end_dim) for tensor in original.values()
    ]
    seq_lens = [o_i.size(1) for o_i in flat_original_tensors]
    sequence = _torch.split(sequence, seq_lens, dim=1)
    sequence = [
        maybe_unflatten_sequence(e_i, original=o_i, end_dim=end_dim)
        for e_i, o_i in zip(sequence, original_tensors)
    ]
    return dict(zip(original, sequence))


def maybe_flatten_embeddings(
    embeddings: _Union[_torch.Tensor, _Dict[str, _torch.Tensor]]
) -> _torch.Tensor:
    """
    A convenience function for calling :func:`maybe_flatten_sequence` with
    ``end_dim=-2``.  This is helpful for flattening spatial embeddings with shape
    ``(batch_size, height, width, dim)`` into shape ``(batch_size, sequence_len, dim)``.
    """
    return maybe_flatten_sequence(embeddings, end_dim=-2)


def maybe_unflatten_embeddings(
    embeddings: _torch.Tensor,
    *,
    original: _Union[_torch.Tensor, _Dict[str, _torch.Tensor]],
) -> _Union[_torch.Tensor, _Dict[str, _torch.Tensor]]:
    """
    A convenience function for calling :func:`maybe_unflatten_sequence` with
    ``end_dim=-2``.
    """
    return maybe_unflatten_sequence(embeddings, original=original, end_dim=-2)


def inverse_permute(tensor: _torch.Tensor, perm: _List[int]):
    """
    A function that performs the inverse of :func:`torch.permute`.

    Args:
        tensor (:obj:`torch.Tensor`): Tensor to unpermute.
        perm (:obj:`List[int]`): Int list specifying the original axis permutation.

    Returns:
        The inverse permutation of tensor.
    """
    inv_perm = [perm.index(idx) for idx in range(len(perm))]
    assert len(inv_perm) == len(perm)
    return _torch.permute(tensor, inv_perm)


def stack(*tensors, dim=0):
    """
    This function operates similarly to torch.stack, but accepts multiple tensors as
    input arguments instead of a list of tensors. It can be frequently used to fuse
    parameters because the 'to_tamm' and 'from_tamm' functions in ParamMapper
    do not accept lists as input.
    """
    return _torch.stack(tensors, dim=dim)


def relaxed_one_hot(
    tensor: _torch.Tensor, *, num_classes: int, dtype: _torch.dtype = _torch.bool
):
    """
    This function is similar to :func:`torch.nn.functional` except for the following
    differences:

    1. The function ignores indices outside the range ``[0, num_classes)`` rather
       than raising an error.
    2. The dtype of the result defaults to ``bool``, and it is also configurable.
    3. The ``num_classes`` argument is required.

    Args:
        tensor (:obj:`torch.Tensor`): An integer tensor of indices.
        num_classes (:obj:`int`): The embedding size of the resulting one-hot encodings.
        dtype (:obj:`torch.dtype`): The result dtype.

    Returns:
        A binary-valued tensor with shape ``(*tensor.shape, num_classes)``.  Each
        entry takes value ``1`` if its index corresponds to an index in ``tensor``
        (and ``0`` otherwise).
    """
    input_shape = tensor.shape
    if tensor.device.type == "mps":
        tensor = tensor.flatten()  # due to an mps bug as of torch 2.5

    arange = _torch.arange(num_classes, device=tensor.device, dtype=tensor.dtype)
    result = tensor[..., None] == arange

    if tensor.device.type == "mps":
        result = result.reshape(*input_shape, -1)

    return result.type(dtype)


def cumsum(tensor: _torch.Tensor, dim: int) -> _torch.Tensor:
    """
    This is the same as :func:`torch.cumsum` but it is much faster on CUDA
    for important use cases.
    """
    should_move_dim = dim not in (-1, tensor.ndim - 1)
    if should_move_dim:
        tensor = tensor.movedim(dim, -1)
    result = tensor.cumsum(dim=-1)
    if should_move_dim:
        result = result.movedim(-1, dim)
    return result


def crop(tensor: _torch.Tensor, *, shape: _Tuple[int, ...]) -> _torch.Tensor:
    """
    Truncates tensors with shape ``(batch_size, num_channels, *spatial_shape)``
    at top left corner to tensors with shape ``(batch_size, num_channels, *shape)``.
    """
    tensor_spatial_shape = tensor.shape[2:]
    if tensor_spatial_shape == shape:
        return tensor
    if any(i_dim > j_dim for i_dim, j_dim in zip(shape, tensor_spatial_shape)):
        raise ValueError(
            "Each dimension of truncation_shape must not be larger than the "
            "corresponding dimension in the tensor to be truncated."
        )
    slices = (slice(None), slice(None)) + tuple(slice(dim) for dim in shape)
    tensor = tensor[slices]
    return tensor


def soft_cap(tensor: _torch.Tensor, *, cap: float) -> _torch.Tensor:
    """
    Computes ``cap * tanh(tensor / cap)``, which is a smooth and differentiable way
    to cap the values of a tensor.

    Raises: ValueError: If ``cap`` is non-positive.
    """

    if cap <= 0:
        raise ValueError(f"soft_cap requires cap > 0, but cap is {cap}")
    return cap * _torch.tanh(tensor / cap)


def expand_dim(
    tensor: _torch.Tensor,
    repeat: int,
    dim: int = -1,
    unsqueeze: bool = False,
    interleave: bool = False,
):
    """
    Repeats a tensor along a specific dimension using :meth:`torch.Tensor.expand`
    (which does not copy the underlying data).

    Args:
        tensor (:obj:`torch.Tensor`): The tensor to expand.
        repeat (:obj:`int`): The expansion factor.
        dim (:obj:`int`, optional): The dimension to expand.  Defaults to ``-1``.
        unsqueeze (:obj:`bool`, optional): A flag for inserting a new dimension
            using :torch:`torch.unsqueeze` before the expansion.  Defaults to ``False``.
        interleave (:obj:`bool`, optional): A flag for interleaving the expanded values,
            similar to :func:`torch.repeat_interleave`.  Defaults to ``False``.
    """
    if unsqueeze:
        tensor = tensor.unsqueeze(dim)
    dim = dim % tensor.ndim

    is_original_size_1 = tensor.size(dim) == 1

    if not is_original_size_1:
        if interleave:
            dim = dim + 1
        tensor = tensor.unsqueeze(dim)

    expand_sizes = (-1,) * dim + (repeat,) + (-1,) * (tensor.ndim - dim - 1)
    tensor = tensor.expand(expand_sizes)

    if not is_original_size_1:
        if interleave:
            dim = dim - 1
        tensor = tensor.flatten(start_dim=dim, end_dim=dim + 1)

    return tensor
