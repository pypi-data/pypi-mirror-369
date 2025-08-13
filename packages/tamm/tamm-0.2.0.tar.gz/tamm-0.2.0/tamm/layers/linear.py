"""
This module provides variations of linear layers, including linear layers that output
multiple tensors and a linear layer with a weight tied to another module's parameter.
"""

import itertools as _itertools
import logging as _logging
from typing import List as _List
from typing import Optional as _Optional

import torch as _torch
import torch.nn as _nn
from torch.nn import functional as _F

from tamm.layers import functional as _tamm_F
from tamm.layers import init as _init
from tamm.layers import sequential as _sequential
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.utils import torch_utils as _torch_utils

_logger = _logging.getLogger(__name__)


class Linear(_nn.Linear, _LayerMixin):
    """
    Embedding layer with variance scaled init.
    """

    def forward(self, *args, **kwargs):
        # pylint: disable=W0246
        return super().forward(*args, **kwargs)

    def reset_parameters(self) -> None:
        _init.shape_normalized_normal_(self.weight, dim=1)
        if self.bias is not None:
            _nn.init.zeros_(self.bias)


class MultiOutputLinear(_nn.Module, _LayerMixin):
    """
    A linear layer that outputs multiple tensors given the same input.

    Args:
        input_dim (:obj:`int`): The input's dimension along its last axis.
        output_dims (:obj:`int`): A list of one or more output dimensions.
        bias (:obj:`bool`): Will the linear layers use a bias component or not.
    """

    def __init__(
        self,
        input_dim: int,
        output_dims: _List[int],
        bias: bool = False,
        *,
        vec_dim: _Optional[_List[int]] = None,
        device=None,
        dtype=None,
        override_linear_cls=None,
    ):
        super().__init__()
        self.output_dims = output_dims
        self.bias = bias

        # Handle vectorized
        self.vec_dim = vec_dim
        if vec_dim is None:
            linear_cls = Linear
            extra_kwargs = {}
        else:
            linear_cls = VectorizedLinear
            extra_kwargs = {"vec_dim": vec_dim}

        # Option for overriding the linear cls
        if override_linear_cls is not None:
            linear_cls = override_linear_cls

        for idx, output_dim in enumerate(output_dims):
            linear = linear_cls(
                input_dim,
                output_dim,
                bias=self.bias,
                device=device,
                dtype=dtype,
                **extra_kwargs,
            )
            self.register_module(f"linear_{idx}", linear)

    # pylint: disable-next=all
    def forward(self, input, **kwargs):
        return tuple(linear(input, **kwargs) for linear in self.children())

    def extra_repr(self) -> str:
        return f"out_features={self.output_dims}, bias={self.bias}"

    def _load_from_state_dict(self, state_dict, prefix, *args, **kwargs):
        """
        MultiOutputLinear and FusedMultiOutputLinear are interchangeable except for
        the state_dict format.  It is useful for users to have the option of swapping
        them because some adapters support one and not the other.  Here we override
        nn.Module._load_from_state_dict so that MultiOutputLinear can load state
        dicts from FusedMultiOutputLinear.  This needs to rely on PyTorch internals
        because PyTorch does not otherwise provide a way of extending load_state_dict.
        """
        self._adapt_state_dict_from_fused_format(state_dict, prefix=prefix)
        return super()._load_from_state_dict(state_dict, prefix, *args, **kwargs)

    def _adapt_state_dict_from_fused_format(self, state_dict, prefix=""):
        param_names = ["weight"]
        if self.bias:
            param_names.append("bias")

        for param_name in param_names:
            fused_param_key = f"{prefix}fused_linear.{param_name}"

            if fused_param_key not in state_dict:  # nothing to do for this param
                continue

            fused_param = state_dict[fused_param_key]

            if param_name == "weight":
                expected_shape = (sum(self.output_dims), self.linear_0.in_features)
            else:
                expected_shape = (sum(self.output_dims),)

            # stop processing if shape's off
            if fused_param.shape != expected_shape:
                return

            new_param_keys = [
                f"{prefix}linear_{idx}.{param_name}"
                for idx, _ in enumerate(self.output_dims)
            ]
            # Stop processing if any of the un-fused tensors exist in the state_dict
            for key in new_param_keys:
                if key in state_dict:
                    return

            _logger.debug(
                f"Mapping FusedMultiOutputLinear's {param_name} "
                f"to MultiOutputLinear format"
            )
            state_dict.pop(fused_param_key)
            split_weights = _torch.split(fused_param, self.output_dims)
            for key, weight in zip(new_param_keys, split_weights):
                state_dict[key] = weight


