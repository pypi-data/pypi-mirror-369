"""
Triton kernels implemented as opaque torch operators via custom_op.
This approach is used to maintain compatibility with PyTorch 2.5.1.
Reference: https://docs.pytorch.org/tutorials/advanced/python_custom_ops.html

Note: For PyTorch >= 2.6, we could potentially migrate to @torch.library.triton_op,
but this would introduce challenges for fullgraph compilation due to:
1) Data dependencies in the kernel launch grid
2) Slicing operations in the current implementation
This migration is deferred for now to maintain compatibility and performance.
"""
import torch
import triton  # pylint: disable=import-error
from torch.library import custom_op

from tamm._ops.segment_matmul.torch import segment_matmul as segment_matmul_torch
from tamm._ops.segment_matmul.triton_kernels import (
    segment_matmul_kernel,
    segment_matmul_kernel_backward_dw,
)

# pylint: disable=invalid-name,too-many-locals


@custom_op("tamm::segment_matmul_triton_backward_dw_track", mutates_args={})
def segment_matmul_triton_backward_dw_track(
    tensor1: torch.Tensor,
    tensor2: torch.Tensor,
    group_sizes: torch.Tensor,
) -> torch.Tensor:
    """
    Compute grouped matrix multiplication using Triton kernels. This is a specialized implementation intended for
    backward gradient computation for 'Expert Weights'

    Parameters:
        tensor1: Input tensor of shape [T, B, D_IN]
        tensor2: Input tensor of shape [T, B, D_OUT]
        group_sizes: Group size specifications of shape [T, E]
    Returns:
        Tensor of shape [T, E, D_IN, D_OUT] containing matrix multiplication results
    """
    T, _, D_IN = tensor1.shape
    T, _, D_OUT = tensor2.shape
    T, E = group_sizes.shape
    output = torch.empty(
        (T, E, D_IN, D_OUT), device=tensor1.device, dtype=tensor1.dtype
    )
    stride_tensor1_b = tensor1.stride(1)
    stride_tensor1_din = tensor1.stride(2)

    stride_tensor2_b = tensor2.stride(1)
    stride_tensor2_dout = tensor2.stride(2)

    stride_output_e = output.stride(1)
    stride_output_din = output.stride(2)
    stride_output_dout = output.stride(3)

    for track_idx in range(0, T):

        def grid(meta):
            return (
                triton.cdiv(D_IN, meta["BLOCK_SIZE_D_IN"])
                * triton.cdiv(D_OUT, meta["BLOCK_SIZE_D_OUT"]),
            )

        segment_matmul_kernel_backward_dw[grid](
            tensor1[track_idx],
            tensor2[track_idx],
            output[track_idx],
            group_sizes[track_idx],
            stride_tensor1_b=stride_tensor1_b,
            stride_tensor1_din=stride_tensor1_din,
            stride_tensor2_b=stride_tensor2_b,
            stride_tensor2_dout=stride_tensor2_dout,
            stride_output_e=stride_output_e,
            stride_output_din=stride_output_din,
            stride_output_dout=stride_output_dout,
            E=E,
            D_IN=D_IN,
            D_OUT=D_OUT,
        )

    return output


@custom_op("tamm::segment_matmul_triton_track", mutates_args={})
def segment_matmul_triton_track(
    segment_input: torch.Tensor,
    group_sizes: torch.Tensor,
    weight: torch.Tensor,
) -> torch.Tensor:
    """
    Compute grouped matrix multiplication using Triton kernels.

    Parameters:
        segment_input: Input segments of shape [T, B, D_IN]
        group_sizes: Expert groupings of shape [T, E]
        weight: Expert weights of shape [T, E, D_IN, D_OUT]
    Returns:
        Tensor of shape [T, B, D_OUT] containing grouped GEMM results
    """
    T, E, D_IN, D_OUT = weight.shape
    _, B, _ = segment_input.shape  # T, B, D_IN
    output = torch.empty(
        (T, B, D_OUT), device=segment_input.device, dtype=segment_input.dtype
    )
    stride_segment_input_b = segment_input.stride(1)
    stride_segment_input_din = segment_input.stride(2)

    stride_weight_e = weight.stride(1)
    stride_weight_din = weight.stride(2)
    stride_weight_dout = weight.stride(3)

    stride_output_b = output.stride(1)
    stride_output_dout = output.stride(2)

    for track_idx in range(0, T):
        # pylint: disable=cell-var-from-loop
        def grid(meta):
            return (
                triton.cdiv(group_sizes[track_idx], meta["BLOCK_SIZE_B"]).sum()
                * triton.cdiv(D_OUT, meta["BLOCK_SIZE_D_OUT"]),
            )

        segment_matmul_kernel[grid](
            segment_input[track_idx],
            weight[track_idx],
            output[track_idx],
            group_sizes[track_idx],
            stride_segment_input_b=stride_segment_input_b,
            stride_segment_input_din=stride_segment_input_din,
            stride_weight_e=stride_weight_e,
            stride_weight_din=stride_weight_din,
            stride_weight_dout=stride_weight_dout,
            stride_output_b=stride_output_b,
            stride_output_dout=stride_output_dout,
            E=E,
            D_IN=D_IN,
            D_OUT=D_OUT,
        )

    return output


