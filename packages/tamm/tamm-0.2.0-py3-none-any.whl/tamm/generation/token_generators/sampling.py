"""
token_generators.sampling
^^^^^^^^^^^^^^^^^^^^^^^^^
"""

from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch
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
from tamm.generation.token_generators.utils import process_logit as _process_logit
from tamm.utils.torch_utils import (
    torch_exportable_dataclass as _torch_exportable_dataclass,
)


class SamplingNextTokenLogic(_NextTokenLogic):
    """
    Generates next token by transforming the logits into a probability distribution
    using the sampling parameters (temperature scaling, top_k and top_p filtering)
    and drawing a random sample from this distribution.

    Args:
        temperature (:obj:`float`): A scaling factor applied to the logits to adjust the randomness
          of the predictions. Defaults to ``None``.
        top_k (:obj:`int`): The number of highest probability tokens to consider when filtering the logits.
          if ``top_k`` is greater than 0, only the top k tokens with highest probability are retained.
          Defaults to ``None``.
        top_p (:obj:`float`): Cumulative probability threshold for nucleus sampling. Defaults to ``None``.
    """

    def __init__(
        self,
        temperature: _Optional[float] = None,
        top_k: _Optional[int] = None,
        top_p: _Optional[float] = None,
    ):
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p

    def compute_probabilities(self, logits: _torch.Tensor) -> _torch.Tensor:
        """
        Returns a probability distribution by transforming logits using the sampling
        parameters.
        """
        _, probs = _process_logit(
            logits, temperature=self.temperature, top_k=self.top_k, top_p=self.top_p
        )
        return probs

    def __call__(
        self,
        logits: _torch.Tensor,
        return_probabilities: bool = False,
        rng: _Optional[_torch.Generator] = None,
    ) -> _NextTokenLogicOutput:
        probs = self.compute_probabilities(logits)
        next_tokens = _torch.multinomial(probs, num_samples=1, generator=rng)
        if return_probabilities:
            return _NextTokenLogicOutput(token_ids=next_tokens, probabilities=probs)
        return _NextTokenLogicOutput(token_ids=next_tokens)


@_torch_exportable_dataclass
class SamplingTokenGeneratorOutput(_TokenGeneratorOutput):
    """
    Output generated from :py:class:`SamplingTokenGenerator`, consisting of token_ids and
    corresponding logits, if that option is enabled.

    Args:
        token_ids (:py:class:`_torch.Tensor`): Tokens produced by the sampling generator.
          Does not include ``input_ids``.
        logits (optional :py:class:`_torch.Tensor`): Logits corresponding to the generated tokens
        probabilities (optional :py:class:`_torch.Tensor`): Probability distributions corresponsing to
         the token ids.
    """

    token_ids: _torch.Tensor
    logits: _Optional[_torch.Tensor] = None
    probabilities: _Optional[_torch.Tensor] = None


class SamplingTokenGenerator(_VanillaTokenGenerator):
    """
    Token generator that uses sampling decoding strategy.

    Args:
        model (:obj:`nn.Module`): The model instance.
        eos_id (:obj:`Union[int, torch.Tensor, List[torch.Tensor]]`): End of sequence token ID(s).
        pad_id (:obj:`Union[int, torch.Tensor]`): Padding token ID.
        temperature (:obj:`float`): A scaling factor applied to the logits to adjust the randomness
          of the predictions. Defaults to ``None``.
        top_k (:obj:`int`): The number of highest probability tokens to consider when filtering the logits.
          if ``top_k`` is greater than 0, only the top k tokens with highest probability are retained.
          Defaults to ``None``.
        top_p (:obj:`float`): Cumulative probability threshold for nucleus sampling. Defaults to ``None``.
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
        temperature: _Optional[float] = None,
        top_k: _Optional[int] = None,
        top_p: _Optional[float] = None,
        cache_type: _Optional[_KVCacheType] = _KVCacheType.V0,
        cache_dtype: _Optional[_torch.dtype] = None,
        output_logits: bool = False,
        output_probabilities: bool = False,
    ):
        next_token_logic = SamplingNextTokenLogic(
            temperature=temperature, top_k=top_k, top_p=top_p
        )
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
    ) -> SamplingTokenGeneratorOutput:
        token_ids, return_logits, return_probs = self._generate(
            input_ids, max_new_tokens, seed
        )
        return SamplingTokenGeneratorOutput(
            token_ids=token_ids, logits=return_logits, probabilities=return_probs
        )