class FusedMultiOutputLinear(_nn.Module, _LayerMixin):
    """
    A :class:`nn.Module` for fusing multiple linear layers (with the same input dim) as
    a single linear layer.

    Args:
        input_dim (:obj:`int`): The input's dimension along its last axis.
        output_dims (:obj:`int`): A list of one or more output dimensions.
        bias (:obj:`bool`): Whether the linear layer uses a bias or not.
    """

    def __init__(
        self,
        input_dim: int,
        output_dims: _List[int],
        bias: bool = False,
        *,
        vec_dim: _Optional[_List[int]] = None,
        device=None,
        dtype=None,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dims = output_dims
        self.bias = bias

        # Handle vectorized
        self.vec_dim = vec_dim
        if vec_dim is None:
            linear_cls = Linear
            extra_kwargs = {}
        else:
            linear_cls = VectorizedLinear
            extra_kwargs = {"vec_dim": vec_dim}

        self.fused_linear = linear_cls(
            input_dim,
            sum(output_dims),
            bias=bias,
            device=device,
            dtype=dtype,
            **extra_kwargs,
        )

    # pylint: disable-next=all
    def forward(self, inp: _torch.Tensor):
        output = self.fused_linear(inp)
        return tuple(
            tensor.contiguous()
            for tensor in _torch.split(output, self.output_dims, dim=-1)
        )

    def extra_repr(self) -> str:
        return f"out_features={self.output_dims}, bias={self.bias}"

    def _load_from_state_dict(self, state_dict, prefix, *args, **kwargs):
        """
        MultiOutputLinear and FusedMultiOutputLinear are interchangeable except for
        the state_dict format.  It is useful for users to have the option of swapping
        them because some adapters support one and not the other.  Here we override
        nn.Module._load_from_state_dict so that FusedMultiOutputLinear can load state
        dicts from MultiOutputLinear.  This needs to rely on PyTorch internals because
        PyTorch does not otherwise provide a way of extending load_state_dict.
        """
        self.adapt_state_dict_from_unfused_format(
            state_dict, bias=self.bias, prefix=prefix
        )
        return super()._load_from_state_dict(state_dict, prefix, *args, **kwargs)

    @staticmethod
    def adapt_state_dict_from_unfused_format(state_dict, bias, prefix=""):
        weight_names = ["weight"]
        if bias:
            weight_names.append("bias")
        for weight_name in weight_names:
            matching_keys = []
            for idx in _itertools.count():
                key = f"{prefix}linear_{idx}.{weight_name}"
                if key not in state_dict:
                    break
                matching_keys.append(key)

            if len(matching_keys) > 0:
                _logger.debug(
                    f"Mapping MultiOutputLinear's {weight_name} "
                    f"to FusedMultiOutputLinear format"
                )
                tensors = [state_dict.pop(key) for key in matching_keys]
                fused_key = f"{prefix}fused_linear.{weight_name}"
                assert fused_key not in state_dict
                state_dict[f"{prefix}fused_linear.{weight_name}"] = _torch.cat(tensors)


class TiedWeightLinear(_nn.Module, _LayerMixin):
    """
    A replacement for :class:`nn.Linear` that uses a weight parameter from another
    :obj:`nn.Module`.

    Args:
        module (:obj:`nn.Module`): The module with the weight parameter.  The weight
            parameter should have shape ``(out_features, in_features)``.
        parameter_name (:obj:`str`): The name of the weight parameter registered on
            ``module``.  (The parameter must be accessible via
            ``getattr(module, parameter_name)``.)
    """

    _WEIGHT_NAME = "weight"

    def __init__(
        self,
        module: _nn.Module,
        parameter_name: str,
        transpose: bool = False,
    ):
        super().__init__()
        self._parameters = _torch_utils.TieableParamsDict(self._parameters)

        # Implementation note: We access the tied weight as an attribute of another
        # module rather than simply as a nn.Parameter due to FSDP behavior as of
        # Torch 2.0.  Specifically, FSDP replaces parameters on modules with sharded
        # parameters. Thus, parameters would become untied between modules unless we can
        # still access the new sharded parameter via the module's updated attribute.

        self._parameters.register_tied_parameter(
            name=self._WEIGHT_NAME,
            tied_module=module,
            tied_param_name=parameter_name,
            # This ensures that every time we access the param (for example
            # layer.state_dict()) we have the updated value from the tied module.
        )

        if len(self._weight_shape) != 2:
            raise RuntimeError(
                "TiedWeightLinear received a weight tensor with dim "
                f"{len(self._weight_shape)} (expected 2)"
            )

        self.transpose = transpose

        if self.transpose:
            self.in_features, self.out_features = self._weight_shape
        else:
            self.out_features, self.in_features = self._weight_shape

        self._maybe_register_deepspeed_external_param()

    @property
    def weight(self):
        # This property is almost not needed because nn.Module.__getattr__() will already
        # return the weight from _parameters.  However, this only happens when the weight
        # is a nn.Parameter, and FSDP sometimes replaces it with a vanilla torch.Tensor.
        # Adding this property ensures it still works when weight becomes a non-Param.
        return self._parameters.get_tied_value(self._WEIGHT_NAME)

    @property
    def _weight_shape(self):
        if hasattr(self.weight, "ds_shape"):  # special case to support deepspeed
            return self.weight.ds_shape
        return self.weight.shape

    def _maybe_register_deepspeed_external_param(self):
        if not hasattr(self.weight, "ds_id"):
            return
        try:
            from deepspeed import zero  # pylint: disable=all
        except Exception:
            _logger.debug(
                "TiedWeightLinear failed to import deepspeed to register its external param"
            )
            return

        zero.register_external_parameter(self, self.weight)
        _logger.debug(
            "TiedWeightLinear registered its weight as a deepspeed external param"
        )

    def _replicate_for_data_parallel(self):
        # torch DataParallel (which is not a common use case, since DDP is faster)
        # calls this method and sets _parameters to an empty dict.  In order to
        # ensure the replica still works, we need to reassign _parameters to a
        # TieableParamsDict
        replica = super()._replicate_for_data_parallel()
        replica._parameters = _torch_utils.TieableParamsDict(self._parameters)
        # pylint: disable-next=protected-access
        replica._parameters._tied_parameters = self._parameters._tied_parameters.copy()
        return replica

    def __setattr__(self, name, value):
        if name == self._WEIGHT_NAME:
            # As of torch 2.5, FSDP calls this to replace the param with a tensor.
            # We want to just ignore it and still use the param of the tied module.
            _logger.debug("Ignoring call to set weight of TiedWeightLinear layer")
            return
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if name == self._WEIGHT_NAME:
            # As of torch 2.5, FSDP calls this to replace the param with a tensor.
            # We want to just ignore it and still use the param of the tied module.
            _logger.debug("Ignoring call to delete weight of TiedWeightLinear layer")
            return
        super().__delattr__(name)

    # pylint: disable-next=all
    def forward(self, inp: _torch.Tensor) -> _torch.Tensor:
        # As of torch 2.5, using self.weight here causes issues with torch.compile
        weight = self._parameters.get_tied_value(self._WEIGHT_NAME)
        if self.transpose:
            weight = weight.transpose(-1, -2)
        return _F.linear(inp, weight)  # pylint: disable=not-callable

    def reset_parameters(self):
        pass

    def extra_repr(self) -> str:
        return f"in_features={self.in_features}, out_features={self.out_features}"


class TiedWeightLinearSequence(_sequential.Sequential):
    """
    A sequence of :class:`TiedWeightLinear` layers that share the same ``module``.

    Args:
        module (:obj:`nn.Module`):
    """

    def __init__(
        self,
        module: _nn.Module,
        parameter_names: _List[str],
        transpose_flags: _Optional[_List[bool]] = None,
    ):
        if transpose_flags is None:
            transpose_flags = [False] * len(parameter_names)

        named_layers = {}
        for idx, (name, transpose) in enumerate(zip(parameter_names, transpose_flags)):
            layer = TiedWeightLinear(
                module=module, parameter_name=name, transpose=transpose
            )
            named_layers[f"layer_{idx}"] = layer

        super().__init__(named_layers)


# Implementation of _vectorized_ Linear operations.
class VectorizedLinear(_LayerMixin, _nn.Module):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        vec_dim: _List[int] = (1,),
        bias: bool = False,
        *,
        device=None,
        dtype=None,
    ):
        # Same as Linear but vec_dim is a tuple/list of ints
        # that replicate the linear layer along these dimensions.
        #
        # Example: VectorizedLinear(3, 5, vec_dim=[1,8])
        # -> creates linear layer with weights of shape (1,8,3)
        # -> operator on `input` does input @ weights (bmm)
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.vec_dim = vec_dim

        weight_shape = tuple(vec_dim) + (in_features, out_features)
        self.weight = _nn.Parameter(_torch.empty(weight_shape, **factory_kwargs))

        if bias:
            bias_shape = tuple(vec_dim) + (out_features,)
            self.bias = _nn.Parameter(_torch.empty(bias_shape, **factory_kwargs))
        else:
            self.register_parameter("bias", None)

        self.reset_parameters()

    def reset_parameters(self) -> None:
        _init.shape_normalized_normal_(self.weight, dim=-2)
        if self.bias is not None:
            _nn.init.zeros_(self.bias)

    # pylint: disable=redefined-builtin
    def forward(self, input: _torch.Tensor) -> _torch.Tensor:
        # Optimize decode performance when batch > seqlen for ParallelTrack models.
        #
        # Specifically target input shapes of format [batch, tracks, seqlen, input_dim]
        # where weight shapes are of format [tracks, input_dim, output_dim]
        #
        # During decode, seqlen=1, while batch can be high; in this case, it's much faster
        # to swap batch and seqlen dimensions so that matrix-matrix multiplications are used.
        optimize_decode_inference = (
            len(input.shape) == 4
            and len(self.weight.shape) == 3
            and input.shape[1] == self.weight.shape[0]
            and input.shape[0] > input.shape[2]
        )
        if optimize_decode_inference:
            input = _torch.swapaxes(input, 0, 2)

        x = _torch.matmul(input, self.weight)

        if optimize_decode_inference:
            x = _torch.swapaxes(x, 0, 2)

        if self.bias is not None:
            x = x + self.bias
        return x

    def extra_repr(self) -> str:
        return (
            f"in_features={self.in_features}, "
            f"out_features={self.out_features}, "
            f"vec_dim={self.vec_dim}, bias={self.bias is not None}"
        )


# Implementation of segmented linear operations. See functiona segment_matmul for details.
class SegmentedLinear(VectorizedLinear):
    # pylint: disable=redefined-builtin
    def forward(self, input: _torch.Tensor, **kwargs) -> _torch.Tensor:
        return _tamm_F.segment_matmul(input, kwargs["group_sizes"], self.weight)
