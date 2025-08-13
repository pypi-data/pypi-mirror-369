"""
Similar to PyTorch `default <https://pytorch.org/docs/stable/tensor_attributes.html#>`_
``device`` which can be accessed via
:meth:`torch.get_default_device` and :meth:`torch.get_default_device`, |tamm| has
the following global defaults which may affect module creation.

* ``pretrained`` (default: ``False``)

Controls whether a model will be loaded with pretrained weights.

.. autofunction:: tamm.get_default_pretrained_flag
.. autofunction:: tamm.set_default_pretrained_flag
.. autofunction:: tamm.pretrained_flag_context

* ``freeze_params`` (default: :class:`OptionalBool`.NOTSET)

Controls whether module parameters are frozen when created. Default is NOTSET meaning
the builder will not change the state of ``require_grad`` (i.e., ``not freeze_params``)

.. autofunction:: tamm.get_default_freeze_params_flag
.. autofunction:: tamm.set_default_freeze_params_flag
.. autofunction:: tamm.freeze_params_flag_context

* ``first_token_generation`` (default: ``False``)

Indicates whether the model is currently generating the first token in a sequence.

.. autofunction:: tamm.get_first_token_generation_flag
.. autofunction:: tamm.first_token_generation_context

Context Resolvers
^^^^^^^^^^^^^^^^^
.. autofunction:: tamm.resolve_device
.. autofunction:: tamm.resolve_pretrained_flag
.. autofunction:: tamm.resolve_freeze_params

"""

from tamm.context_vars._first_token_generation import (
    first_token_generation_context,
    get_first_token_generation_flag,
)
from tamm.context_vars._freeze_params import (
    freeze_params_flag_context,
    get_default_freeze_params_flag,
    set_default_freeze_params_flag,
)
from tamm.context_vars._model_build_device import (
    get_model_build_device,
    model_build_device_context,
)
from tamm.context_vars._pretrained import (
    get_default_pretrained_flag,
    pretrained_flag_context,
    set_default_pretrained_flag,
)
from tamm.context_vars._resolvers import (
    resolve_device,
    resolve_freeze_params,
    resolve_pretrained_flag,
)

__all__ = [
    "get_model_build_device",
    "model_build_device_context",
    "resolve_device",
    "resolve_pretrained_flag",
    "resolve_freeze_params",
    "get_default_pretrained_flag",
    "set_default_pretrained_flag",
    "pretrained_flag_context",
    "get_default_freeze_params_flag",
    "set_default_freeze_params_flag",
    "freeze_params_flag_context",
    "get_first_token_generation_flag",
    "first_token_generation_context",
]
