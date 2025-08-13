"""
layers.activation
^^^^^^^^^^^^^^^^^

This module implements activation functions.  These layers inherit from
`PyTorch activation layers <https://docs.pytorch.org/docs/stable/nn.html#non-linear-activations-weighted-sum-nonlinearity>`__
in most cases, and the PyTorch layers have additional documentation.


Helpers for activation layer creation
=====================================

.. autofunction:: tamm.layers.activation.create_activation_layer

.. autofunction:: tamm.layers.activation.create_activation_builder

.. autofunction:: tamm.layers.activation.is_activation_gated

.. autofunction:: tamm.layers.activation.list_activation_registry


Non-gated activation layers
===========================

.. autoclass:: tamm.layers.activation.Activation
    :members:
    :exclude-members: Builder

.. autoclass:: tamm.layers.CELU

.. autoclass:: tamm.layers.ELU

.. autoclass:: tamm.layers.GELU

.. autoclass:: tamm.layers.HardSigmoid

.. autoclass:: tamm.layers.HardSwish

.. autoclass:: tamm.layers.HardTanh

.. autoclass:: tamm.layers.LeakyReLU

.. autoclass:: tamm.layers.Mish

.. autoclass:: tamm.layers.PReLU

.. autoclass:: tamm.layers.QuickGELU

.. autoclass:: tamm.layers.ReLU

.. autoclass:: tamm.layers.ReLU6

.. autoclass:: tamm.layers.RReLU

.. autoclass:: tamm.layers.SELU

.. autoclass:: tamm.layers.Sigmoid

.. autoclass:: tamm.layers.SiLU

.. autoclass:: tamm.layers.Softmax

.. autoclass:: tamm.layers.Softplus

.. autoclass:: tamm.layers.SoftShrink

.. autoclass:: tamm.layers.Softsign

.. autoclass:: tamm.layers.Tanh

.. autoclass:: tamm.layers.TanhShrink

.. autoclass:: tamm.layers.LambdaActivation


Gated activation layers
=======================

.. autoclass:: tamm.layers.activation.GatedActivation
    :members:
    :exclude-members: Builder

.. autoclass:: tamm.layers.BilinearActivation

.. autoclass:: tamm.layers.GEGLU

.. autoclass:: tamm.layers.GLU

.. autoclass:: tamm.layers.ReGLU

.. autoclass:: tamm.layers.SwiGLU
"""

import abc as _abc
import inspect as _inspect
from typing import Callable as _Callable
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn
from torch.nn import functional as _F

from tamm.layers import common as _layers_common
from tamm.layers import functional as _tamm_F
from tamm.layers import lambda_layer as _lambda_layer
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.utils import registry as _registry_module

ActivationSpecType = _Union[
    str, list, tuple, _layers_common.LayerBuilder, _layers_common.ModuleConfig
]

_ACTIVATION_BUILDERS = _registry_module.Registry("Activation builders")


def _register_activation(cls, *, key, description=None):
    if description is not None:
        pass
    elif hasattr(cls, "__doc__"):
        description = cls.__doc__
    else:
        description = f"{cls.__name__} activation"
    if not hasattr(cls, "Builder"):
        raise RuntimeError(f"Cannot register activation because {cls} has no Builder")
    _ACTIVATION_BUILDERS.register(cls.Builder, key=key, description=description)


def create_activation_layer(
    spec: _Union[ActivationSpecType, None]
) -> _Union["Activation", None]:
    """
    Creates an activation layer from a variety of possible specification types.

    Args:
        spec: The specification for the activation.  If the arg is a valid key to the
            activation registry (``"relu"``, ``"gelu"``, ``"glu"``, or another string
            from :func:`.list_activation_registry`), then the function creates the
            layer from the registry and returns it.  The ``spec`` arg can also be
            an :class:`.Activation` instance, a :obj:`.LayerBuilder`,
            a :obj:`.ModuleConfig`, or the name of a function from
            :mod:`torch.nn.functional`.

    Returns:
        An :obj:`Activation` instance corresponding to ``spec``.  Returns ``None``
        if ``spec`` is ``None``.
    """
    if isinstance(spec, Activation):
        return spec
    builder = create_activation_builder(spec)
    if builder is None:
        return None
    return builder.build()


