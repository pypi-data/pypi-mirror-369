import torch as _torch


def segment_matmul(segmented_input, group_sizes, weight):
    # Ensure that we're executing "vectorized segment matmul" (i.e: a PTT MoE activation layer)
    # A normal non-vectorized segment matmul can be performed with an explicit tracks=1.
    # input expected to be of shape (tracks, batch*seq*top_k, hidden_dim) in MoE case
    if len(segmented_input.shape) != 3:
        raise ValueError(
            "segment_matmul currently only accepts 3-dimensional inputs (parallel-track op)"
        )

    # For each track, perform segment matmul
    tracks = segmented_input.shape[0]
    group_sizes_list = group_sizes.tolist()
    track_results = []
    for track in range(tracks):
        # Following contains a list of tensors to pass to each expert, of length experts
        track_experts_tensors = _torch.split(
            segmented_input[track], group_sizes_list[track]
        )

        # Perform feedforward per expert
        for idx, expert_tensor in enumerate(track_experts_tensors):
            track_results.append(_torch.matmul(expert_tensor, weight[track, idx]))

    return _torch.cat(track_results).reshape((tracks, -1, weight.shape[-1]))
