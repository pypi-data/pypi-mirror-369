import abc as _abc
from typing import Optional as _Optional

import torch as _torch

from tamm.utils.torch_utils import (
    torch_exportable_dataclass as _torch_exportable_dataclass,
)


@_torch_exportable_dataclass
class NextTokenLogicOutput:
    """
    Output generated from :py:class:`NextTokenLogic`, consisting of token ids and
    corresponding probabilities, if that option is enabled.

    Args:
        token_ids (:py:class:`_torch.Tensor`): New token ids produced by the next token logic.
          token_ids have the same number of dimensions as the input logits, i.e., if the
          input logits have shape [bs x seq_len x vocab_size], the token_ids would have shape
          [bs x seq_len x 1].
        probabilities (optional :py:class:`_torch.Tensor`): Probability distributions corresponsing to
         the generated token ids.
    """

    token_ids: _torch.Tensor
    probabilities: _Optional[_torch.Tensor] = None


class NextTokenLogic(_abc.ABC):
    """
    An abstract class for implementing logic for generating next token given a
    model's output logits for the current input_ids.
    """

    @_abc.abstractmethod
    def compute_probabilities(self, logits: _torch.Tensor) -> _torch.Tensor:
        """
        Computes a probability distribution from a model's logits.
        """

    @_abc.abstractmethod
    def __call__(
        self,
        logits: _torch.Tensor,
        return_probabilities: bool = False,
        rng: _Optional[_torch.Generator] = None,
    ) -> NextTokenLogicOutput:
        """
        Compute next token given the model's logits. Also return probabilities
        when return_probabilities is set to ``True``.
        """
