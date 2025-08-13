"""
layers.mixture_of_experts
-------------------------

This module implements building blocks for mixture of experts layers.


Main layer
^^^^^^^^^^

.. autoclass:: tamm.layers.mixture_of_experts.MixtureOfExperts


Router
^^^^^^

.. autoclass:: tamm.layers.mixture_of_experts.MixtureOfExpertsRouter

.. autoclass:: tamm.layers.mixture_of_experts.router.MixtureOfExpertsRouterOutput


Samplers
^^^^^^^^

.. autoclass:: tamm.layers.mixture_of_experts.sampler.MixtureOfExpertsSampler
    :members: forward

.. autoclass:: tamm.layers.mixture_of_experts.sampler.MixtureOfExpertsSamplerOutput

.. autoclass:: tamm.layers.mixture_of_experts.TopKMixtureOfExpertsSampler
    :show-inheritance:


Dispatcher
^^^^^^^^^^

.. autoclass:: tamm.layers.mixture_of_experts.dispatcher.MixtureOfExpertsDispatcher
    :members: forward

.. autoclass:: tamm.layers.mixture_of_experts.DroplessMixtureOfExpertsDispatcher
    :show-inheritance:

.. autoclass:: tamm.layers.mixture_of_experts.CapacityConstrainedMixtureOfExpertsDispatcher
    :show-inheritance:

.. autoclass:: tamm.layers.mixture_of_experts.dispatcher.MixtureOfExpertsDispatcherForwardMode
    :members:

.. autoclass:: tamm.layers.mixture_of_experts.dispatcher.MixtureOfExpertsDispatchOutput
    :members:


Capacity constraint
^^^^^^^^^^^^^^^^^^^


.. autoclass:: tamm.layers.mixture_of_experts.dispatcher.MixtureOfExpertsCapacityConstraint
    :members: forward

.. autoclass:: tamm.layers.mixture_of_experts.VanillaMixtureOfExpertsCapacityConstraint
    :show-inheritance:

.. autoclass:: tamm.layers.mixture_of_experts.dispatcher.MixtureOfExpertsCapacityConstraintOutput


Losses
^^^^^^

.. autoclass:: tamm.layers.mixture_of_experts.LoadBalanceLoss
    :members: forward

.. autoclass:: tamm.layers.mixture_of_experts.RouterZLoss
    :members: forward
"""

from tamm.layers.mixture_of_experts.dispatcher import (
    CapacityConstrainedMixtureOfExpertsDispatcher,
    DroplessMixtureOfExpertsDispatcher,
    VanillaMixtureOfExpertsCapacityConstraint,
)
from tamm.layers.mixture_of_experts.loss import LoadBalanceLoss, RouterZLoss
from tamm.layers.mixture_of_experts.mixture_of_experts import MixtureOfExperts
from tamm.layers.mixture_of_experts.router import MixtureOfExpertsRouter
from tamm.layers.mixture_of_experts.sampler import TopKMixtureOfExpertsSampler

__all__ = [
    "CapacityConstrainedMixtureOfExpertsDispatcher",
    "DroplessMixtureOfExpertsDispatcher",
    "LoadBalanceLoss",
    "MixtureOfExpertsRouter",
    "MixtureOfExperts",
    "RouterZLoss",
    "TopKMixtureOfExpertsSampler",
    "VanillaMixtureOfExpertsCapacityConstraint",
]
