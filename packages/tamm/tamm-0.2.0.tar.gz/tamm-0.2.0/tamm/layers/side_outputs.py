import dataclasses as _dataclasses
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional

import torch as _torch

from tamm.utils import torch_utils as _torch_utils


@_torch_utils.torch_exportable_dataclass
class OutputWithSideOutputs:
    """
    Class to support passing side outputs to higher level.
    This is used in layers in tamm.layers.sequential.Sequential to capture
    intermediate outputs that might be helpful for users in training process.
    """

    output: _torch.Tensor
    side_outputs: _Optional[_Dict[str, _Any]] = _dataclasses.field(default_factory=dict)

    def merge_side_outputs(self, other_side_outputs: _Dict[str, _Any]) -> None:
        self.side_outputs = merge_side_outputs(self.side_outputs, other_side_outputs)


def merge_side_outputs(
    side_outputs: _Dict[str, _Any], other_side_outputs: _Dict[str, _Any]
):
    result = {**side_outputs}

    for key, other_val in other_side_outputs.items():
        if key not in side_outputs:
            result[key] = other_val
            continue

        val = side_outputs[key]
        if not isinstance(val, list):
            val = [val]
        if isinstance(other_val, list):
            val.extend(other_val)
        else:
            val.append(other_val)
        result[key] = val

    return result
