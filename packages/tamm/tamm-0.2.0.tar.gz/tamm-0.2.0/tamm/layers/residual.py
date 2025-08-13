"""
layers.residual
---------------

This module implements layers for the ``residual_connection`` option of
:class:`tamm.layers.Sequential`.

.. autoclass:: tamm.layers.GatedActivationResidualConnection

.. autoclass:: tamm.layers.NormalizedResidualConnection

.. autoclass:: tamm.layers.ResidualAdd

.. autoclass:: tamm.layers.ResidualScaledAdd

.. autoclass:: tamm.layers.ShortcutAddActResidualConnection
"""

from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

from tamm import _helpers
from tamm.layers import activation as _activation
from tamm.layers import common as _layers_common
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class ResidualAdd(_nn.Module, _layers_common.LayerMixin):
    """
    A vanilla residual connection that adds a layer's input to its output.
    The forward function takes ``input`` and ``residual_input`` arguments
    and returns their sum.
    """

    def __init__(self):
        super().__init__()  # Needed because builder doesn't support *args

    def forward(
        self,
        input: _torch.Tensor,  # pylint: disable=redefined-builtin
        residual_input: _torch.Tensor,
    ) -> _torch.Tensor:
        return input + residual_input


class ShortcutAddActResidualConnection(_nn.Module, _layers_common.LayerMixin):
    """
    A residual connection that applies a shortcut transformation to the residual
    inputs, then adds the shortcut result to outputs, and finally applies an activation
    transform to the sum. Given ``input = sublayer(x)`` and ``residual_input = x``,
    this layer returns

    ::

        activation(input + shortcut(residual_input))

    The ``shortcut`` and ``activation`` layers are optional.

    Args:
        shortcut: The shortcut layer.  Defaults to ``None``.
        activation: Any valid argument to :func:`.create_activation_layer`.
            Defaults to ``None``.
    """

    def __init__(
        self,
        shortcut: _OptionalModuleOrBuilder = None,
        activation: _Optional[_activation.ActivationSpecType] = None,
    ):
        super().__init__()
        self.shortcut = _helpers.maybe_build_module(shortcut)
        self.activation = _activation.create_activation_layer(activation)

    # pylint: disable=redefined-builtin
    def forward(
        self,
        input: _torch.Tensor,
        residual_input: _torch.Tensor,
    ) -> _torch.Tensor:
        if self.shortcut is not None:
            residual_input = self.shortcut(residual_input)
        x = input + residual_input
        if self.activation is None:
            return x
        return self.activation(x)


class GatedActivationResidualConnection(_nn.Module, _layers_common.LayerMixin):
    """
    A residual connection that applies gated activation to the residual inputs (using
    the non-residual inputs for gating).

    Args:
        activation: Any argument to :func:`.create_activation_layer` that
            specifies a gated activation.
    """

    def __init__(self, activation: _activation.ActivationSpecType):
        super().__init__()
        self.activation = _activation.create_activation_layer(activation)

    # pylint: disable=redefined-builtin
    def forward(
        self,
        input: _torch.Tensor,
        residual_input: _torch.Tensor,
    ) -> _torch.Tensor:
        return self.activation(gate_input=input, input=residual_input)


class ResidualScaledAdd(_nn.Module, _layers_common.LayerMixin):
    """
    Module for implementing residual scaled connections.  The forward function takes
    ``input`` and ``residual_input`` arguments and returns their sum, scaled by their
    respective scaling factors.

    Args:
        scale (:obj:`float`): input scale factor.
        residual_scale (:obj:`float`): residual scale factor.
    """

    def __init__(self, scale: float = 1, residual_scale: float = 1):
        self.scale = scale
        self.residual_scale = residual_scale
        super().__init__()

    def forward(
        self,
        input: _torch.Tensor,  # pylint: disable=redefined-builtin
        residual_input: _torch.Tensor,
    ) -> _torch.Tensor:
        """
        Computes the scaled residual sum.

        Args:
            input (:obj:`torch.Tensor`): Input tensor.
            residual_input (:obj:`torch.Tensor`): Residual Input tensor.
        Returns:
            :obj:`torch.Tensor`: Scaled residual sum.
        """
        if self.residual_scale != 1:
            residual_input = self.residual_scale * residual_input
        return _torch.add(residual_input, input, alpha=self.scale)

    def extra_repr(self) -> str:
        return f"scale={self.scale}, residual_scale={self.residual_scale}"


class NormalizedResidualConnection(_nn.Module, _layers_common.LayerMixin):
    """
    A residual connection that applies post normalization and other norm variants.
    Given ``input = sublayer(x)`` and ``residual_input = x``, this layer computes

    ::

        post_norm(
            combine(
                pre_residual_norm(input), residual_input
            )
        )

    The ``combine`` layer defaults to :class:`.ResidualAdd`, and the norm layers
    are optional.

    Args:
        pre_residual_norm: An optional norm layer applied to the ``input`` (the
            output of a sublayer).  Defaults to ``None``.
        combine: A layer that combines ``input`` and ``residual_input`` args.
            Defaults to :class:`.ResidualAdd`.
        post_norm: An optional norm layer applied to the output of ``combine``.
            Defaults to ``None``.
    """

    def __init__(
        self,
        pre_residual_norm: _OptionalModuleOrBuilder = None,
        combine: _OptionalModuleOrBuilder = None,
        post_norm: _OptionalModuleOrBuilder = None,
    ):
        super().__init__()
        if combine is None:
            combine = ResidualAdd()
        _helpers.append_children(
            self,
            pre_residual_norm=pre_residual_norm,
            combine=combine,
            post_norm=post_norm,
        )

    def forward(
        self,
        input: _torch.Tensor,  # pylint: disable=redefined-builtin
        residual_input: _torch.Tensor,
    ) -> _torch.Tensor:
        if self.pre_residual_norm is not None:
            input = self.pre_residual_norm(input)
        x = self.combine(input, residual_input)
        if self.post_norm is not None:
            x = self.post_norm(x)
        return x


def _maybe_create_residual_add_builder(
    *,
    apply_residual_add: bool,
    apply_pre_residual_norm: bool,
    apply_post_norm: bool,
    norm: _layers_common.LayerBuilder,
) -> _Union[None, _layers_common.LayerBuilder]:
    """
    A helper function for creating (possibly normalized) residual add layers.
    Raises :obj:`RuntimeError` if either ``apply_pre_residual_norm`` or
    ``apply_post_norm`` are ``True`` when ``apply_residual_add`` is ``False``.
    Otherwise returns ``None`` if ``apply_residual_add`` is ``False`` and
    a residual connection builder if it is ``True``.
    """
    if apply_pre_residual_norm or apply_post_norm:
        if not apply_residual_add:
            raise ValueError(
                "apply_pre_residual_norm and apply_post_norm are not supported "
                "without apply_residual_add"
            )
        builder = NormalizedResidualConnection.Builder()
        if apply_pre_residual_norm:
            builder.pre_residual_norm = norm
        if apply_post_norm:
            builder.post_norm = norm
        return builder
    return ResidualAdd.Builder() if apply_residual_add else None
