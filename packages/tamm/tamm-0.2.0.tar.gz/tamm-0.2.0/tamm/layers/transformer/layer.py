"""
transformer.layer
^^^^^^^^^^^^^^^^^

This module implements a transformer layer.

.. autoclass:: tamm.layers.TransformerLayer
    :members:
"""

from tamm.layers import sequential as _sequential
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class TransformerLayer(_sequential.Sequential, _LayerMixin):
    """
    A sequence of (self) attention, optional cross-attention, and finally feed
    forward. The :meth:`forward` method is equivalent to:

    .. code-block:: python

        def forward(
            self, inputs, attention_side_inputs, cross_attention_side_inputs
        ):
            x = self.attention(inputs, **attention_side_inputs)

            if self.cross_attention is not None:
                x = self.cross_attention(hidden_states, **cross_attention_side_inputs)

            return self.feed_forward(x)

    Typically the layer takes inputs of shape
    ``(batch_size, sequence_length, input_dim)`` and returns outputs of the same shape.

    Args:
        attention: A self-attention layer.
        cross_attention: An optional cross-attention layer.
        feed_forward: A feed-forward layer.
    """

    def __init__(
        self,
        *,
        attention: _ModuleOrBuilder,
        cross_attention: _OptionalModuleOrBuilder = None,
        feed_forward: _ModuleOrBuilder,
    ):
        named_layers = {}
        side_input_keys = {}

        named_layers["attention"] = attention
        side_input_keys["attention"] = [
            # individual args only included for backward compatibility:
            "attention_mask",
            "flash_attention_options",
            "kv_cache",
            "query_rope_coefficients",
            "key_rope_coefficients",
            # keyword arguments:
            ("attention_side_inputs", "**kwargs"),
        ]

        if cross_attention:
            named_layers["cross_attention"] = cross_attention
            side_input_keys["cross_attention"] = [
                # keyword arguments:
                ("cross_attention_side_inputs", "**kwargs"),
            ]

        named_layers["feed_forward"] = feed_forward

        super().__init__(named_layers, side_input_keys=side_input_keys)
