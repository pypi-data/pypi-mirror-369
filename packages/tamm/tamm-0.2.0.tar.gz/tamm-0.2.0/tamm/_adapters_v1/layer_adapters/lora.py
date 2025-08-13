import math as _math
from typing import Any as _Any
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

from tamm._adapters_v1.layer_adapters.common import LayerAdapter as _LayerAdapter
from tamm._adapters_v1.layer_adapters.common import (
    MergeableLayerAdapterMixin as _MergeableLayerAdapterMixin,
)
from tamm._adapters_v1.layer_adapters.common import (
    attach_config_class as _attach_config_class,
)
from tamm._adapters_v1.layer_annotations import (
    BatchedFusedLinearProjection as _BatchedFusedLinearProjection,
)
from tamm._adapters_v1.layer_annotations import (
    BatchedLinearProjection as _BatchedLinearProjection,
)
from tamm._adapters_v1.layer_annotations import (
    FusedLinearProjection as _FusedLinearProjection,
)
from tamm._adapters_v1.layer_annotations import LinearProjection as _LinearProjection
from tamm._adapters_v1.layer_annotations import (
    get_layer_annotations as _get_layer_annotations,
)


@_attach_config_class
class LoRA(_LayerAdapter, _MergeableLayerAdapterMixin):
    _supported_layer_annotations = (_LinearProjection,)

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        rank: int,
        alpha: _Optional[float] = None,
        dropout_p: float = 0,
        device: _Optional[_Union[_torch.device, str]] = None,
        dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim

        if rank <= 0:
            raise ValueError("rank must be a positive integer.")
        self.rank = int(rank)

        self.alpha = alpha if alpha is not None else self.rank
        self.dropout_p = dropout_p

        self.a_transpose = _nn.Parameter(
            _torch.empty(input_dim, rank, device=device, dtype=dtype)
        )
        self.b_transpose = _nn.Parameter(
            _torch.empty(rank, output_dim, device=device, dtype=dtype)
        )
        self.reset_parameters()

    def reset_parameters(self) -> None:
        super().reset_parameters()
        fan_in = self.a_transpose.size(0)
        _nn.init.normal_(self.a_transpose, std=_math.sqrt(1.0 / fan_in))
        _nn.init.zeros_(self.b_transpose)

    @property
    def scale(self) -> float:
        return self.alpha / self.rank

    def _transform_outputs(
        self,
        *,
        args: _Any,
        kwargs: _Any,
        transformed_args: _Any,
        transformed_kwargs: _Any,
        outputs: _torch.Tensor,
    ) -> _torch.Tensor:
        if not isinstance(transformed_args, tuple):
            raise TypeError(
                f"{self.__class__.__name__} expects a tuple for transformed_args"
            )
        if len(transformed_args) != 1:
            raise ValueError(
                f"{self.__class__.__name__} expects transformed_args of length 1"
            )
        x = transformed_args[0]

        if self.training and self.dropout_p > 0:
            x = _nn.functional.dropout(x, p=self.dropout_p)
        return self._transform_outputs_impl(x, outputs)

    def _transform_outputs_impl(
        self, x: _torch.Tensor, outputs: _torch.Tensor
    ) -> _torch.Tensor:
        x = x.flatten(end_dim=-2)
        x = _torch.matmul(x, self.a_transpose)

        batch_shape = outputs.shape[:-1]
        outputs = outputs.flatten(end_dim=-2)
        outputs = _torch.addmm(outputs, x, self.b_transpose, alpha=self.scale)
        return outputs.reshape(*batch_shape, -1)

    @_torch.no_grad()
    def merge_adapter(self, wrapped_module: _nn.Module):
        wrapped_module_type = _get_layer_annotations(
            wrapped_module, filter_types=self._supported_layer_annotations
        )
        if wrapped_module_type is None:
            raise ValueError(
                f"{self.__class__.__name__} adapter's merge function only works with layers annotated "
                f"with types: {self._supported_layer_annotations}."
            )
        weight_param = wrapped_module.get_parameter(
            wrapped_module_type[0].weight_param_name
        )
        self.merge_into_weight(weight_param)

    @_torch.no_grad()
    def merge_into_weight(self, weight: _torch.Tensor) -> None:
        a_transpose = self.a_transpose.type(weight.dtype)
        b_transpose = self.b_transpose.type(weight.dtype)
        weight.addmm_(b_transpose.T, a_transpose.T, alpha=self.scale)

    def extra_repr(self) -> str:
        return (
            f"out_features={self.output_dim}, "
            f"in_features={self.input_dim}, "
            f"rank={self.rank}, "
            f"alpha={self.alpha}, "
            f"dropout_p={self.dropout_p}"
        )


