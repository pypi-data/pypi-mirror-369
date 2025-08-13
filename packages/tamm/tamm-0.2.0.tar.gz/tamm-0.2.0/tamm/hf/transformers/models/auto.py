"""
Implements functionality related to auto-classes in the transformers package.
"""

import functools as _functools
import logging as _logging

import transformers as _transformers

from tamm import _helpers
from tamm.hf.transformers.models import _mixins
from tamm.hf.transformers.models import causal_lm as _causal_lm
from tamm.hf.transformers.models import sentencepiece as _sentencepiece

_logger = _logging.getLogger(__name__)


@_helpers.cache  # execute the function only once
def register_with_auto_classes() -> None:
    """
    Register tamm Hugging Face classes with auto classes from :mod:`transformers`,
    such as ``AutoConfig``, ``AutoModel``, and ``AutoModelForCausalLM``.

    Example:

        .. code-block:: python

            register_with_auto_classes()

            from transformers import AutoConfig, AutoModel

            config = AutoConfig.for_model("tamm_causal_lm")
            AutoModel.from_config(config)
    """
    _transformers.AutoConfig.register(
        model_type=_causal_lm.TammCausalLMConfig.model_type,
        config=_causal_lm.TammCausalLMConfig,
    )
    _transformers.AutoModel.register(
        config_class=_causal_lm.TammCausalLMConfig,
        model_class=_causal_lm.TammCausalLMModel,
    )
    _transformers.AutoModelForCausalLM.register(
        config_class=_causal_lm.TammCausalLMConfig,
        model_class=_causal_lm.TammCausalLMForCausalLM,
    )
    _transformers.AutoTokenizer.register(
        config_class=_sentencepiece.TammSentencePieceConfig,
        slow_tokenizer_class=_sentencepiece.TammSentencePieceTokenizer,
    )
    _register_with_auto_classes_deprecated()
    _logger.info("Registered tamm with transformers auto classes")


def _register_with_auto_classes_deprecated():
    """
    Helper function for organizing the registration of deprecated types
    with HF auto classes.
    """


def _auto_register_tamm_classes(fn):
    """
    A decorator that wraps a function in order to call
    :func:`register_with_auto_classes` before calling the function.
    """

    @_functools.wraps(fn)
    def wrapper(*args, **kwargs):
        register_with_auto_classes()
        return fn(*args, **kwargs)

    return wrapper


def _add_tamm_auto_registration_to_auto_class(cls):
    """
    A class decorator that wraps methods of transformers autoclass
    subclasses in order to register tamm objects automatically as needed.
    """

    method_names = ["from_pretrained", "from_config", "for_model"]
    for name in method_names:
        if not hasattr(cls, name):
            continue
        new_fn = _auto_register_tamm_classes(getattr(cls, name))
        setattr(cls, name, new_fn)
    return cls


@_add_tamm_auto_registration_to_auto_class
class AutoConfig(_transformers.AutoConfig):
    """
    Extends :class:`transformers.AutoConfig` to automatically register
    tamm objects when used.
    """


@_add_tamm_auto_registration_to_auto_class
class AutoModel(_transformers.AutoModel, _mixins.FromModelIDMixin):
    """
    Extends :class:`transformers.AutoModel` to add :meth:`from_tamm_model_id` and
    :meth:`save_pretrained_for_tamm_model_id` methods.  This class also
    automatically calls :func:`register_with_auto_classes` as needed.
    """


@_add_tamm_auto_registration_to_auto_class
class AutoModelForCausalLM(
    _transformers.AutoModelForCausalLM, _mixins.FromModelIDMixin
):
    """
    Extends :class:`transformers.AutoModelForCausalLM` to add :meth:`from_tamm_model_id`
    and :meth:`save_pretrained_for_tamm_model_id` methods.  This class also
    automatically calls :func:`register_with_auto_classes` as needed.
    """


@_add_tamm_auto_registration_to_auto_class
class AutoTokenizer(_transformers.AutoTokenizer):
    """
    Extends :class:`transformers.AutoTokenizer` to add
    :meth:`from_tamm_tokenizer_id` and
    :meth:`save_pretrained_for_tamm_tokenizer_id` methods.  This class also
    automatically calls :func:`register_with_auto_classes` as needed.
    """
