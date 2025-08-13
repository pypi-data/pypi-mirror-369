import torch as _torch

from tamm import _adapters_v1, _helpers
from tamm.layers import feed_forward as _feed_forward
from tamm.layers import side_outputs as _side_outputs
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class MixtureOfExperts(_torch.nn.Module, _LayerMixin):
    """
    A general mixture of experts layer.  This layer routes inputs, dispatches them,
    computes expert outputs, and then combines the results. The layer also supports
    optional norm (applied to the inputs), dropout (applied to the combined outputs),
    and residual connection (applied to the final outputs) transforms.

    Args:
        norm: A norm builder (optional).
        router: A :obj:`.MixtureOfExpertsRouter` builder.
        dispatcher: A :obj:`.MixtureOfExpertsDispatcher` builder.
        experts: A builder for the experts layer.  This layer must be compatible
            with the dispatcher (i.e., accept as inputs the ``experts_arg`` and
            ``experts_kwargs`` from the dispatcher, which depend on the
            dispatcher type).
        output_dropout: A :class:`.Dropout` builder (optional).
        residual_connection: A builder for a residual layer, such as
            :class:`.ResidualAdd` (optional).
        output_expert_assignments (:obj:`bool`): Flag that when ``True`` results in the
            inclusion of per token expert assignments as side outputs. Defaults to ``False``.
    """

    def __init__(
        self,
        norm: _OptionalModuleOrBuilder,
        router: _ModuleOrBuilder,
        dispatcher: _ModuleOrBuilder,
        experts: _ModuleOrBuilder,
        output_dropout: _OptionalModuleOrBuilder,
        residual_connection: _OptionalModuleOrBuilder,
        output_expert_assignments: bool = False,
    ):
        super().__init__()
        _helpers.append_children(
            self,
            norm=norm,
            router=router,
            dispatcher=dispatcher,
            experts=experts,
            output_dropout=output_dropout,
            residual_connection=residual_connection,
        )
        self._mark_adaptable_layers()
        self.output_expert_assignments = output_expert_assignments

    def _mark_adaptable_layers(self):
        if isinstance(self.experts, _feed_forward.TransformerFeedForward):
            _adapters_v1.layer_annotations.unannotate_layer(
                self.experts.output_transform
            )
            _adapters_v1.annotate_layer(
                self.experts.output_transform,
                [("MoEFeedForwardOutputTransform",)],
            )

            layers = (
                [
                    self.experts.hidden_transform.linear_0,
                    self.experts.hidden_transform.linear_1,
                ]
                if self.experts.activation.is_gated
                else [self.experts.hidden_transform]
            )

            for layer in layers:
                _adapters_v1.layer_annotations.unannotate_layer(layer)
                _adapters_v1.annotate_layer(
                    layer,
                    [("MoEFeedForwardHiddenTransform",)],
                )

    # pylint: disable-next=redefined-builtin
    def forward(self, input: _torch.Tensor) -> _torch.Tensor:
        """
        Args:
            input (:obj:`torch.Tensor`): Input hidden states, typically with shape
                ``(batch_size, seq_len, hidden_dim)`` for transformer models.

        Returns:
            A :obj:`torch.Tensor` or :obj:`OutputWithSideOutputs` (if the output
            contains auxiliary losses).  The main tensor output is the combined
            expert outputs.
        """

        x = input

        if self.norm is not None:
            x = self.norm(x)

        router_out = self.router(x)

        dispatch_out = self.dispatcher(
            x, mode="dispatch", expert_assignments=router_out.expert_assignments
        )

        x = self.experts(dispatch_out.experts_arg, **dispatch_out.experts_kwargs)

        x = self.dispatcher(
            x,
            mode="combine",
            assignment_weights=router_out.assignment_weights,
            combine_input=dispatch_out.combine_input,
        )

        if self.output_dropout is not None:
            x = self.output_dropout(x)

        if self.residual_connection is not None:
            x = self.residual_connection(x, residual_input=input)

        output = x
        side_outputs = {}

        if router_out.losses:
            side_outputs = _side_outputs.merge_side_outputs(
                side_outputs, other_side_outputs=router_out.losses
            )

        if self.output_expert_assignments:
            side_outputs = _side_outputs.merge_side_outputs(
                side_outputs,
                other_side_outputs={
                    "expert_assignments": router_out.expert_assignments
                },
            )

        if side_outputs:
            output = _side_outputs.OutputWithSideOutputs(
                output, side_outputs=side_outputs
            )

        return output