def create_activation_builder(
    spec: _Union[ActivationSpecType, None]
) -> _Union[_layers_common.LayerBuilder, None]:
    """
    Creates a :obj:`.LayerBuilder` for an activation layer from a variety of possible
    specification types.

    Args:
        spec: The specification for the activation.  If the arg is a valid key to the
            activation registry (see :func:`.list_activation_registry`), then the
            function creates the builder from the registry and returns it.  The ``spec``
            arg can also be (1) a :obj:`LayerBuilder` instance, in which case it
            becomes the returned object, (2) a :obj:`.ModuleConfig` instance, in which
            case the function returns a builder from the config, or (3) the name of a
            function from ``torch.nn.functional``, in which case the function returns
            a :obj:`LambdaActivation` builder that wraps that function.

    Returns:
        A :obj:`.LayerBuilder` corresponding to ``spec``.  Returns ``None`` if
        ``spec`` is ``None``.
    """

    if spec is None:
        return None
    if isinstance(spec, _layers_common.LayerBuilder):
        return spec
    if isinstance(spec, _layers_common.ModuleConfig):
        return spec.create_builder()
    if _ACTIVATION_BUILDERS.is_valid_key(spec):
        return _ACTIVATION_BUILDERS.create(spec)
    is_torch_functional_name = isinstance(spec, str) and hasattr(_F, spec)
    if is_torch_functional_name:
        return LambdaActivation.Builder(spec)
    return _ACTIVATION_BUILDERS.create(spec)


def is_activation_gated(spec: _Union[ActivationSpecType, None]) -> bool:
    """
    Determines whether an activation is gated.

    Args:
        spec: The specification for the activation (the same as the argument
            to :func:`create_activation_layer`).

    Returns:
        ``True`` if the activation is gated and ``False`` otherwise.
    """
    if isinstance(spec, Activation):
        return spec.is_gated
    if spec is None:
        return False
    if _ACTIVATION_BUILDERS.is_valid_key(spec):
        layer_builder_cls = _ACTIVATION_BUILDERS.get_factory_fn(spec)
        if hasattr(layer_builder_cls, "_CALLABLE"):
            layer_cls = layer_builder_cls._CALLABLE
        else:
            layer_cls = None
        if _inspect.isclass(layer_cls) and issubclass(layer_cls, GatedActivation):
            return True
        if _inspect.isclass(layer_cls) and issubclass(layer_cls, Activation):
            return False
    layer = create_activation_layer(spec)
    return layer.is_gated


def list_activation_registry() -> _List[str]:
    """
    Returns a list of keys for registered activation types
    (``relu``, ``gelu``, ``glu``, etc.).
    """
    return _ACTIVATION_BUILDERS.list()


class Activation(_nn.Module, _abc.ABC, _LayerMixin):
    """Base class for activation layers."""

    def __init__(self):
        super().__init__()  # needed to remove nn.Module args from tamm Builder

    def __init_subclass__(cls, key=None, description=None, **kwargs):
        """Automatically register subclasses that provide a key."""
        super().__init_subclass__(**kwargs)
        if key is None or not hasattr(cls, "Builder"):
            return
        _register_activation(cls, key=key)

    @property
    def is_gated(self):
        """
        A flag with value ``True`` if the layer expects two tensors (with the same
        shape) as input and ``False`` otherwise.
        """
        return False

    @_abc.abstractmethod
    # pylint: disable-next=all
    def forward(self, input: _torch.Tensor) -> _torch.Tensor:
        """Subclasses implement forward."""