@_attach_config_class
class BatchedLoRA(LoRA):
    _supported_layer_annotations = (_BatchedLinearProjection,)

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        rank: int,
        vec_dim: _List[int],
        alpha: _Optional[float] = None,
        dropout_p: float = 0,
        device: _Optional[_Union[_torch.device, str]] = None,
        dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
    ):
        super().__init__(
            input_dim=input_dim,
            output_dim=output_dim,
            rank=rank,
            alpha=alpha,
            dropout_p=dropout_p,
            device=device,
            dtype=dtype,
        )
        self.vec_dim = vec_dim

        self.a_transpose = _nn.Parameter(
            _torch.empty(
                *vec_dim, self.input_dim, self.rank, device=device, dtype=dtype
            )
        )
        self.b_transpose = _nn.Parameter(
            _torch.empty(
                *vec_dim, self.rank, self.output_dim, device=device, dtype=dtype
            )
        )
        self.reset_parameters()

    def _transform_outputs_impl(
        self, x: _torch.Tensor, outputs: _torch.Tensor
    ) -> _torch.Tensor:
        return outputs + ((x @ self.a_transpose) * self.scale) @ self.b_transpose

    @_torch.no_grad()
    def merge_into_weight(self, weight: _torch.Tensor) -> None:
        weight.add_(
            (
                (self.a_transpose.to(dtype=weight.dtype) * self.scale)
                @ self.b_transpose.to(dtype=weight.dtype)
            )
        )

    def extra_repr(self) -> str:
        return (
            f"out_features={self.output_dim}, "
            f"in_features={self.input_dim}, "
            f"rank={self.rank}, "
            f"alpha={self.alpha}, "
            f"dropout_p={self.dropout_p}, "
            f"vec_dim={self.vec_dim}"
        )


class ZeroOutputModule(_nn.Module):
    def forward(self, *inputs) -> int:  # pylint: disable=unused-argument
        return 0

    def reset_parameters(self) -> None:
        pass


