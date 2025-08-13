"""
This module provides variations of dropout layers.
"""

import torch.nn as _nn

from tamm.layers.common import LayerMixin as _LayerMixin


class Dropout(_nn.Dropout, _LayerMixin):
    """A dropout layer with a default dropout rate of zero."""

    def __init__(self, p: float = 0.0, inplace: bool = False) -> None:
        super().__init__(p=p, inplace=inplace)

    def forward(self, *args, **kwargs):  # pylint: disable=useless-parent-delegation
        # This override is important for torch.compile with DDP as of torch 2.5
        return super().forward(*args, **kwargs)
