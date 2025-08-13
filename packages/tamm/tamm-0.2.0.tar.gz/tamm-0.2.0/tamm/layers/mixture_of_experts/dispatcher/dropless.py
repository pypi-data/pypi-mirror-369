from typing import Any as _Any
from typing import Optional as _Optional

import torch as _torch

from tamm.layers import functional as _tamm_F
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.mixture_of_experts.dispatcher import common as _common

# pylint: disable=line-too-long


class DroplessMixtureOfExpertsDispatcher(
    _common.MixtureOfExpertsDispatcher, _LayerMixin
):
    """
    A dispatcher that performs no token dropping.  The dispatch operation
    transforms inputs of shape ``(batch_size, seq_len, hidden_dim)`` into
    two tensors:

    1. Experts input hidden states with shape
       ``(batch_size * seq_len * num_experts_per_token, hidden_dim)``
       where the first dimension is sorted by expert index.
    2. A 1d tensor with length ``num_experts``, which contains the number of
       tokens routed to each expert.

    This dispatcher is intended for experts implemented using
    `grouped GEMM <https://developer.nvidia.com/blog/introducing-grouped-gemm-apis-in-cublas-and-more-performance-updates/#grouped_gemm_apis>`__.

    The layer also supports multiple sets of experts (each set of size
    ``num_experts``) via the ``track_dim`` argument.  For this, the layer
    maps inputs with shape ``(num_tracks, batch_size, seq_len, hidden_dim)``
    to an experts input with shape
    ``(num_tracks, batch_size * seq_len * num_experts_per_token, hidden_dim)``
    and group sizes with shape ``(num_tracks, num_experts)``.

    Args:
        num_experts (:obj:`int`): The number of experts.  If ``track_dim``
            is not ``None``, this is the number of experts per track.
        track_dim (:obj:`int`, optional): If using multiple sets (tracks) of
            experts, this is the index of the track dimension in the
            :meth:`forward` dispatching inputs.  Defaults to ``None``.
    """

    def __init__(self, num_experts: int, track_dim: _Optional[int] = None):
        super().__init__()
        self.num_experts = num_experts
        self.track_dim = track_dim

    def extra_repr(self):
        components = [f"num_experts={self.num_experts}"]
        if self.track_dim is not None:
            components.append(f"track_dim={self.track_dim}")
        return ", ".join(components)

    @property
    def _num_track_dims(self):
        return 0 if self.track_dim is None else 1

    def _dispatch(
        self, hidden_states: _torch.Tensor, *, expert_assignments: _torch.Tensor
    ) -> _common.MixtureOfExpertsDispatchOutput:
        # shorthand for shape comments:
        # - T: num tracks
        # - B: batch size
        # - S: sequence length
        # - D: hidden dim
        # - K: experts per token

        x = hidden_states

        if self.track_dim not in (0, None):
            x = x.movedim(self.track_dim, 0)  # (T, B, S, D)
            expert_assignments = expert_assignments.movedim(
                self.track_dim, 0
            )  # (T, B, S, K)

        num_experts_per_token = expert_assignments.size(-1)
        x = _tamm_F.expand_dim(x, num_experts_per_token, dim=-2, unsqueeze=True)
        expanded_hidden_states_shape = x.shape

        expert_assignments = expert_assignments.flatten(
            start_dim=self._num_track_dims
        )  # (T, B*S*K)
        indices = _torch.argsort(expert_assignments, dim=-1)

        x = x.flatten(start_dim=self._num_track_dims, end_dim=-2)  # (T, B*S*K, D)
        x = _torch.take_along_dim(x, indices[..., None], -2)  # (T, B*S*K, D)

        group_sizes = _torch.nn.functional.one_hot(  # pylint: disable=not-callable
            expert_assignments, num_classes=self.num_experts
        ).sum(dim=-2)

        combine_indices = _torch.argsort(indices, dim=-1)

        return _common.MixtureOfExpertsDispatchOutput(
            experts_arg=x,
            experts_kwargs={"group_sizes": group_sizes},
            combine_input={
                "combine_indices": combine_indices,
                "expanded_hidden_states_shape": expanded_hidden_states_shape,
            },
        )

    def _combine(
        self,
        experts_output: _torch.Tensor,
        *,
        assignment_weights: _torch.Tensor,
        combine_input: _Any,
    ) -> _torch.Tensor:
        combine_indices = combine_input["combine_indices"]
        expanded_hidden_states_shape = combine_input["expanded_hidden_states_shape"]

        if self.track_dim not in (0, None):
            assignment_weights = assignment_weights.movedim(
                self.track_dim, 0
            )  # (T, B, S, K)

        x = _torch.take_along_dim(
            experts_output, combine_indices[..., None], -2
        )  # (T, B*S*K, D)
        x = x.reshape(expanded_hidden_states_shape)  # (T, B, S, K, D)
        assignment_weights = assignment_weights.to(x.dtype)
        x = _torch.linalg.vecdot(  # pylint: disable=not-callable
            x, assignment_weights[..., None], dim=-2
        )  # (T, B, S, D)

        if self.track_dim not in (0, None):
            x = x.movedim(0, self.track_dim)

        return x