@_attach_config_class
class LoRAFusedMultiOutputLinear(_LayerAdapter, _MergeableLayerAdapterMixin):
    _supported_layer_annotations = (_FusedLinearProjection,)

    def __init__(
        self,
        input_dim: int,
        output_dims: _List[int],
        ranks: _List[int],
        alphas: _List[_Optional[float]] = (None, None, None),
        dropout_ps: _List[float] = (0.0, 0.0, 0.0),
        mask: _Tuple[bool, ...] = (True, False, True),
        device: _Optional[_Union[_torch.device, str]] = None,
        dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
    ):
        super().__init__()
        if not (
            len(output_dims)
            == len(ranks)
            == len(dropout_ps)
            == len(alphas)
            == len(mask)
        ):
            raise ValueError(
                f"Mismatch detected between number of output "
                f"dimensions: {len(output_dims)}, ranks: {len(ranks)}, "
                f"dropout_ps: {len(dropout_ps)}, "
                f"masks: {len(mask)} and alphas: {len(alphas)}"
            )

        self.input_dim = input_dim
        self.output_dims = output_dims
        self.mask = mask
        self.ranks = [
            rank if mask_value else None for rank, mask_value in zip(ranks, mask)
        ]
        self.alphas = [
            alpha if mask_value else None for alpha, mask_value in zip(alphas, mask)
        ]
        self.dropout_ps = [
            p if mask_value else None for p, mask_value in zip(dropout_ps, mask)
        ]
        self._create_child_lora_adapters(device=device, dtype=dtype)

    def _create_child_lora_adapters(
        self,
        device: _Optional[_Union[_torch.device, str]] = None,
        dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
    ):
        for idx, mask_value in enumerate(self.mask):
            layer_name = f"lora_{idx}"
            if not mask_value:
                setattr(self, layer_name, None)
                continue

            lora = LoRA(
                input_dim=self.input_dim,
                output_dim=self.output_dims[idx],
                rank=self.ranks[idx],
                alpha=self.alphas[idx],
                dropout_p=self.dropout_ps[idx],
                device=device,
                dtype=dtype,
            )
            self.register_child_adapter(layer_name, lora)

    @property
    def num_outputs(self):
        return len(self.output_dims)

    def _transform_outputs(
        self,
        *,
        args: _Any,
        kwargs: _Any,
        transformed_args: _Any,
        transformed_kwargs: _Any,
        outputs: _List[_torch.Tensor],
    ):
        if len(transformed_args) != 1:
            raise ValueError(
                f"LoRA layer for fused linear expected 1 input tensor but received "
                f"{len(transformed_args)}"
            )
        if len(outputs) != len(self.output_dims):
            raise ValueError(
                f"LoRA layer for fused linear expected f{self.num_outputs} outputs but "
                f"received {len(outputs)}"
            )
        return tuple(
            self._transform_single_output(
                lora_idx=idx,
                args=args,
                kwargs=kwargs,
                transformed_args=transformed_args,
                transformed_kwargs=transformed_kwargs,
                outputs=outputs[idx],
            )
            for idx in range(self.num_outputs)
        )

    def _transform_single_output(
        self, *, lora_idx, args, kwargs, transformed_args, transformed_kwargs, outputs
    ):
        lora = getattr(self, f"lora_{lora_idx}")
        if lora is None:
            return outputs
        return lora(
            mode="transform_outputs",
            args=args,
            kwargs=kwargs,
            transformed_args=transformed_args,
            transformed_kwargs=transformed_kwargs,
            outputs=outputs,
        )

    def _get_child_adapter_weight_params(
        self, weight_param: _torch.Tensor
    ) -> _List[_torch.Tensor]:
        return weight_param.split(self.output_dims)

    @_torch.no_grad()
    def merge_adapter(self, wrapped_module: _nn.Module):
        wrapped_module_type = _get_layer_annotations(
            wrapped_module, filter_types=self._supported_layer_annotations
        )
        if wrapped_module_type is None:
            raise ValueError(
                f"{self.__class__.__name__} adapter's merge function only works with "
                f"layers annotated with types: {self._supported_layer_annotations}."
            )
        weight_param = wrapped_module.get_parameter(
            wrapped_module_type[0].weight_param_name
        )
        weight_params = self._get_child_adapter_weight_params(weight_param)
        for idx, weight in enumerate(weight_params):
            lora = getattr(self, f"lora_{idx}")
            if lora is None:
                continue
            lora.merge_into_weight(weight)


@_attach_config_class
class BatchedLoRAFusedMultiOutputLinear(LoRAFusedMultiOutputLinear):
    _supported_layer_annotations = (_BatchedFusedLinearProjection,)

    def __init__(
        self,
        input_dim: int,
        output_dims: _List[int],
        ranks: _List[int],
        vec_dim: _List[int],
        alphas: _List[_Optional[float]] = (None, None, None),
        dropout_ps: _List[float] = (0.0, 0.0, 0.0),
        mask: _Tuple[bool, ...] = (True, False, True),
        device: _Optional[_Union[_torch.device, str]] = None,
        dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
    ):
        self.vec_dim = vec_dim
        super().__init__(
            input_dim=input_dim,
            output_dims=output_dims,
            ranks=ranks,
            alphas=alphas,
            dropout_ps=dropout_ps,
            mask=mask,
            device=device,
            dtype=dtype,
        )

    def _create_child_lora_adapters(
        self,
        device: _Optional[_Union[_torch.device, str]] = None,
        dtype: _Optional[_Union[_torch.dtype, str]] = _torch.float32,
    ):
        for idx, mask_value in enumerate(self.mask):
            layer_name = f"lora_{idx}"
            if not mask_value:
                setattr(self, layer_name, None)
                continue

            lora = BatchedLoRA(
                input_dim=self.input_dim,
                output_dim=self.output_dims[idx],
                rank=self.ranks[idx],
                vec_dim=self.vec_dim,
                alpha=self.alphas[idx],
                dropout_p=self.dropout_ps[idx],
                device=device,
                dtype=dtype,
            )
            self.register_child_adapter(layer_name, lora)

    def _get_child_adapter_weight_params(
        self, weight_param: _torch.Tensor
    ) -> _List[_torch.Tensor]:
        return weight_param.split(self.output_dims, dim=-1)
