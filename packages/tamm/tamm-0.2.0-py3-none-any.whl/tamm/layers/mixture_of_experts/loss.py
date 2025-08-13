"""
This module implements loss functions specific to mixture of experts layers.
"""


import torch as _torch

from tamm.layers.common import LayerMixin as _LayerMixin


class LoadBalanceLoss(_torch.nn.Module, _LayerMixin):
    """
    A differentiable load balancing loss for MoE routers.  For more details,
    see the `Switch Transformers paper <https://arxiv.org/abs/2101.03961>`__.
    This loss is normalized such that its value is ``1.0`` when the expert
    assignments and assignment probabilities are both uniform.
    """

    def __init__(self):
        super().__init__()

    def forward(
        self,
        expert_assignments: _torch.Tensor,
        assignment_probabilities: _torch.Tensor,
    ):
        """
        Computes and returns the loss value.

        Args:
            expert_assignments (:obj:`torch.Tensor`): An integer tensor that
                maps tokens to chosen experts.  The expected shape is
                ``(*batch_shape, seq_len, num_experts_per_token)``.
            assignment_probabilities (:obj:`torch.Tensor`): The output of the
                router's softmax op.  The expected shape is
                ``(*batch_shape, seq_len, num_experts)``.
        """

        num_experts = assignment_probabilities.size(-1)

        # pylint: disable-next=not-callable
        one_hot_assignments = _torch.nn.functional.one_hot(
            expert_assignments, num_classes=num_experts
        )  # (T, B, S, K, E)
        counts = one_hot_assignments.count_nonzero(dim=(-3, -2))  # (T, B, E)
        denom = one_hot_assignments.shape[-3:-1].numel()  # S * K

        soft_freqs = assignment_probabilities.mean(-2)  # (T, B, E)

        return _torch.mean(counts * soft_freqs) * (num_experts**2 / denom)


class RouterZLoss(_torch.nn.Module, _LayerMixin):
    """
    A loss function that penalizes large logits in MoE routers.  For more
    details, see the `ST-MoE paper <https://arxiv.org/abs/2202.08906>`__.
    """

    def __init__(self):
        super().__init__()

    def forward(self, logits: _torch.Tensor) -> _torch.Tensor:
        """
        Computes and returns the loss value.

        Args:
            logits (:obj:`torch.Tensor`): The input to the router's
                softmax op.  The expected shape is
                ``(*batch_shape, seq_len, num_experts)``.
        """

        tensor = _torch.logsumexp(logits, dim=-1)
        return tensor.square().mean()