class LambdaActivation(_lambda_layer.Lambda, Activation):
    """
    Activation layer that wraps a callable function for :meth:`forward`.

    Args:
        function (:obj:`Callable` or :obj:`str`): A callable function that takes
            inputs to the forward function and returns the output of forward.
            This can also be a :obj:`str` corresponding to a function from
            :obj:`torch.nn.functional`.
    """

    def __init__(self, function: _Union[str, _Callable]):
        Activation.__init__(self)
        if isinstance(function, str):
            if not hasattr(_torch.nn.functional, function):
                raise ValueError(
                    f"Function '{function}' is not a member of torch.nn.functional"
                )
            function = getattr(_torch.nn.functional, function)
        _lambda_layer.Lambda.__init__(self, function)


class GatedActivation(Activation):
    """
    Base class for gated activation layers.  Gated activations receive a second
    input for gating.
    """

    @property
    def is_gated(self):
        """Returns ``True``."""
        return True

    @_abc.abstractmethod
    # pylint: disable-next=all
    def forward(self, gate_input: _torch.Tensor, input: _torch.Tensor) -> _torch.Tensor:
        """Subclasses implement forward."""


class CELU(_nn.CELU, Activation, key="celu"):
    """CELU activation."""

    def __init__(self, alpha: float = 1.0):
        Activation.__init__(self)
        _nn.CELU.__init__(self, alpha=alpha)


class ELU(_nn.ELU, Activation, key="elu"):
    """ELU activation."""

    def __init__(self, alpha: float = 1.0):
        Activation.__init__(self)
        _nn.ELU.__init__(self, alpha=alpha)


class GELU(_nn.GELU, Activation, key="gelu"):
    """GELU activation with tanh approximation by default."""

    def __init__(self, approximate="tanh"):
        Activation.__init__(self)
        _nn.GELU.__init__(self, approximate=approximate)


class HardSigmoid(_nn.Hardsigmoid, Activation, key="hard_sigmoid"):
    """Hard sigmoid activation."""

    def __init__(self):
        Activation.__init__(self)
        _nn.Hardsigmoid.__init__(self)


class HardSwish(_nn.Hardswish, Activation, key="hard_swish"):
    """Hard swish activation."""

    def __init__(self):
        Activation.__init__(self)
        _nn.Hardswish.__init__(self)


class HardTanh(_nn.Hardtanh, Activation, key="hard_tanh"):
    """Hard tanh activation."""

    def __init__(self, min_val: float = -1.0, max_val: float = 1.0):
        Activation.__init__(self)
        _nn.Hardtanh.__init__(self, min_val=min_val, max_val=max_val)


class LeakyReLU(_nn.LeakyReLU, Activation, key="leaky_relu"):
    """Leaky ReLU activation."""

    def __init__(self, negative_slope: float = 0.01):
        Activation.__init__(self)
        _nn.LeakyReLU.__init__(self, negative_slope=negative_slope)


class Mish(_nn.Mish, Activation, key="mish"):
    """Mish activation."""

    def __init__(self):
        Activation.__init__(self)
        _nn.Mish.__init__(self)


class PReLU(_nn.PReLU, Activation, key="prelu"):
    """PReLU activation."""

    def __init__(
        self, num_parameters: int = 1, init: float = 0.25, device=None, dtype=None
    ):
        Activation.__init__(self)
        _nn.PReLU.__init__(
            self, num_parameters=num_parameters, init=init, device=device, dtype=dtype
        )


class QuickGELU(Activation, key="quick_gelu"):
    """
    Quick GELU activation, which approximates GELU using ``x * sigmoid(1.702 * x)``.
    """

    def forward(self, input):  # pylint: disable=all
        return input * _torch.sigmoid(1.702 * input)


class ReLU(_nn.ReLU, Activation, key="relu"):
    """ReLU activation."""

    def __init__(self):
        Activation.__init__(self)
        _nn.ReLU.__init__(self)


