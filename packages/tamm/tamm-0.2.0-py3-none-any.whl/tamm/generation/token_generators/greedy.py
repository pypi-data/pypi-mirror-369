"""
token_generators.greedy
^^^^^^^^^^^^^^^^^^^^^^^
"""

from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch
import torch.nn.functional as _F
from torch import nn as _nn

from tamm.generation.token_generators._vanilla import _VanillaTokenGenerator
from tamm.generation.token_generators.base import (
    TokenGeneratorOutput as _TokenGeneratorOutput,
)
from tamm.generation.token_generators.next_token_logic import (
    NextTokenLogic as _NextTokenLogic,
)
from tamm.generation.token_generators.next_token_logic import (
    NextTokenLogicOutput as _NextTokenLogicOutput,
)
from tamm.generation.token_generators.utils import KVCacheType as _KVCacheType
from tamm.utils.torch_utils import (
    torch_exportable_dataclass as _torch_exportable_dataclass,
)


class GreedyNextTokenLogic(_NextTokenLogic):
    """
    Generates next token as the argmax of the model's output logits.
    """

    def compute_probabilities(self, logits: _torch.Tensor) -> _torch.Tensor:
        """
        Returns a one-hot probability distribution with value ``1`` at the index
        corresponding to argmax of logits.
        """
        # pylint: disable=not-callable
        indices = logits.argmax(dim=-1)
        one_hot = _F.one_hot(indices, num_classes=logits.size(-1))
        return one_hot.to(logits.dtype)

    def __call__(
        self,
        logits: _torch.Tensor,
        return_probabilities: bool = False,
        rng: _Optional[_torch.Generator] = None,
    ) -> _NextTokenLogicOutput:
        if not return_probabilities:
            return _NextTokenLogicOutput(token_ids=logits.argmax(dim=-1, keepdim=True))
        probabilities = self.compute_probabilities(logits)
        return _NextTokenLogicOutput(
            token_ids=probabilities.argmax(dim=-1, keepdim=True),
            probabilities=probabilities,
        )


@_torch_exportable_dataclass
class GreedyTokenGeneratorOutput(_TokenGeneratorOutput):
    """
    Output generated from :py:class:`GreedyTokenGenerator`, consisting of token ids and
    corresponding logits, if that option is enabled.

    Args:
        token_ids (:py:class:`_torch.Tensor`): Token ids produced by the greedy generator.
          Does not include ``input_ids``.
        logits (optional :py:class:`_torch.Tensor`): Logits corresponding to the generated token ids.
        probabilities (optional :py:class:`_torch.Tensor`): Probability distributions corresponsing to
         the token ids.
    """

    token_ids: _torch.Tensor
    logits: _Optional[_torch.Tensor] = None
    probabilities: _Optional[_torch.Tensor] = None


class GreedyTokenGenerator(_VanillaTokenGenerator):
    """
    Token generator that uses greedy decoding strategy.

    Args:
        model (:obj:`nn.Module`): The model instance.
        eos_id (:obj:`Union[int, torch.Tensor, List[torch.Tensor]]`): End of sequence token ID(s).
        pad_id (:obj:`Union[int, torch.Tensor]`): Padding token ID.
        cache_type (:obj:`KVCacheType`, optional): Type of KV cache to use. Defaults to KVCacheType.V0.
        cache_dtype (:obj:`torch.dtype`, optional): Data type for KV cache. Defaults to None.
        output_logits (:obj:`bool`): When set to ``True``, :py:meth:`generate` returns logits
          corresponding to the generated ``token_ids``.
        output_probabilities (:obj:`bool`): When set to ``True``, :py:meth:`generate` returns probability
          distributions corresponding to the generated ``token_ids``.
    """

    def __init__(
        self,
        model: _nn.Module,
        eos_id: _Union[int, _torch.Tensor, _List[_torch.Tensor]],
        pad_id: _Union[int, _torch.Tensor],
        cache_type: _Optional[_KVCacheType] = _KVCacheType.V0,
        cache_dtype: _Optional[_torch.dtype] = None,
        output_logits: bool = False,
        output_probabilities: bool = False,
    ):
        next_token_logic = GreedyNextTokenLogic()
        # pylint: disable=duplicate-code
        super().__init__(
            model=model,
            next_token_logic=next_token_logic,
            eos_id=eos_id,
            pad_id=pad_id,
            cache_type=cache_type,
            cache_dtype=cache_dtype,
            output_logits=output_logits,
            output_probabilities=output_probabilities,
        )

    @_torch.inference_mode()
    def generate(
        self,
        input_ids: _torch.Tensor,
        max_new_tokens: int,
        seed: _Optional[int] = None,
    ) -> GreedyTokenGeneratorOutput:
        token_ids, return_logits, return_probs = self._generate(
            input_ids, max_new_tokens, seed
        )
        return GreedyTokenGeneratorOutput(
            token_ids=token_ids, logits=return_logits, probabilities=return_probs
        )
