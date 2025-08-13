import abc as _abc
import enum as _enum
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional

import torch as _torch

from tamm import _helpers
from tamm.utils import torch_utils as _torch_utils


@_torch_utils.torch_exportable_dataclass
class MixtureOfExpertsDispatchOutput:
    """
    A dataclass for holding the outputs of a :obj:`MixtureOfExpertsDispatcher` in
    dispatch mode.

    Args:
        experts_arg:  The first positional argument to the experts layer,
            typically a tensor containing dispatched tokens.  The type and shape
            of this object depends on the dispatcher type.
        experts_kwargs (:obj:`dict`): Keyword arguments to the experts layer.
            The contents may depend on the dispatcher type.
        combine_input: An auxiliary input for calling the dispatcher in combine
            mode (after computing the outputs of experts).
    """

    experts_arg: _Any

    experts_kwargs: _Dict[str, _Any]

    combine_input: _Any


class MixtureOfExpertsDispatcherForwardMode(str, _enum.Enum):
    """
    An :obj:`Enum` for specifying the forward mode of a
    :obj:`MixtureOfExpertsDispatcher`.
    """

    DISPATCH = "DISPATCH"
    """Dispatch tokens to the experts."""

    COMBINE = "COMBINE"
    """Combine outputs from the experts."""


class MixtureOfExpertsDispatcher(_torch.nn.Module, _abc.ABC):
    """
    Base class for MoE layers that dispatch inputs to experts and later combine outputs
    from the experts.

    Example:

        .. code-block:: python

            # Dispatch tokens:
            dispatch_output = dispatcher(
                inputs, mode="dispatch", expert_assignments=expert_assignments
            )

            # Compute expert outputs (interface depends on the dispatcher type):
            experts_output = experts(
                dispatch_output.experts_arg, **dispatch_output.experts_kwargs
            )

            # Combine expert outputs:
            hidden_states = dispatcher(
                experts_output,
                mode="combine",
                assignment_weights=assignment_weights,
                combine_input=dispatch_output.combine_input,
            )
    """

    def __init__(self):
        super().__init__()

    @_abc.abstractmethod
    def _dispatch(
        self, hidden_states: _torch.Tensor, *, expert_assignments: _torch.Tensor
    ) -> MixtureOfExpertsDispatchOutput:
        """
        Dispatches tokens to experts, returning a
        :obj:`MixtureOfExpertsDispatchOutput`.

        Args:
            hidden_states (:obj:`torch.Tensor`): Input hidden states with shape
                ``(*batch_dim, seq_len, hidden_dim)``.
            expert_assignments (:obj:`torch.Tensor`): An integer tensor with shape
                ``(*batch_dim, seq_len, num_experts_per_token)`` that contains the
                indices of the experts to evaluate for each token.
        """

    @_abc.abstractmethod
    def _combine(
        self,
        experts_output: _Any,
        *,
        assignment_weights: _torch.Tensor,
        combine_input: _Any,
    ) -> _torch.Tensor:
        """
        Combines the outputs of experts, returning a :obj:`torch.Tensor`.

        Args:
            experts_output: The output of the experts layer.  This is typically
                a tensor, but the type or shape may vary depending on the
                dispatcher subclass.
            assignment_weights (:obj:`torch.Tensor`): A floating point tensor with
                the same shape as ``expert_assignments`` from dispatch mode.
                These are weights for combining expert outputs.
            combine_input (:obj:`torch.Tensor`): Auxiliary combine inputs
                produced by the dispatch call.
        """

    def forward(
        self,
        inputs: _Any,
        *,
        mode: MixtureOfExpertsDispatcherForwardMode,
        expert_assignments: _Optional[_torch.Tensor] = None,
        assignment_weights: _Optional[_torch.Tensor] = None,
        combine_input: _Any = None,
    ):
        """
        Either dispatches tokens to experts (if in dispatch mode) or combines
        outputs from experts (if in combine mode).

        Args:
            inputs: In dispatch mode, these are the tensor inputs (hidden states)
                to the MoE layer.  In combine mode, these are the outputs of the
                experts layer.
            mode (:obj:`str` or :obj:`MixtureOfExpertsDispatcherForwardMode`): The
                mode (either ``"dispatch"`` or ``"combine"``).
            expert_assignments (:obj:`torch.Tensor`): For dispatch mode only. An
                integer tensor that maps tokens to chosen experts.  The expected
                shape is ``(*batch_shape, seq_len, num_experts_per_token)``.
            assignment_weights (:obj:`torch.Tensor`): For combine mode only.  A
                floating point tensor with the same shape as
                ``expert_assignments``.  These are weights for combining expert
                outputs.
            combine_input (:obj:`torch.Tensor`): For combine mode only.
                Auxiliary combine inputs produced by the dispatch call.
        """

        mode = _helpers.get_enum_member_from_name(
            MixtureOfExpertsDispatcherForwardMode, mode
        )

        if mode is MixtureOfExpertsDispatcherForwardMode.DISPATCH:
            return self._dispatch(inputs, expert_assignments=expert_assignments)

        if mode is MixtureOfExpertsDispatcherForwardMode.COMBINE:
            return self._combine(
                inputs,
                assignment_weights=assignment_weights,
                combine_input=combine_input,
            )

        raise RuntimeError(f"Mode {mode} not recognized")