class ReLU6(_nn.ReLU6, Activation, key="relu6"):
    """ReLU6 activation."""

    def __init__(self):
        Activation.__init__(self)
        _nn.ReLU6.__init__(self)


class RReLU(_nn.RReLU, Activation, key="rrelu"):
    """Randomized leaky ReLU activation."""

    def __init__(self, lower: float = 0.125, upper: float = 0.3333333333333333):
        Activation.__init__(self)
        _nn.RReLU.__init__(self, lower=lower, upper=upper)


class SELU(_nn.SELU, Activation, key="selu"):
    """SELU activation."""

    def __init__(self):
        Activation.__init__(self)
        _nn.SELU.__init__(self)


class SiLU(_nn.SiLU, Activation, key="silu"):
    """SiLU activation."""

    def __init__(self):
        Activation.__init__(self)
        _nn.SiLU.__init__(self)


_register_activation(SiLU, key="swish", description="Alias of silu")


class Sigmoid(_nn.Sigmoid, Activation, key="sigmoid"):
    """Sigmoid activation."""

    def __init__(self):
        Activation.__init__(self)
        _nn.Sigmoid.__init__(self)


class Softmax(_nn.Softmax, Activation, key="softmax"):
    """Softmax activation."""

    def __init__(self, dim: _Optional[int] = None):
        Activation.__init__(self)
        _nn.Softmax.__init__(self, dim=dim)


class Softplus(_nn.Softplus, Activation, key="softplus"):
    """Softplus activation."""

    def __init__(self, beta: float = 1.0, threshold: float = 20.0):
        Activation.__init__(self)
        _nn.Softplus.__init__(self, beta=beta, threshold=threshold)


class SoftShrink(_nn.Softshrink, Activation, key="soft_shrink"):
    """Soft shrink activation."""

    def __init__(self, lambd: float = 0.5):
        Activation.__init__(self)
        _nn.Softshrink.__init__(self, lambd=lambd)


class Softsign(_nn.Softsign, Activation, key="softsign"):
    """Softsign activation."""

    def __init__(self):
        Activation.__init__(self)
        _nn.Softsign.__init__(self)


class Tanh(_nn.Tanh, Activation, key="tanh"):
    """Tanh activation."""

    def __init__(self):
        Activation.__init__(self)
        _nn.Tanh.__init__(self)


class TanhShrink(_nn.Tanhshrink, Activation, key="tanh_shrink"):
    """Tanh shrink activation."""

    def __init__(self):
        Activation.__init__(self)
        _nn.Tanhshrink.__init__(self)


class GEGLU(GatedActivation, key="geglu"):
    """Gated activation with GELU for gating."""

    def __init__(self, approximate="tanh"):
        Activation.__init__(self)
        self.approximate = approximate

    # pylint: disable-next=all
    def forward(self, gate_input, input):
        return _tamm_F.geglu(gate_input, input, approximate=self.approximate)


class BilinearActivation(GatedActivation, key="bilinear"):
    """Gated activation that uses the identity function for gating."""

    # pylint: disable-next=all
    def forward(self, gate_input, input):
        return input * gate_input


class GLU(GatedActivation, key="glu"):
    """Gated activation that uses the sigmoid function for gating."""

    # pylint: disable-next=all
    def forward(self, gate_input, input):
        return input * _torch.sigmoid(gate_input)


class ReGLU(GatedActivation, key="reglu"):
    """Gated activation with ReLU for gating."""

    # pylint: disable-next=all
    def forward(self, gate_input, input):
        return _tamm_F.reglu(gate_input, input)


class SwiGLU(GatedActivation, key="swiglu"):
    """Gated activation with Swish (SiLU) for gating."""

    # pylint: disable-next=all
    def forward(self, gate_input, input):
        return _tamm_F.swiglu(gate_input, input)


_register_activation(SwiGLU, key="swi_glu", description="Alias of swiglu (deprecated)")
