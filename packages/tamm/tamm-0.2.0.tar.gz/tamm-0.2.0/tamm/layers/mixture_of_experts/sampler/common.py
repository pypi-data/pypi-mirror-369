import abc as _abc

import torch as _torch

from tamm.utils import torch_utils as _torch_utils


@_torch_utils.torch_exportable_dataclass
class MixtureOfExpertsSamplerOutput:
    """
    Result dataclass for :obj:`MixtureOfExpertsSampler` layers.

    Args:
        expert_assignments (:obj:`torch.Tensor`): An integer tensor that
            maps tokens to chosen experts.  The expected shape is
            ``(*batch_shape, seq_len, num_experts_per_token)``.
        assignment_weights (:obj:`torch.Tensor`): A floating point tensor with
            the same shape as ``expert_assignments``.  These are weights
            for combining expert outputs for each token.
    """

    expert_assignments: _torch.Tensor
    assignment_weights: _torch.Tensor


class MixtureOfExpertsSampler(_torch.nn.Module, _abc.ABC):
    """An abstract base class for MoE samplers."""

    @_abc.abstractmethod
    def forward(self, probabilities: _torch.Tensor) -> MixtureOfExpertsSamplerOutput:
        """
        Transforms routing probabilities into weighted expert assignments.

        Args:
            probabilities (:obj:`torch.Tensor`): The output of the router's
                softmax op.  The expected shape is
                ``(*batch_shape, seq_len, num_experts)``.

        Returns a :obj:`MixtureOfExpertsSamplerOutput`.
        """
