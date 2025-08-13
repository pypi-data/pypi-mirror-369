from typing import Dict as _Dict
from typing import Optional as _Optional

import torch as _torch

from tamm import _helpers
from tamm.layers import activation as _activation
from tamm.layers import basic as _basic
from tamm.layers import linear as _linear
from tamm.layers.common import ConfigurableLayerMixin as _ConfigurableLayerMixin
from tamm.layers.mixture_of_experts import loss as _loss
from tamm.layers.mixture_of_experts import sampler as _sampler
from tamm.utils import torch_utils as _torch_utils


@_torch_utils.torch_exportable_dataclass
class MixtureOfExpertsRouterOutput:
    """
    Result dataclass for :obj:`MixtureOfExpertsRouter` layers.

    Args:
        expert_assignments (:obj:`torch.Tensor`): An integer tensor that
            maps tokens to chosen experts.  The expected shape is
            ``(*batch_shape, seq_len, num_experts_per_token)``.
        assignment_weights (:obj:`torch.Tensor`): A floating point tensor with
            the same shape as ``expert_assignments``.  These are weights
            for combining expert outputs for each token.
        losses (:obj:`torch.Tensor`): A dictionary of scalar auxiliary
            losses for training router behavior.
    """

    expert_assignments: _torch.Tensor
    assignment_weights: _torch.Tensor
    losses: _Dict[str, _torch.Tensor]


class MixtureOfExpertsRouter(_torch.nn.Module, _ConfigurableLayerMixin):
    """
    A layer that computes expert assignments for each token. This layer is a
    sequence of the following child layers:

    * ``input_transform``
    * ``logits_cap`` (optional)
    * ``softmax``
    * ``sampler``

    It also computes logits and load balancing losses.
    """

    def __init__(
        self,
        *,
        input_transform,
        logits_cap=None,
        softmax,
        sampler,
        logits_loss=None,
        load_balance_loss=None,
        cast_dtype=_torch.float32,
    ):
        super().__init__()
        _helpers.append_children(
            self,
            input_transform=input_transform,
            logits_cap=logits_cap,
            softmax=softmax,
            sampler=sampler,
            logits_loss=logits_loss,
            load_balance_loss=load_balance_loss,
        )
        self.cast_dtype = cast_dtype

    def extra_repr(self):
        return f"cast_dtype={self.cast_dtype}"

    def forward(self, tensor: _torch.Tensor) -> MixtureOfExpertsRouterOutput:
        """
        Transforms hidden states into per-token expert assignments and weights.

        Args:
            tensor (:obj:`torch.Tensor`): Input hidden states with shape
                ``(*batch_shape, seq_len, hidden_dim)``.

        Returns:
            A :obj:`MixtureOfExpertsRouterOutput`.
        """

        losses = {}

        logits = self.input_transform(tensor)

        if self.cast_dtype is not None:
            logits = logits.type(self.cast_dtype)

        if self.logits_cap is not None:
            logits = self.logits_cap(logits)

        if self.logits_loss is not None:
            losses["logits_loss"] = self.logits_loss(logits)

        probabilities = self.softmax(logits)

        sampler_output = self.sampler(probabilities)

        if self.load_balance_loss is not None:
            losses["load_balance_loss"] = self.load_balance_loss(
                expert_assignments=sampler_output.expert_assignments,
                assignment_probabilities=probabilities,
            )

        return MixtureOfExpertsRouterOutput(
            expert_assignments=sampler_output.expert_assignments,
            assignment_weights=sampler_output.assignment_weights,
            losses=losses,
        )

    @classmethod
    def create_basic_builder(  # pylint: disable=arguments-differ
        cls,
        *,
        input_dim: int,
        num_experts: int,
        num_experts_per_token: int,
        logits_cap: _Optional[float] = None,
        include_logits_loss: bool = True,
        include_load_balance_loss: bool = True,
    ):
        """
        Configures a basic MoE router with top-k sampling.

        Args:
            input_dim (:obj:`int`): The hidden dimension of the input states.
            num_experts (:obj:`int`): The number of experts.
            num_experts_per_token (:obj:`int`): The number of experts to
                activate for each token.
            logits_cap (:obj:`float`, optional): An optional cap value for
                the magnitude of router logits.  If specified, the layer
                applies tanh soft-capping to the logits.  Defaults to
                ``None`` (no capping).
            include_logits_loss (:obj:`bool`, optional): A flag for including
                a :obj:`RouterZLoss` value in the layer's outputs.  Defaults
                to ``True``.
            include_load_balance_loss (:obj:`bool`, optional): A flag for
                including a :obj:`LoadBalanceLoss` value in the layer's
                outputs.  Defaults to ``True``.
        """

        kwargs = {}

        kwargs["input_transform"] = _linear.Linear.Builder(
            input_dim, num_experts, bias=False
        )

        if logits_cap is not None:
            kwargs["logits_cap"] = _basic.SoftCap.Builder(cap=logits_cap)

        kwargs["softmax"] = _activation.Softmax.Builder(dim=-1)

        kwargs["sampler"] = _sampler.TopKMixtureOfExpertsSampler.Builder(
            num_experts_per_token=num_experts_per_token
        )

        if include_logits_loss:
            kwargs["logits_loss"] = _loss.RouterZLoss.Builder()

        if include_load_balance_loss:
            kwargs["load_balance_loss"] = _loss.LoadBalanceLoss.Builder()

        return cls.Builder(**kwargs)
