from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
from torch import nn as _nn

from tamm.generation.token_generators.base import TokenGenerator as _TokenGenerator
from tamm.generation.token_generators.next_token_logic import (
    NextTokenLogic as _NextTokenLogic,
)
from tamm.generation.token_generators.utils import (
    KVCacheType,
    check_eos_endings,
    create_random_number_generator,
    model_forward_step,
    pad_after_termination,
    prepare_input_ids,
    setup_kv_cache,
)


class _VanillaTokenGenerator(_TokenGenerator):
    """
    Token generator that uses autoregressive strategy for generating tokens,
    i.e., it generates first token by passing inputs to the model, and then appends this token
    to the inputs to generate the next token and so on.

    Args:
        model (:obj:`nn.Module`): The model instance.
        next_token_logic (:obj:`_NextTokenLogic`): Logic specifying how model's output logits should be
         used to generate the next token.
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
        next_token_logic: _NextTokenLogic,
        eos_id: _Union[int, _torch.Tensor, _List[_torch.Tensor]],
        pad_id: _Union[int, _torch.Tensor],
        cache_type: _Optional[KVCacheType] = KVCacheType.V0,
        cache_dtype: _Optional[_torch.dtype] = None,
        output_logits: bool = False,
        output_probabilities: bool = False,
    ):
        super().__init__(
            model=model,
            eos_id=eos_id,
            pad_id=pad_id,
        )
        self.next_token_logic = next_token_logic
        self._cache_type = cache_type
        self._cache_dtype = cache_dtype
        self.output_logits = output_logits
        self.output_probabilities = output_probabilities

    # pylint: disable=duplicate-code, too-many-locals
    @_torch.inference_mode()
    def _generate(
        self,
        input_ids: _torch.Tensor,
        max_new_tokens: int,
        seed: _Optional[int] = None,
    ) -> _Tuple[_torch.Tensor, _Optional[_torch.Tensor], _Optional[_torch.Tensor]]:
        input_ids = prepare_input_ids(input_ids)
        batch_size, prompt_len = input_ids.shape
        device = input_ids.device

        torch_rng = create_random_number_generator(device, seed)

        kv_cache = setup_kv_cache(
            model=self.model,
            batch_size=batch_size,
            cache_len=prompt_len + max_new_tokens,
            input_ids=input_ids,
            pad_id=self.pad_id,
            cache_type=self._cache_type,
            cache_dtype=self._cache_dtype,
        )

        eos_token_ids = [x.to(input_ids.device) for x in self.eos_ids]
        next_tokens = None
        return_logits, logits_list = None, []
        return_probs, probs_list = None, []

        for token_idx in range(max_new_tokens):
            output = model_forward_step(
                model=self.model,
                input_ids=input_ids,
                next_tokens=next_tokens,
                pad_id=self.pad_id,
                kv_cache=kv_cache,
                prompt_len=prompt_len,
                token_idx=token_idx,
            )
            logits = output.logits[:, -1, : self.model.config.vocab_size]
            next_token_output = self.next_token_logic(
                logits, return_probabilities=self.output_probabilities, rng=torch_rng
            )
            next_tokens = next_token_output.token_ids
            input_ids = _torch.cat([input_ids, next_tokens], dim=-1)

            if self.output_logits:
                logits_list.append(logits.unsqueeze(1))
            if self.output_probabilities:
                probs_list.append(next_token_output.probabilities.unsqueeze(1))  # type: ignore[union-attr]

            should_terminate = (
                check_eos_endings(
                    generated_tokens=next_tokens, eos_token_ids=eos_token_ids
                )
                .all()
                .item()
            )

            if should_terminate:
                break

        token_ids = input_ids[:, prompt_len:]
        token_ids = pad_after_termination(token_ids, self.pad_id, eos_token_ids)

        if self.output_logits:
            return_logits = _torch.cat(logits_list, dim=1)
        if self.output_probabilities:
            return_probs = _torch.cat(probs_list, dim=1)

        return token_ids, return_logits, return_probs
