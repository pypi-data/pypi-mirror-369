"""
This module provides a class for wrapping arbitary functions into :obj:`nn.Module`
objects.
"""

from typing import Callable as _Callable

import torch.nn as _nn

from tamm.layers.common import LayerMixin as _LayerMixin


class Lambda(_nn.Module, _LayerMixin):
    """
    A :class:`nn.Module` for wrapping a function as a :obj:`Module`.

    Args:
        function (:obj:`Callable`): A callable function that takes inputs to the forward
            function and returns the output of forward.
    """

    def __init__(self, function: _Callable):
        super().__init__()
        self.function = function

    # pylint: disable-next=all
    def forward(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def extra_repr(self) -> str:
        return f"function={repr(self.function)}"
