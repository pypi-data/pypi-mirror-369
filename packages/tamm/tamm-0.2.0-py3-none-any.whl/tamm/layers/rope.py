"""
layers.rope
^^^^^^^^^^^

This submodule provides utilities for
`rotary positional embeddings <https://arxiv.org/abs/2104.09864>`__.

.. autofunction:: tamm.layers.rope.compute_rope_coefficients

.. autofunction:: tamm.layers.rope.rotate
"""

import math as _math
from typing import Optional as _Optional
from typing import Tuple as _Tuple

import torch as _torch


def compute_rope_coefficients(
    *,
    positions: _torch.Tensor,
    dim: int,
    theta: float = 10000.0,
    dtype: _Optional[_torch.dtype] = None,
) -> _torch.Tensor:
    """
    Computes sine and cosine values for rotating a tensor with :func:`~.rope.rotate`.

    Args:
        positions (:obj:`torch.Tensor`): A ``batch_size x seq_length`` tensor of
            token positions.
        dim (:obj:`int`): The last dim of the tensor to rotate.  This must be divisible
            by 2.
        theta (:obj:`float`): The base value for computing sinusoid frequencies.
        dtype (:obj:`torch.dtype`): The dtype for the result.

    Returns:
        A tensor of sine and cosine values with shape
        ``[batch_size x seq_length, 1, (dim / 2),  2,  2]``.  The last two dimensions
        hold 2D rotation matrices.
    """
    if dim % 2:
        raise ValueError(f"dim has value {dim}, but this must be an even integer")

    # flatten batch_size and seq_length dims to support on-device export
    # (as of april 2025, coremltools limits tensors to 5 dimensions)
    positions = positions.flatten()

    # This is to avoid a bug in torch compile while ensuring numerical accuracy
    # Moving a small list of floats shouldn't create too much burden to GPUs
    exponents = [x * (2 / dim - 1) / (dim // 2 - 1) for x in range(dim // 2)]
    freqs_list = [_math.pow(theta, x) for x in exponents]
    freqs = _torch.tensor(freqs_list, dtype=_torch.float32, device=positions.device)
    angles = positions[..., None, None] * freqs
    sin, cos = _torch.sin(angles), _torch.cos(angles)
    if dtype is not None:
        sin, cos = sin.type(dtype), cos.type(dtype)
    result = _torch.stack([cos, -sin, sin, cos], dim=-1)
    return result.reshape(
        *result.shape[:-1], 2, 2
    )  # the last 2 dimensions are the 2d rotation matrices


def rotate(
    x: _torch.Tensor, *, rope_coefficients: _torch.Tensor
) -> _Tuple[_torch.Tensor, _torch.Tensor]:
    """
    Returns a rotation of ``x``.

    Args:
        x (:obj:`torch.Tensor`): A ``batch_size x seq_length x num_heads x dim`` tensor.
        rope_coefficients (:obj:`torch.Tensor`): A
            ``[batch_size x seq_length, 1, (dim / 2),  2,  2]`` tensor returned by
            :func:`compute_rope_coefficients`.

    Returns:
        The rotated ``x``.  This is a 2D rotation of each pair of values in the last
        dimension.
    """
    input_shape = x.shape
    input_dtype = x.dtype

    if len(x.shape) != 4:
        x = x.reshape(*input_shape[:-1], -1, 1, 2)
        # split batch_size and seq_length from the first dim
        rope_coefficients = rope_coefficients.reshape(
            input_shape[0], -1, *rope_coefficients.shape[1:]
        )
        # Make it work for a vectorized dimension (dimension after batch) (TODO: is there a better way)
        rope_coefficients = rope_coefficients.unsqueeze(1)
    else:
        # flatten batch_size and seq_length to match rope_coefficients
        x = x.reshape(-1, *input_shape[2:-1], input_shape[-1] // 2, 1, 2)

    # pylint: disable-next=not-callable
    x = _torch.linalg.vecdot(x, rope_coefficients, dim=-1)

    x = x.reshape(input_shape)
    return x.type(input_dtype)
