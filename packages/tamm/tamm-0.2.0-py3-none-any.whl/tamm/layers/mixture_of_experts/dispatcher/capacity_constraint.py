import abc as _abc
import math as _math
from typing import Optional as _Optional

import torch as _torch

from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.utils import torch_utils as _torch_utils


@_torch_utils.torch_exportable_dataclass
class MixtureOfExpertsCapacityConstraintOutput:
    """
    A result dataclass for :obj:`MixtureOfExpertsCapacityConstraint` layers.

    Args:
        assignment_indicators (:obj:`torch.Tensor`): An updated indicator
            tensor with shape
            ``(*track_shape, *batch_shape, num_experts_per_token, num_experts)``.
            A value of ``1`` indicates a token assigned to an expert (and not
            dropped).
        capacity_per_expert (:obj:`int`): The total number of tokens to dispatch
            per expert.
    """

    assignment_indicators: _torch.Tensor
    capacity_per_expert: int


class MixtureOfExpertsCapacityConstraint(_torch.nn.Module, _abc.ABC):
    """
    A base class for capacity constraint layers in
    :obj:`CapacityConstrainedMixtureOfExpertsDispatcher` layers.
    """

    @_abc.abstractmethod
    def forward(
        self, assignment_indicators: _torch.Tensor, num_track_dims: int
    ) -> MixtureOfExpertsCapacityConstraintOutput:
        """
        Determines which tokens to drop as well as the token capacity of
        experts.

        Args:
            assignment_indicators (:obj:`torch.Tensor`): An indicator tensor
                with shape
                ``(*track_shape, *batch_shape, num_experts_per_token, num_experts)``.
                A value of ``1`` indicates a token assigned to an expert.
            num_track_dims (:obj:`int`): The number of track dimensions in
                ``assignment_indicators``.

        Returns:
            A :obj:`MixtureOfExpertsCapacityConstraintOutput`.
        """


class VanillaMixtureOfExpertsCapacityConstraint(
    MixtureOfExpertsCapacityConstraint, _LayerMixin
):
    """
    A basic capacity constraint that determines the capacity using a
    capacity factor.  This layer prioritizes tokens first based on the
    ``num_experts_per_token`` index, then the sequence index, and finally the
    batch index.  Tokens with larger indices are more likely to drop.

    Args:
        capacity_factor (:obj:`float`): The amount of expert capacity relative
            to the number of tokens.  A value of ``1`` results in the same
            capacity as the number of tokens, but it likely results in token
            dropping due to load imbalances.  Larger values result in more
            computation but less token dropping.
        capacity_factor_eval (:obj:`float`, optional): An optional capacity value
            for eval mode.  Defaults to ``capacity_factor``.
    """

    def __init__(
        self,
        *,
        capacity_factor: float,
        capacity_factor_eval: _Optional[float] = None,
    ):
        super().__init__()

        if capacity_factor_eval is None:
            capacity_factor_eval = capacity_factor
        self.capacity_factor = capacity_factor
        self.capacity_factor_eval = capacity_factor_eval

    def extra_repr(self):
        return (
            f"capacity_factor={self.capacity_factor}, "
            f"capacity_factor_eval={self.capacity_factor_eval}"
        )

    def forward(
        self, assignment_indicators: _torch.Tensor, num_track_dims: int
    ) -> MixtureOfExpertsCapacityConstraintOutput:
        # assignment_indicators has shape (T, B, S, K, E)

        assignment_indicators = assignment_indicators.swapdims(
            num_track_dims,
            -2
            # this prioritizes larger K indices for token dropping and avoids
            # prioritizing based on the batch index
        )  # (T, K, S, B, E)

        tokens_shape = assignment_indicators.shape[num_track_dims:-1]  # (K, S, B)
        assignment_indicators = assignment_indicators.flatten(
            start_dim=num_track_dims, end_dim=-2
        )  # (T, K*S*B, E)

        capacity_per_expert = self._get_capacity_per_expert(
            num_tokens=tokens_shape.numel(), num_experts=assignment_indicators.size(-1)
        )

        capacity_indices = _torch.cumsum(assignment_indicators, dim=-2)  # (T, K*S*B, E)
        capacity_indices *= assignment_indicators
        capacity_indices *= capacity_indices <= capacity_per_expert
        updated_indicators = capacity_indices.not_equal_(0)  # (T, K*S*B, E)

        updated_indicators = updated_indicators.unflatten(
            num_track_dims, tokens_shape
        )  # (T, K, S, B, E)

        updated_indicators = updated_indicators.swapdims(
            num_track_dims, -2
        )  # (T, B, S, K, E)

        return MixtureOfExpertsCapacityConstraintOutput(
            assignment_indicators=updated_indicators,
            capacity_per_expert=capacity_per_expert,
        )

    def _get_capacity_per_expert(self, *, num_tokens: int, num_experts: int):
        if self.training:
            capacity_factor = self.capacity_factor
        else:
            capacity_factor = self.capacity_factor_eval
        return _math.ceil(capacity_factor * num_tokens / num_experts)
