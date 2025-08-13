# pylint: disable=invalid-name,too-many-locals


import triton  # pylint: disable=import-error
import triton.language as tl  # pylint: disable=import-error


@triton.autotune(
    configs=[
        triton.Config(
            {
                "BLOCK_SIZE_B": block_size_b,
                "BLOCK_SIZE_D_IN": block_size_din,
                "BLOCK_SIZE_D_OUT": block_size_dout,
                "GROUP_SIZE_B": group_size_b,
            },
            num_stages=num_stages,
            num_warps=num_warps,
            num_ctas=1,
        )
        for num_warps in [16]
        for num_stages in [2, 3]
        for block_size_b in [128, 256]
        for block_size_dout in [128]
        for block_size_din in [64]
        for group_size_b in [8]
    ],
    key=["E", "D_IN", "D_OUT"],
)
@triton.jit
def segment_matmul_kernel(
    segment_input_ptr,
    weights_ptr,
    output_ptr,
    group_sizes_ptr,
    stride_segment_input_b,
    stride_segment_input_din,
    stride_weight_e,
    stride_weight_din,
    stride_weight_dout,
    stride_output_b,
    stride_output_dout,
    E: tl.constexpr,
    D_IN: tl.constexpr,
    D_OUT: tl.constexpr,
    BLOCK_SIZE_B: tl.constexpr,
    BLOCK_SIZE_D_OUT: tl.constexpr,
    BLOCK_SIZE_D_IN: tl.constexpr,
    GROUP_SIZE_B: tl.constexpr,
) -> None:
    """
    Performs grouped matrix multiplication for MoE forward pass.

    This kernel computes Y = X @ W where inputs are grouped by expert assignment.
    Each group (expert) has its own weight matrix, and the computation is parallelized
    across batch elements and output dimensions.

    Parameters:
        segment_input_ptr: Pointer to input tensor X of shape [B, D_IN]
        weights_ptr: Pointer to weight tensor W of shape [E, D_IN, D_OUT]
        output_ptr: Pointer to output tensor Y of shape [B, D_OUT]
        group_sizes_ptr: Pointer to array containing number of elements per expert
        stride_segment_input_b: Stride of input tensor along batch dimension
        stride_segment_input_din: Stride of input tensor along input dimension
        stride_weight_e: Stride of weight tensor along expert dimension
        stride_weight_din: Stride of weight tensor along input dimension
        stride_weight_dout: Stride of weight tensor along output dimension
        stride_output_b: Stride of output tensor along batch dimension
        stride_output_dout: Stride of output tensor along output dimension
        E: Number of experts
        D_IN: Input dimension size
        D_OUT: Output dimension size
        BLOCK_SIZE_B: Tile size for batch dimension
        BLOCK_SIZE_D_OUT: Tile size for output dimension
        BLOCK_SIZE_D_IN: Tile size for input dimension
        GROUP_SIZE_B: Number of batch blocks to process together (for l2 cache optimization)
    """
    pid = tl.program_id(axis=0)
    offs_group_sizes = tl.arange(0, triton.next_power_of_2(E))
    group_sizes = tl.load(
        group_sizes_ptr + offs_group_sizes, mask=offs_group_sizes < E, other=0.0
    )
    num_pid_b = tl.sum(tl.cdiv(group_sizes, BLOCK_SIZE_B))
    num_pid_dout = tl.cdiv(D_OUT, BLOCK_SIZE_D_OUT)
    num_pid_in_group = GROUP_SIZE_B * num_pid_dout
    group_id = pid // num_pid_in_group
    first_pid_b = group_id * GROUP_SIZE_B
    group_size_b = min(num_pid_b - first_pid_b, GROUP_SIZE_B)
    g_idx = first_pid_b + ((pid % num_pid_in_group) % group_size_b)
    dout_idx = (pid % num_pid_in_group) // group_size_b

    n_blocks_group = tl.cdiv(group_sizes, BLOCK_SIZE_B)
    n_blocks_group_cumsum = tl.cumsum(n_blocks_group)
    expert_idx = tl.argmax(g_idx < n_blocks_group_cumsum, axis=0, tie_break_left=True)

    b_start_index = tl.where(
        offs_group_sizes < expert_idx, group_sizes, tl.zeros_like(group_sizes)
    )
    b_start_index = tl.sum(b_start_index)

    intra_group_start_idx = tl.where(
        offs_group_sizes < expert_idx, group_sizes, tl.zeros_like(group_sizes)
    )
    intra_group_start_idx = tl.sum(tl.cdiv(intra_group_start_idx, BLOCK_SIZE_B))
    n_blocks_this_group = tl.cdiv(tl.load(group_sizes_ptr + expert_idx), BLOCK_SIZE_B)
    intra_group_idx = (g_idx - intra_group_start_idx) % n_blocks_this_group

    b_start = b_start_index + intra_group_idx * BLOCK_SIZE_B
    group_sizes_upto_expert = tl.where(
        offs_group_sizes <= expert_idx, group_sizes, tl.zeros_like(group_sizes)
    )
    b_max_boundary = tl.sum(group_sizes_upto_expert)

    accumulator = tl.zeros((BLOCK_SIZE_B, BLOCK_SIZE_D_OUT), dtype=tl.float32)

    # regular matmul
    for k_offset in tl.range(0, tl.cdiv(D_IN, BLOCK_SIZE_D_IN)):
        k_start = k_offset * BLOCK_SIZE_D_IN
        offs_b_in = b_start + tl.arange(0, BLOCK_SIZE_B)
        offs_k_in = k_start + tl.arange(0, BLOCK_SIZE_D_IN)
        input_ptrs = (
            segment_input_ptr
            + offs_b_in[:, None] * stride_segment_input_b
            + offs_k_in[None, :] * stride_segment_input_din
        )
        input_mask = (offs_b_in[:, None] < b_max_boundary) & (offs_k_in[None, :] < D_IN)
        segment_input_block = tl.load(input_ptrs, mask=input_mask, other=0.0)

        offs_k_weight = k_start + tl.arange(0, BLOCK_SIZE_D_IN)
        offs_dout_weight = dout_idx * BLOCK_SIZE_D_OUT + tl.arange(0, BLOCK_SIZE_D_OUT)
        weight_ptrs = (
            weights_ptr
            + expert_idx * stride_weight_e
            + offs_k_weight[:, None] * stride_weight_din
            + offs_dout_weight[None, :] * stride_weight_dout
        )
        weight_mask = (offs_k_weight[:, None] < D_IN) & (
            offs_dout_weight[None, :] < D_OUT
        )
        weights_block = tl.load(weight_ptrs, mask=weight_mask, other=0.0)
        accumulator = tl.dot(
            segment_input_block,
            weights_block,
            acc=accumulator,
            input_precision="tf32x3",
        )

    offs_b_out = b_start + tl.arange(0, BLOCK_SIZE_B)
    offs_dout_out = dout_idx * BLOCK_SIZE_D_OUT + tl.arange(0, BLOCK_SIZE_D_OUT)
    output_ptrs = (
        output_ptr
        + offs_b_out[:, None] * stride_output_b
        + offs_dout_out[None, :] * stride_output_dout
    )
    output_mask = (offs_b_out[:, None] < b_max_boundary) & (
        offs_dout_out[None, :] < D_OUT
    )
    tl.store(output_ptrs, accumulator, mask=output_mask)


