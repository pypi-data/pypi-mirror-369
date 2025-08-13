import torch as _torch
import torch.nn as _nn

from tamm.layers.common import LayerMixin as _LayerMixin


class FlattenedCrossEntropyLoss(_nn.CrossEntropyLoss, _LayerMixin):
    # pylint: disable=redefined-builtin
    def forward(self, input: _torch.Tensor, target: _torch.Tensor) -> _torch.Tensor:
        input = input.view(-1, input.shape[-1])
        target = target.flatten()
        return super().forward(input, target)
