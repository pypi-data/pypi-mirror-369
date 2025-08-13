from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional

import torch as _torch

from tamm._adapters_v1 import LayerAdapter as _LayerAdapter
from tamm._adapters_v1.layer_adapters.common import AdapterMode as _AdapterMode
from tamm._adapters_v1.layer_adapters.common import (
    AdapterWithExtraInputs as _AdapterWithExtraInputs,
)
from tamm._adapters_v1.layer_adapters.common import _validate_adapters


class SoftMixingLoRA(_AdapterWithExtraInputs):
    """
    Applies a mixture of multiple LoRA adapters in parallel to the
    adapted layer, such that the output of the adapted layer is:

    output = adapted_layer(input) + lora_0(weight[:, 0] * inputs) +
        lora_1(weight[:, 1] * inputs) + lora_2(weight[:, 2] * inputs) + ...

    where weight is a m x n tensor where m is equal to the batch size of inputs
    and n is equal to the number of LoRA adapters being applied together.
    """

    extra_input_names: _List[str] = ["adapter_input_weights"]

    def __init__(
        self,
        adapters: _Dict[str, _LayerAdapter],
    ):
        super().__init__()
        _validate_adapters(adapters)
        self.register_child_adapters(adapters)
        self.adapters = self._child_adapters

    def forward(
        self,
        mode: _AdapterMode,
        *,
        args: _Any,
        kwargs: _Any,
        transformed_args: _Any,
        transformed_kwargs: _Any,
        outputs: _Any,
        adapter_input_weights: _Optional[_torch.Tensor] = None,
    ):
        if mode is _AdapterMode.TRANSFORM_INPUTS:
            return self._transform_inputs(args=args, kwargs=kwargs)
        return self._transform_outputs(
            args=args,
            kwargs=kwargs,
            transformed_args=transformed_args,
            transformed_kwargs=transformed_kwargs,
            outputs=outputs,
            adapter_input_weights=adapter_input_weights,
        )

    def _transform_outputs(
        self,
        *,
        args: _Any,
        kwargs: _Any,
        transformed_args: _Any,
        transformed_kwargs: _Any,
        outputs: _Any,
        adapter_input_weights: _Optional[_torch.Tensor] = None,
    ):
        if not isinstance(transformed_args, tuple):
            raise TypeError("SoftMixingLoRA expects a tuple for transformed_args")
        if len(transformed_args) != 1:
            raise ValueError("SoftMixingLoRA expects transformed_args of length 1")
        x = transformed_args[0]

        ad_idx = 0
        for adapter in self.adapters.values():
            input_weight = adapter_input_weights[:, ad_idx].reshape(
                -1, *([1] * (x.ndim - 1))
            )
            outputs = adapter(
                mode=_AdapterMode.TRANSFORM_OUTPUTS,
                args=args,
                kwargs=kwargs,
                transformed_args=(input_weight * x,),
                transformed_kwargs=transformed_kwargs,
                outputs=outputs,
            )
            ad_idx += 1
        return outputs