@triton.autotune(
    configs=[
        triton.Config(
            {
                "BLOCK_SIZE_B": block_size_b,
                "BLOCK_SIZE_D_IN": block_size_din,
                "BLOCK_SIZE_D_OUT": block_size_dout,
                "GROUP_SIZE_D_OUT": group_size_dout,
            },
            num_stages=num_stages,
            num_warps=num_warps,
            num_ctas=1,
        )
        for num_warps in [16]
        for num_stages in [2, 3]
        for block_size_b in [64, 128]
        for block_size_dout in [64, 128]
        for block_size_din in [64, 128]
        for group_size_dout in [32]
    ],
    key=["E", "D_IN", "D_OUT"],
)
@triton.jit
def segment_matmul_kernel_backward_dw(
    tensor1_ptr,
    tensor2_ptr,
    output_ptr,
    group_sizes_ptr,
    stride_tensor1_b,
    stride_tensor1_din,
    stride_tensor2_b,
    stride_tensor2_dout,
    stride_output_e,
    stride_output_din,
    stride_output_dout,
    E: tl.constexpr,
    D_IN: tl.constexpr,
    D_OUT: tl.constexpr,
    BLOCK_SIZE_B: tl.constexpr,
    BLOCK_SIZE_D_OUT: tl.constexpr,
    BLOCK_SIZE_D_IN: tl.constexpr,
    GROUP_SIZE_D_OUT: tl.constexpr,
) -> None:
    """
    Performs grouped matrix multiplication for MoE backward pass, computing gradients for weights.

    This kernel computes dW = X.T @ dY where inputs are grouped by expert. For each expert,
    it computes the gradient of weights by accumulating outer products across the batch elements
    assigned to that expert.

    Parameters:
        tensor1_ptr: Pointer to input tensor X of shape [B, D_IN]
        tensor2_ptr: Pointer to gradient tensor dY of shape [B, D_OUT]
        output_ptr: Pointer to weight gradient tensor dW of shape [E, D_IN, D_OUT]
        group_sizes_ptr: Pointer to array containing number of elements per expert
        stride_tensor1_b: Stride of input tensor along batch dimension
        stride_tensor1_din: Stride of input tensor along input dimension
        stride_tensor2_b: Stride of gradient tensor along batch dimension
        stride_tensor2_dout: Stride of gradient tensor along output dimension
        stride_output_e: Stride of output tensor along expert dimension
        stride_output_din: Stride of output tensor along input dimension
        stride_output_dout: Stride of output tensor along output dimension
        E: Number of experts
        D_IN: Input dimension size
        D_OUT: Output dimension size
        BLOCK_SIZE_B: Tile size for batch dimension
        BLOCK_SIZE_D_OUT: Tile size for output dimension
        BLOCK_SIZE_D_IN: Tile size for input dimension
        GROUP_SIZE_D_OUT: Number of output dimension tiles to process together (for l2 cache optimization)
    """
    pid = tl.program_id(axis=0)
    experts = tl.arange(0, triton.next_power_of_2(E))
    group_sizes = tl.load(group_sizes_ptr + experts, mask=experts < E, other=0.0)
    num_pid_din = tl.cdiv(D_IN, BLOCK_SIZE_D_IN)
    num_pid_dout = tl.cdiv(D_OUT, BLOCK_SIZE_D_OUT)

    pid_din = pid // num_pid_dout
    pid_dout = pid % num_pid_dout
    pid_din, pid_dout = tl.swizzle2d(
        pid_din, pid_dout, num_pid_din, num_pid_dout, GROUP_SIZE_D_OUT
    )
    b_start = tl.zeros((1,), dtype=tl.int64)
    for expert_idx in tl.range(0, E):
        group_size = tl.load(group_sizes_ptr + expert_idx)
        b_end = tl.sum(
            tl.where(experts <= expert_idx, group_sizes, tl.zeros_like(group_sizes))
        )
        offs_tensor_b = (b_start + tl.arange(0, BLOCK_SIZE_B))[:, None]
        offs_tensor1_din = (
            pid_din * BLOCK_SIZE_D_IN + tl.arange(0, BLOCK_SIZE_D_IN)[None, :]
        )
        offs_tensor1 = (
            offs_tensor_b * stride_tensor1_b + offs_tensor1_din * stride_tensor1_din
        )

        offs_tensor2_dout = (
            pid_dout * BLOCK_SIZE_D_OUT + tl.arange(0, BLOCK_SIZE_D_OUT)[None, :]
        )
        offs_tensor2 = (
            offs_tensor_b * stride_tensor2_b + offs_tensor2_dout * stride_tensor2_dout
        )

        accumulator = tl.zeros((BLOCK_SIZE_D_IN, BLOCK_SIZE_D_OUT), dtype=tl.float32)

        for _ in tl.range(0, tl.cdiv(group_size, BLOCK_SIZE_B)):
            tensor1_block = tl.load(
                tensor1_ptr + offs_tensor1,
                mask=(offs_tensor_b < b_end) & (offs_tensor1_din < D_IN),
                other=0.0,
            )
            tensor2_block = tl.load(
                tensor2_ptr + offs_tensor2,
                mask=(offs_tensor_b < b_end) & (offs_tensor2_dout < D_OUT),
                other=0.0,
            )

            accumulator = tl.dot(
                tensor1_block.T,
                tensor2_block,
                acc=accumulator,
                input_precision="tf32x3",
            )
            offs_tensor_b += BLOCK_SIZE_B
            offs_tensor1 += BLOCK_SIZE_B * stride_tensor1_b
            offs_tensor2 += BLOCK_SIZE_B * stride_tensor2_b

        accumulator = accumulator.to(output_ptr.dtype.element_ty)
        offset_output_din = (pid_din * BLOCK_SIZE_D_IN + tl.arange(0, BLOCK_SIZE_D_IN))[
            :, None
        ]
        offset_output_dout = (
            pid_dout * BLOCK_SIZE_D_OUT + tl.arange(0, BLOCK_SIZE_D_OUT)
        )[None, :]
        output_ptrs = (
            output_ptr
            + expert_idx * stride_output_e
            + offset_output_din * stride_output_din
            + offset_output_dout * stride_output_dout
        )
        output_mask = (offset_output_din < D_IN) & (offset_output_dout < D_OUT)
        tl.store(output_ptrs, accumulator, mask=output_mask)
        b_start += group_size
