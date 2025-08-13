"""HF transformers model configuration for tamm SentencePiece tokenizer"""

import transformers as _transformers


class TammSentencePieceConfig(_transformers.PretrainedConfig):
    """
    A minimal config to go along with the :class:`.TammSentencePieceTokenizer`
    (since :mod:`transformers` requires a config to register the tokenizer
    with :class:`transformers.AutoTokenizer`).
    """

    model_type = "tamm_sentencepiece"
