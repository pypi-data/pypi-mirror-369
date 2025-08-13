from typing import Dict as _Dict
from typing import Optional as _Optional

import torch as _torch

from tamm import _helpers
from tamm.layers import functional as _tamm_F
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.mixture_of_experts.dispatcher import common as _common
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder

# pylint: disable=duplicate-code


class CapacityConstrainedMixtureOfExpertsDispatcher(
    _common.MixtureOfExpertsDispatcher, _LayerMixin
):
    """
    A dispatcher that transforms inputs of shape
    ``(batch_size, seq_len, hidden_dim)`` into expert inputs with shape
    ``(num_experts, expert_capacity, hidden_dim)``.  A capacity constraint
    child layer determines the size of ``expert_capacity``. The dispatcher
    drops tokens when the number of tokens for an expert exceeds the capacity.

    This dispatcher is intended for experts implemented using batched matrix
    multiplies.

    The layer also supports multiple sets of experts (each set of size
    ``num_experts``) via the ``track_dim`` argument.  For this, the layer
    maps inputs with shape ``(num_tracks, batch_size, seq_len, hidden_dim)``
    to an experts input with shape
    ``(num_tracks, num_experts, expert_capacity, hidden_dim)``.

    Args:
        num_experts (:obj:`int`): The number of experts.  If ``track_dim``
            is not ``None``, this is the number of experts per track.
        capacity_constraint: A builder for a
            :obj:`MixtureOfExpertsCapacityConstraint` child layer.
        track_dim (:obj:`int`, optional): If using multiple sets (tracks) of
            experts, this is the index of the track dimension in the
            :meth:`forward` dispatching inputs.  Defaults to ``None``.
    """

    def __init__(
        self,
        num_experts: int,
        capacity_constraint: _ModuleOrBuilder,
        track_dim: _Optional[int] = None,
    ):
        super().__init__()
        self.num_experts = num_experts
        _helpers.append_children(self, capacity_constraint=capacity_constraint)
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
        # - E: num experts
        # - C: capacity per expert

        x = hidden_states

        if self.track_dim not in (0, None):
            x = x.movedim(self.track_dim, 0)  # (T, B, S, D)
            expert_assignments = expert_assignments.movedim(
                self.track_dim, 0
            )  # (T, B, S, K)

        one_hots = _torch.nn.functional.one_hot(  # pylint: disable=not-callable
            expert_assignments, self.num_experts
        )  # (T, B, S, K, E)

        constraint_out = self.capacity_constraint(
            one_hots, num_track_dims=self._num_track_dims
        )
        capacity_per_expert: int = constraint_out.capacity_per_expert
        capacity_per_expert = min(
            capacity_per_expert,
            expert_assignments.shape[self._num_track_dims :].numel(),
        )  # cap to total number of tokens

        capacity_indices = self._compute_capacity_indices(
            assignment_indicators=constraint_out.assignment_indicators,
            capacity_per_expert=capacity_per_expert,
        )  # (T, B, S, K, E)

        dispatch_indices = self._compute_dispatch_indices_from_capacity_indices(
            capacity_indices=capacity_indices,
            capacity_per_expert=capacity_per_expert,
        )  # (T, E*C)

        collapsed_indices = capacity_indices.max(dim=-1)[0]  # (T, B, S, K)
        dropped_assignments = collapsed_indices == -1
        combine_indices = (
            expert_assignments * capacity_per_expert + collapsed_indices
        )  # (T, B, S, K)
        combine_indices = combine_indices.masked_fill(dropped_assignments, 0)

        num_experts_per_token = expert_assignments.size(-1)
        x = _tamm_F.expand_dim(x, num_experts_per_token, dim=-2, unsqueeze=True)

        x = x.flatten(start_dim=self._num_track_dims, end_dim=-2)  # (T, B*S*K, D)
        experts_arg = _torch.take_along_dim(
            x,  # (T, B*S*K, D)
            dispatch_indices.unsqueeze(-1),  # (T, E*C, 1)
            dim=-2,
        )  # (T, E*C, D)
        experts_arg = experts_arg.unflatten(-2, (self.num_experts, -1))  # (T, E, C, D)

        return _common.MixtureOfExpertsDispatchOutput(
            experts_arg=experts_arg,
            experts_kwargs={},
            combine_input={
                "combine_indices": combine_indices,
                "dropped_assignments": dropped_assignments,
            },
        )

    def _compute_capacity_indices(self, *, assignment_indicators, capacity_per_expert):
        """
        Args:
            assignment_indicators (:obj:`torch.Tensor`): A tensor with shape
                ``(*track_shape, *batch_shape, num_experts_per_token, num_experts)``.
                A value of ``1`` indicates a token assigned to an expert.
            capacity_per_expert (:obj:`int`): The capacity per expert.

        Returns:
            An integer :obj:`torch.Tensor` with the same shape as the inputs.
            The tensor contains each token's capacity index for its expert.
            Values of ``-1`` indicate dropped tokens or tokens not assigned to an
            expert.
        """
        bsk_shape = assignment_indicators.shape[self._num_track_dims : -1]
        assignment_indicators = assignment_indicators.flatten(
            start_dim=self._num_track_dims, end_dim=-2
        )  # (T, B*S*K, E)
        indices = _tamm_F.cumsum(assignment_indicators, dim=-2)  # (T, B*S*K, E)
        indices *= assignment_indicators
        indices *= indices <= capacity_per_expert
        indices -= 1
        return indices.unflatten(-2, bsk_shape)  # (T, B, S, K, E)

    def _compute_dispatch_indices_from_capacity_indices(
        self, capacity_indices, capacity_per_expert
    ):
        """
        Args:
            capacity_indices: Integer tensor with shape (T, B, S, K, E).
                A value of -1 represents a non-token or dropped token.  A
                value >= 0 represents the capacity index for a token.
            capacity_per_expert: The max number of tokens to assign that
                each expert will receive.
        """
        capacity_indices = _torch.masked_fill(
            capacity_indices, capacity_indices < 0, capacity_per_expert
        )  # (T, B, S, K, E)
        capacity_indices = capacity_indices.flatten(
            start_dim=self._num_track_dims, end_dim=-2
        )  # (T, B*S*K, E)
        values, dispatch_indices = capacity_indices.topk(
            capacity_per_expert, dim=-2, largest=False
        )  # (T, C, E)
        dispatch_indices = dispatch_indices.masked_fill_(
            values >= capacity_per_expert, 0
        )  # (T, C, E)
        dispatch_indices = dispatch_indices.transpose(-1, -2)  # (T, E, C)
        return dispatch_indices.flatten(start_dim=-2)  # (T, E*C)

    def _combine(
        self,
        experts_output: _torch.Tensor,
        *,
        assignment_weights: _torch.Tensor,
        combine_input: _Dict[str, _torch.Tensor],
    ) -> _torch.Tensor:
        if self.track_dim not in (0, None):
            assignment_weights = assignment_weights.movedim(
                self.track_dim, 0
            )  # (T, B, S, K)

        combine_indices = combine_input["combine_indices"]
        dropped_assignments = combine_input["dropped_assignments"]

        experts_output = experts_output.flatten(
            start_dim=self._num_track_dims, end_dim=-2
        )  # (T, E*C, D)
        bsk_shape = combine_indices.shape[self._num_track_dims :]
        combine_indices = combine_indices.flatten(
            start_dim=self._num_track_dims
        )  # (T, B*S*K)
        x = _torch.take_along_dim(
            experts_output,  # (T, E*C, D)
            combine_indices.unsqueeze(-1),  # (T, B*S*K, 1)
            dim=-2,
        )  # (T, B*S*K, D)
        x = x.unflatten(-2, bsk_shape)  # (T, B, S, K, D)

        assignment_weights = _torch.masked_fill(
            assignment_weights, dropped_assignments, 0
        )
        assignment_weights = assignment_weights.to(x.dtype)

        x = _torch.linalg.vecdot(  # pylint: disable=not-callable
            x, assignment_weights.unsqueeze(-1), dim=-2
        )  # (T, B, S, D)

        if self.track_dim not in (0, None):
            x = x.movedim(0, self.track_dim)

        return x
