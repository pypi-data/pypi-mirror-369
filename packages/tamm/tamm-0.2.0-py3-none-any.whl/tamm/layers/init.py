import math as _math
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch


def shape_normalized_normal_(
    tensor: _torch.Tensor,
    *,
    dim: _Optional[_Union[int, _Tuple[int, ...]]] = None,
):
    """
    Fills a tensor with values drawn i.i.d. from a zero-centered normal
    distribution.  The variance is defined such that the norm of these values
    along ``dim`` has an expected value of ``1``.

    Args:
        tensor (:obj:`torch.Tensor`): The tensor to initialize.
        dim (:obj:`int` or :obj:`tuple` of :obj:`int`, optional):  The
            dimension(s) of ``tensor`` to consider when choosing the variance of
            the initialization distribution.  Defaults to all dimensions.
    """

    if dim is None:
        count = tensor.numel()
    elif isinstance(dim, int):
        count = tensor.size(dim)
    else:
        sizes = [tensor.size(d) for d in dim]
        count = _torch.Size(sizes).numel()

    std = 1 / _math.sqrt(count)
    _torch.nn.init.normal_(tensor, std=std)
