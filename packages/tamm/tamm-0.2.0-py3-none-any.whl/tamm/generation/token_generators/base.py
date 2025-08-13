"""
token_generators.base
^^^^^^^^^^^^^^^^^^^^^
"""

import abc as _abc
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union
from typing import cast as _cast

import torch as _torch
from torch import nn as _nn

from tamm.utils.torch_utils import (
    torch_exportable_dataclass as _torch_exportable_dataclass,
)


@_torch_exportable_dataclass
class TokenGeneratorOutput:
    """
    Output generated from :py:class:`TokenGenerator`, consisting of token_ids and other
    fields specific to the generation algorithm.

    Attributes:
        token_ids (:py:class:`_torch.Tensor`): Token ids produced by a generator. Does not include ``input_ids``.
    """

    token_ids: _torch.Tensor


class TokenGenerator(_abc.ABC):
    """
    Base class for classes that generate tokens using an autoregressive decoder model.
    """

    def __init__(
        self,
        model: _nn.Module,
        eos_id: _Union[int, _torch.Tensor, _List[_torch.Tensor]],
        pad_id: _Union[int, _torch.Tensor],
    ):
        self.model = model
        self.eos_ids = self._cast_eos_ids_to_list(eos_id)
        self.pad_id = pad_id

    @_abc.abstractmethod
    def generate(
        self,
        input_ids: _torch.Tensor,
        max_new_tokens: int,
        seed: _Optional[int] = None,
    ) -> TokenGeneratorOutput:
        """
        Generate tokens using an autoregressive decoder model.
        """

    @staticmethod
    def _cast_eos_ids_to_list(
        eos_ids: _Union[int, _torch.Tensor, _List[_torch.Tensor], _List[int]]
    ) -> _List[_torch.Tensor]:
        # XXX: eos_ids may be one of two things with different semantics;
        #
        # a) a single torch.Tensor of various single-shot tokens, each of which terminates decoding
        # b) a list of 1D torch.Tensors, any of which must be found in its entirety in a decode in order to
        # terminate decoding
        #
        # we determine which we have been passed here and cast it into the latter form
        if isinstance(eos_ids, int):
            return [_torch.tensor([eos_ids])]
        if isinstance(eos_ids, _torch.Tensor):
            return list(eos_ids.flatten())
        if isinstance(eos_ids, list) and isinstance(eos_ids[0], int):
            return [_torch.tensor(token, dtype=_torch.int) for token in eos_ids]
        return _cast(_List[_torch.Tensor], eos_ids)
