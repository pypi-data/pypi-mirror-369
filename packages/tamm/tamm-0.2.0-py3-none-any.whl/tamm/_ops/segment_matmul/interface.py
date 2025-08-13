import logging

import torch
from packaging.version import Version

from tamm._ops.segment_matmul.torch import segment_matmul as segment_matmul_torch

logger = logging.getLogger(__name__)


class EnvironmentNotSatisfiedError(Exception):
    """
    Execution environment not satisfied. e.g. GPU not supported, version mismatch and other reasons.
    """


try:
    from torch.utils._triton import has_triton

    if not has_triton():
        raise EnvironmentNotSatisfiedError("Triton is not installed")

    import triton  # pylint: disable=import-error

    if Version(triton.__version__) < Version("3.3.0"):
        raise EnvironmentNotSatisfiedError(
            "There's a bug in triton<3.3.0 affecting numerical accuracy. "
            "Install tamm with 'uv pip install \"tamm[triton]\"' to get the correct dependencies"
        )
    if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] < 8:
        raise EnvironmentNotSatisfiedError(
            "GPUs with CUDA compute capability<8.0 are not supported"
        )
    # pylint: disable=ungrouped-imports
    from tamm._ops.segment_matmul.triton_wrappers import (
        segment_matmul as segment_matmul_triton,
    )

except (ModuleNotFoundError, EnvironmentNotSatisfiedError) as e:
    logger.debug(
        "triton segment matmul cannot be activated for better performance because %s. Will fallback to torch native.",
        e,
    )
    segment_matmul_triton = None  # type: ignore #pylint: disable=invalid-name


def segment_matmul(
    segmented_input: torch.Tensor, group_sizes: torch.Tensor, weight: torch.Tensor
) -> torch.Tensor:
    """Multi-track segment matrix multiplication.

    Performs a segmented matrix multiplication against input, where each segment
    corresponds to a different expert weight. Used in Mixture of Experts (MoE) models.

    .. warning::
        This implementation does not support autocast due to lack of ``@custom_fwd`` and ``@custom_bwd``
        https://docs.pytorch.org/docs/stable/notes/amp_examples.html#amp-custom-examples. Raise an issue in
        #help-tamm if you need the triton kernel to support autocasting.

    This function automatically selects the appropriate implementation:

    * torch native: Used on CPU or GPU with CUDA capability < 8.0
    * triton kernel: GPU with CUDA capability >= 8.0

    Args:
        segmented_input: Tensor of shape ``[T, B, D_IN]`` containing input data
        group_sizes: Tensor of shape ``[T, E]`` indicating sizes of each expert group
        weight: Expert weights tensor of shape ``[T, E, D_IN, D_OUT]``

    Returns:
        torch.Tensor: Result of the segmented matrix multiplication

        Shape Parameters:

        * T: Number of tracks
        * B: Number of ``batches * top_k * context_length``
        * E: Number of experts
        * D_IN: Input dimension of expert weight, per track
        * D_OUT: Output dimension of expert weight, per track

    Example:

        For T=8, E=4, group_sizes=[3, 5, 2, 6] (B=16):

        * segmented_input shape: ``[8, 16, D_IN]``
        * weight shape: ``[8, 4, D_IN, D_OUT]``

        Segments are:

        * segment 1 (expert 1): ``segmented_input[:, 0:3, :]``
        * segment 2 (expert 2): ``segmented_input[:, 3:8, :]``
        * segment 3 (expert 3): ``segmented_input[:, 8:10, :]``
        * segment 4 (expert 4): ``segmented_input[:, 10:16, :]``

        Computed as:

        .. code-block:: python

            torch.cat((einsum("tbi,tio->tbo", segment1, weight[:, 0]),
                       einsum("tbi,tio->tbo", segment2, weight[:, 1]),
                       einsum("tbi,tio->tbo", segment3, weight[:, 2]),
                       einsum("tbi,tio->tbo", segment4, weight[:, 3])), dim=1)
    """
    if segment_matmul_triton is not None:
        return segment_matmul_triton(segmented_input, group_sizes, weight)
    return segment_matmul_torch(segmented_input, group_sizes, weight)