@segment_matmul_triton_track.register_fake
def segment_matmul_triton_track_fake(
    segment_input: torch.Tensor,
    group_sizes: torch.Tensor,
    weight: torch.Tensor,
) -> torch.Tensor:
    """
    Fake implementation for segment_matmul_triton_track that verifies inputs and returns an empty output tensor.
    This is needed for torch.compile to trace ``segment_matmul_triton_track``

    Parameters:
        segment_input: Input segments of shape [T, B, D_IN]
        group_sizes: Expert groupings of shape [T, E]
        weight: Expert weights of shape [T, E, D_IN, D_OUT]

    Returns:
        Empty tensor of shape [T, B, D_OUT]
    """
    assert weight.is_contiguous()
    assert group_sizes.is_contiguous()
    assert segment_input.is_contiguous()

    T, _, D_IN, D_OUT = weight.shape
    _, B, _ = segment_input.shape  # T, B, D_I
    assert segment_input.size(0) == T
    assert segment_input.size(2) == D_IN
    return torch.empty(
        (T, B, D_OUT), device=segment_input.device, dtype=segment_input.dtype
    )


@segment_matmul_triton_backward_dw_track.register_fake
def segment_matmul_triton_backward_dw_track_fake(
    tensor1: torch.Tensor,
    tensor2: torch.Tensor,
    group_sizes: torch.Tensor,
) -> torch.Tensor:
    """
    Fake implementation for segment_matmul_triton_backward_dw_track that verifies inputs and
    returns an empty output tensor. This is needed for torch.compile to trace
    ``segment_matmul_triton_backward_dw_track``

    Parameters:
        tensor1: Input tensor of shape [T, B, D_IN]
        tensor2: Input tensor of shape [T, B, D_OUT]
        group_sizes: Group size specifications of shape [T, E]

    Returns:
        Empty tensor of shape [T, E, D_IN, D_OUT]
    """
    T, _, D_IN = tensor1.shape
    T, _, D_OUT = tensor2.shape
    T, E = group_sizes.shape
    assert tensor1.is_contiguous()
    assert tensor2.is_contiguous()
    assert group_sizes.is_contiguous()
    assert tensor1.shape[:2] == tensor2.shape[:2]
    return torch.empty((T, E, D_IN, D_OUT), device=tensor1.device, dtype=tensor1.dtype)


def setup_context(ctx, inputs, output):
    """
    Setup autograd context by saving tensors needed for backward pass.

    Parameters:
        ctx: Autograd context
        inputs: Input tensors (segment_input, group_sizes, weight)
        output: Output tensor
    """
    del output
    segment_input, group_sizes, weight = inputs
    saved_segment_input, saved_weight = None, None
    if ctx.needs_input_grad[0]:
        saved_segment_input = segment_input
    if ctx.needs_input_grad[0] or ctx.needs_input_grad[2]:
        saved_weight = weight
    ctx.save_for_backward(saved_segment_input, group_sizes, saved_weight)


def backward(ctx, grad_output):
    """
    Compute gradients for the group GEMM operation.

    Parameters:
        ctx: Autograd context
        grad_output: Gradient of the output tensor

    Returns:
        Gradients for segment_input, group_sizes, and weight
    """
    saved_segment_input, group_sizes, saved_weight = ctx.saved_tensors
    grad_segment_input, grad_weight = None, None
    if ctx.needs_input_grad[0]:
        # grad_output: (T, B, D_OUT)
        # saved_weight: (T, E, D_IN, DOUT)
        # grad_segment_input: (T, B, D_IN)
        grad_segment_input = segment_matmul_triton_track(
            grad_output, group_sizes, saved_weight.swapaxes(2, 3)
        )
    if ctx.needs_input_grad[2]:
        # grad_output: (T, B, D_OUT)
        # saved_segment_input: (T, B, D_IN)
        # grad_saved_weight: (T, E, D_IN, D_OUT)
        # grad_saved_weight =  torch.einsum('tbi,tbo->tbio', saved_segment_input, grad_output)
        grad_weight = segment_matmul_triton_backward_dw_track(
            saved_segment_input, grad_output, group_sizes
        )
    return grad_segment_input, None, grad_weight


segment_matmul_triton_track.register_autograd(backward, setup_context=setup_context)


def segment_matmul(
    segmented_input: torch.Tensor, group_sizes: torch.Tensor, weight: torch.Tensor
) -> torch.Tensor:
    if segmented_input.device.type == "cpu":
        return segment_matmul_torch(segmented_input, group_sizes, weight)

    return segment_matmul_triton_track(segmented_input, group_sizes, weight)
