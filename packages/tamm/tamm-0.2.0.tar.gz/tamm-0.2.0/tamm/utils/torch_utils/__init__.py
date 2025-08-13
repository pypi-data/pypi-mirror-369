"""
utils.torch_utils
=================

This module implements utilities for working with PyTorch.


Iteration tools
^^^^^^^^^^^^^^^

.. autofunction:: tamm.utils.torch_utils.iter_named_parameters_and_buffers_with_layers

.. autofunction:: tamm.utils.torch_utils.iter_named_parameters_and_buffers

.. autofunction:: tamm.utils.torch_utils.map_named_parameters_and_buffers


Parameter counting
^^^^^^^^^^^^^^^^^^

.. autofunction:: tamm.utils.torch_utils.get_num_params

.. autofunction:: tamm.utils.torch_utils.get_num_frozen_params

.. autofunction:: tamm.utils.torch_utils.get_num_trainable_params


Exportable dataclass
^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tamm.utils.torch_utils.torch_exportable_dataclass


Parameter tying
^^^^^^^^^^^^^^^

.. autoclass:: tamm.utils.torch_utils.TieableParamsDict
    :members: register_tied_parameter, get_tied_value
"""

from tamm.utils.torch_utils.exportable_dataclass import torch_exportable_dataclass
from tamm.utils.torch_utils.itertools import (
    iter_named_parameters_and_buffers,
    iter_named_parameters_and_buffers_with_layers,
    map_named_parameters_and_buffers,
)
from tamm.utils.torch_utils.num_params import (
    get_num_frozen_params,
    get_num_params,
    get_num_trainable_params,
)
from tamm.utils.torch_utils.tieable_params import TieableParamsDict
