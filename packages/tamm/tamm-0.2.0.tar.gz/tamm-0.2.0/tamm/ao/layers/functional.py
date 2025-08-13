from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch


def fake_quantize(
    tensor: _torch.Tensor,
    *,
    scale: _torch.Tensor,
    zero_point: _torch.Tensor,
    quant_min: int,
    quant_max: int,
    cast_dtype: _Optional[_torch.dtype] = None,
    reciprocal_mul: bool = False,
):
    """
    Computes fake quantization via the formula

    .. code-block:: python

        quant = (torch.round(tensor / scale) + zero_point).clamp(quant_min, quant_max)
        return scale * (quant - zero_point)

    If ``cast_dtype`` is not ``None``, then the function casts ``tensor`` and ``scale``
    to ``cast_dtype`` before computing the result (but the dtype of the result is the
    same as the input dtype).
    """
    return FakeQuantize.apply(
        tensor, scale, zero_point, quant_min, quant_max, cast_dtype, reciprocal_mul
    )


class FakeQuantize(_torch.autograd.Function):
    # pylint: disable=arguments-differ,abstract-method

    generate_vmap_rule = True

    @staticmethod
    def forward(
        ctx,
        tensor: _torch.Tensor,
        scale: _torch.Tensor,
        zero_point: _torch.Tensor,
        quant_min: int,
        quant_max: int,
        cast_dtype: _Union[_torch.dtype, None],
        reciprocal_mul: bool = False,
    ):
        input_dtype = tensor.dtype
        ctx.input_dtype = input_dtype

        if reciprocal_mul:
            scale_inv = 1 / scale
        if cast_dtype is not None:
            tensor = tensor.type(cast_dtype)
            if reciprocal_mul:
                scale_inv = scale_inv.type(cast_dtype)
            scale = scale.type(cast_dtype)

        if cast_dtype == input_dtype:
            if reciprocal_mul:
                out = tensor.mul(scale_inv)
            else:
                out = tensor.div(scale)
        else:
            if reciprocal_mul:
                out = tensor.mul_(scale_inv)
            else:
                out = tensor.div_(scale)
        out.round_()
        out.add_(zero_point)
        out.clamp_(quant_min, quant_max)
        out.sub_(zero_point)
        out.mul_(scale)
        out = out.to(input_dtype)
        return out

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.type(ctx.input_dtype), *(6 * [None])
