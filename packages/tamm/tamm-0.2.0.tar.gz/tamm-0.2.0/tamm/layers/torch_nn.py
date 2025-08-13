"""
This submodule contains |tamm| versions of layers from :mod:`torch.nn`.  These layers
have the same behavior as their :mod:`torch` counterparts.  The difference is that the
|tamm| versions also have a :class:`LayerBuilder` attached as the ``Builder`` class
attribute.
"""

import torch.nn as _nn

from tamm import _compat
from tamm.layers.common import LayerMixin as _LayerMixin


class MaxPool1d(_nn.MaxPool1d, _LayerMixin):
    """A |tamm| version of :class:`torch.nn.MaxPool1d`."""


class MaxPool2d(_nn.MaxPool2d, _LayerMixin):
    """A |tamm| version of :class:`torch.nn.MaxPool2d`."""


class AdaptiveAvgPool2d(_nn.AdaptiveAvgPool2d, _LayerMixin):
    """A |tamm| version of :class:`torch.nn.AdaptiveAvgPool2d`."""


class AvgPool2d(_nn.AvgPool2d, _LayerMixin):
    """A |tamm| version of :class:`torch.nn.AvgPool2d`."""


class BatchNorm2d(_nn.BatchNorm2d, _LayerMixin):
    """A |tamm| version of :class:`torch.nn.BatchNorm2d`."""


class GroupNorm(_nn.GroupNorm, _LayerMixin):
    """A |tamm| version of :class:`torch.nn.GroupNorm`."""


_compat.register_backward_compatibility_import(
    __name__, "Softmax", "tamm.layers.activation.Softmax"
)
