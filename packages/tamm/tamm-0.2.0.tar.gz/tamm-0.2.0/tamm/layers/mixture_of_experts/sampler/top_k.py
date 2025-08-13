import torch as _torch

from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.mixture_of_experts.sampler import common as _common


class TopKMixtureOfExpertsSampler(_common.MixtureOfExpertsSampler, _LayerMixin):
    """
    A deterministic sampler that for each token selects the ``k`` experts with
    largest probability.  To compute the expert weights, the layer re-normalizes
    the probabilities of chosen experts so that they sum to ``1``.

    Args:
        num_experts_per_token (:obj:`int`): The number of experts to select
            for each token (i.e., ``k``).
    """

    def __init__(self, num_experts_per_token: int):
        super().__init__()
        self.num_experts_per_token = num_experts_per_token

    def extra_repr(self):
        return f"num_experts_per_token={self.num_experts_per_token}"

    def forward(
        self, probabilities: _torch.Tensor
    ) -> _common.MixtureOfExpertsSamplerOutput:
        weights, assignments = _torch.topk(
            probabilities, k=self.num_experts_per_token, dim=-1
        )
        weights = weights / weights.sum(dim=-1, keepdim=True)
        return _common.MixtureOfExpertsSamplerOutput(
            expert_assignments=assignments, assignment_weights=weights
        )
