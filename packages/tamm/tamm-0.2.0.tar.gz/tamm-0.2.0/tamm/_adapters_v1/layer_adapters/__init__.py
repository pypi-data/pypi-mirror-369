"""
adapters.layer_adapters
=======================

Common
^^^^^^

.. autoclass:: tamm.adapters.LayerAdapter
    :show-inheritance:
    :members:

Compositions
^^^^^^^^^^^^

.. autoclass:: tamm.adapters.layer_adapters.CompositeInputTransform
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_adapters.CompositeOutputTransform
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_adapters.AveragedInputTransforms
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_adapters.AveragedOutputTransforms
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_adapters.StackedInputTransforms
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_adapters.StackedOutputTransforms
    :show-inheritance:
    :members:

LoRA
^^^^

.. autoclass:: tamm.adapters.layer_adapters.LoRA
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_adapters.BatchedLoRA
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_adapters.LoRAFusedMultiOutputLinear
    :show-inheritance:
    :members:

.. autoclass:: tamm.adapters.layer_adapters.BatchedLoRAFusedMultiOutputLinear
    :show-inheritance:
    :members:
"""

from tamm._adapters_v1.layer_adapters.average import (
    AveragedInputTransforms,
    AveragedOutputTransforms,
)
from tamm._adapters_v1.layer_adapters.common import (
    CompositeInputTransform,
    CompositeOutputTransform,
    LayerAdapter,
    LayerAdapterConfig,
)
from tamm._adapters_v1.layer_adapters.lora import (
    BatchedLoRA,
    BatchedLoRAFusedMultiOutputLinear,
    LoRA,
    LoRAFusedMultiOutputLinear,
)
from tamm._adapters_v1.layer_adapters.stack import (
    StackedInputTransforms,
    StackedOutputTransforms,
)
