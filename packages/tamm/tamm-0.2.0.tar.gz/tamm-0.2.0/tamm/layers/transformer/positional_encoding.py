"""
transformer.positional_encoding
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This submodule implements positional encoding layers for :class:`.TransformerStack`.
These layers encode positions into embeddings and attention masks prior to the sequence
of transformer layers.
Unlike :mod:`tamm.layers.positional_encoding`, this submodule is specific to
:class:`.TransformerStack`.

Base class
----------

.. autoclass:: tamm.layers.TransformerPositionalEncoding
    :show-inheritance:
    :members: forward

.. autoclass:: TransformerPositionalEncodingOutput


Positional encodings
--------------------

.. autoclass:: tamm.layers.ALiBiPositionalEncoding
    :show-inheritance:

.. autoclass:: tamm.layers.NoPositionalEncoding
    :show-inheritance:

.. autoclass:: tamm.layers.RotaryPositionalEmbedding
    :show-inheritance:

.. autoclass:: tamm.layers.SinusoidalPositionalEmbedding
    :show-inheritance:

.. autoclass:: tamm.layers.SlidingWindowPositionalEncoding
    :show-inheritance:

.. autoclass:: tamm.layers.TransformerAbsolutePositionalEmbedding
    :show-inheritance:
    :members: create_builder


Composite positional encodings
------------------------------

.. autoclass:: tamm.layers.SequentialPositionalEncoding
    :show-inheritance:


Secondary positional encodings
------------------------------

.. autoclass:: tamm.layers.SecondaryPositionalEncodings
    :members:


Helper function
---------------

.. autofunction:: tamm.layers.transformer.positional_encoding.compute_alibi_slopes
"""

import abc as _abc
import collections as _collections
import math as _math
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional

import torch as _torch
import torch.nn as _nn

from tamm import _helpers
from tamm.layers import positional_encoding as _positional_encoding
from tamm.layers import rope as _rope
from tamm.layers.common import ConfigurableLayerMixin as _ConfigurableLayerMixin
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.layers.transformer import token_metadata as _token_metadata
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalDeviceOrString as _OptionalDeviceOrString

TransformerPositionalEncodingOutput = _collections.namedtuple(
    "TransformerPositionalEncodingOutput", ["embeddings", "attention_side_inputs"]
)
"""
A :class:`namedtuple` for holding outputs from a :class:`TransformerPositionalEncoding`.

.. py:attribute:: embeddings

    Embedding inputs to the first layer of a transformer.

.. py:attribute:: attention_side_inputs

    Side inputs to self attention layers of a transformer.
"""


class TransformerPositionalEncoding(_nn.Module, _abc.ABC):
    """
    A base class for layers that encode token positions into the inputs of
    a transformer layer sequence.
    """

    def __init__(self):
        super().__init__()

    @_abc.abstractmethod
    def forward(
        self,
        *,
        token_metadata: _token_metadata.TokenMetadata,
        embeddings: _torch.Tensor,
        attention_side_inputs: _Dict[_Any, _Any],
    ) -> TransformerPositionalEncodingOutput:
        """
        Args:
            token_metadata (:obj:`TokenMetadata`): A :obj:`TokenMetadata`
                that includes an integer ``q_positions`` tensor with shape
                ``(batch_size, seq_len)`` and a ``kv_positions`` tensor with
                shape ``(batch_sie, kv_seq_len)``.  The KV sequence length may be larger
                than the query length when using a KV cache.
            embeddings (:obj:`torch.Tensor`): The input embeddings to a transformer
                model with shape ``(batch_size, seq_len, hidden_dim)``.  The dtype
                should match the computation dtype for attention layers.
            attention_side_inputs (:obj:`dict`): A dictionary of side inputs to
                attention layers.  This should contain ``"attention_mask"`` and
                ``"flash_attention_options"`` keys.

        Returns:
            A :obj:`TransformerPositionalEncodingOutput`, which contains new
            ``embeddings`` and ``attention_side_inputs`` objects with positions encoded.
        """


class NoPositionalEncoding(TransformerPositionalEncoding, _LayerMixin):
    """
    A passthrough NoPE layer, which returns unmodified embeddings and attention
    side inputs.
    """

    def forward(
        self,
        *,
        token_metadata: _token_metadata.TokenMetadata,
        embeddings: _torch.Tensor,
        attention_side_inputs: _Dict[_Any, _Any],
    ) -> TransformerPositionalEncodingOutput:
        return TransformerPositionalEncodingOutput(
            embeddings=embeddings, attention_side_inputs=attention_side_inputs
        )


class TransformerAbsolutePositionalEmbedding(
    _positional_encoding.AbsolutePositionalEmbedding,
    TransformerPositionalEncoding,
    _ConfigurableLayerMixin,
):
    """
    Layer for absolute positional embeddings.  This layer maps positions to trainable
    embedding tensors and then adds these embeddings to the token embeddings.

    Args:
        embedding: An embedding layer (or builder) that maps positions to embeddings.
        sequence_start (:obj:`int`, optional): An option that controls which tokens
            receive positional embeddings.  If ``sequence_start > 0``, then the first
            ``sequence_start`` tokens do not receive positional embeddings.

    .. note::
        This layer is the same as :class:`AbsolutePositionalEmbedding` except that it
        adapts the :meth:`forward` signature to work with :class:`.TransformerStack`.
    """

    def forward(  # pylint: disable=arguments-differ
        self,
        *,
        token_metadata: _token_metadata.TokenMetadata,
        embeddings: _torch.Tensor,
        attention_side_inputs: _Dict[_Any, _Any],
    ) -> TransformerPositionalEncodingOutput:
        embeddings = super().forward(embeddings, positions=token_metadata.q_positions)
        return TransformerPositionalEncodingOutput(
            embeddings=embeddings, attention_side_inputs=attention_side_inputs
        )


class SlidingWindowPositionalEncoding(TransformerPositionalEncoding, _LayerMixin):
    """
    Positional encoding layer for sliding window attention
    (`paper <https://arxiv.org/pdf/2004.05150v2>`__).
    This layer masks out attention between tokens when the distance between tokens
    exceeds a window size.

    Args:
        window_size (:obj:int): Number of tokens to attend to on each side.
    """

    def __init__(self, window_size: int):
        """
        Initializes the SlidingWindowPositionalEncoding module.

        Args:
            window_size (:obj:int): Number of tokens in the sliding window on each side.
        """
        super().__init__()
        self.window_size = window_size

    def forward(
        self,
        *,
        token_metadata: _token_metadata.TokenMetadata,
        embeddings: _torch.Tensor,
        attention_side_inputs: _Dict[_Any, _Any],
    ) -> TransformerPositionalEncodingOutput:
        positions, kv_positions = (
            token_metadata.q_positions,
            token_metadata.kv_positions,
        )

        # Extract positions and compute distances
        distances = _torch.abs(positions[:, :, None] - kv_positions[:, None, :])

        # Create a binary mask based on window size
        distance_threshold = self.window_size
        mask = attention_side_inputs["attention_mask"]
        fill_value = float("-inf") if mask.is_floating_point() else 0
        attention_side_inputs["attention_mask"] = mask.masked_fill(
            distances > distance_threshold, fill_value
        )

        flash_options = attention_side_inputs.get("flash_attention_options")
        if flash_options is not None:
            if "window_size" in flash_options:
                raise RuntimeError("flash_options already contains a window_size")
            flash_options["window_size"] = (self.window_size, self.window_size)

        return TransformerPositionalEncodingOutput(
            embeddings=embeddings, attention_side_inputs=attention_side_inputs
        )

    def extra_repr(self) -> str:
        """
        Returns a string representation of the module's configuration for debugging.

        Returns:
            str: The window size configuration.
        """
        return f"window_size={self.window_size}"


class ALiBiPositionalEncoding(TransformerPositionalEncoding, _LayerMixin):
    """
    Positional Encoding layer for Attention with Linear Biases
    (`paper <https://arxiv.org/abs/2108.12409>`__).
    This layer introduces attention biases that are proportional to the negative
    distance between each query and key.  These distances are scaled by a different
    slope for each attention head.

    Args:
        num_heads (:obj:`int`): The number of attention heads.
    """

    def __init__(self, num_heads: int):
        super().__init__()
        self.num_heads = num_heads

    def forward(
        self,
        *,
        token_metadata: _token_metadata.TokenMetadata,
        embeddings: _torch.Tensor,
        attention_side_inputs: _Dict[_Any, _Any],
    ) -> TransformerPositionalEncodingOutput:
        positions, kv_positions = (
            token_metadata.q_positions,
            token_metadata.kv_positions,
        )

        mask = attention_side_inputs.get("attention_mask")
        if mask.ndim == 3:
            mask = mask.unsqueeze(-3)  # add heads dim

        biases = positions[:, None, :, None] - kv_positions[:, None, None, :]
        biases = -_torch.abs(biases.type(embeddings.dtype))
        biases = biases.masked_fill(mask.logical_not(), float("-inf"))
        slopes = compute_alibi_slopes(
            self.num_heads, device=biases.device, dtype=biases.dtype
        )
        mask = biases * slopes[None, :, None, None]
        attention_side_inputs["attention_mask"] = mask

        flash_options = attention_side_inputs.get("flash_attention_options")
        if flash_options is not None:
            flash_options["alibi_slopes"] = slopes.type(_torch.float32)

        return TransformerPositionalEncodingOutput(
            embeddings=embeddings, attention_side_inputs=attention_side_inputs
        )

    def extra_repr(self) -> str:
        return f"num_heads={self.num_heads}"


def compute_alibi_slopes(
    num_heads: int,
    *,
    device: _OptionalDeviceOrString = None,
    dtype: _Optional[_torch.dtype] = None,
) -> _torch.Tensor:
    """
    Computes slopes according to the `ALiBi paper <https://arxiv.org/abs/2108.12409>`__.
    Each slope is a scale factor for the ALiBi attention biases corresponding to its
    head.

    Args:
        num_heads (:obj:`int`): The number of heads for attention.
        device (:obj:`str` or :obj:`torch.device`): The target device for the resulting
            slopes tensor.
        dtype (:obj:`torch.dtype`): The dtype for the resulting slopes tensor.

    Returns:
        A 1D :obj:`torch.Tensor` of slopes with length ``num_heads``.
    """
    n = 2 ** _math.floor(_math.log2(num_heads))  # first power of 2 <= num_heads
    first_n = (2 ** (-8 * (i + 1) / n) for i in range(n))
    remainder = (2 ** (-4 * (2 * i + 1) / n) for i in range(num_heads - n))
    slopes = (*first_n, *remainder)
    return _torch.tensor(slopes, device=device, dtype=dtype)


class RotaryPositionalEmbedding(TransformerPositionalEncoding, _LayerMixin):
    """
    Positional encoder layer for Rotary Positional Embeddings
    (`paper <https://arxiv.org/pdf/2104.09864>`__).  This layer computes RoPE rotation
    matrices and adds them to ``attention_side_inputs`` with keys
    ``"query_rope_coefficients"`` and ``"key_rope_coefficients"``.

    Args:
        dim_per_head (:obj:`int`): The hidden dimension per attention head.
        theta (:obj:`float`, optional): ``theta`` param of RoPE.
    """

    def __init__(
        self,
        dim_per_head: int,
        *,
        theta: float = 10000.0,
    ):
        super().__init__()
        self.dim_per_head = dim_per_head
        self.theta = theta

    def forward(
        self,
        *,
        token_metadata: _token_metadata.TokenMetadata,
        embeddings: _torch.Tensor,
        attention_side_inputs: _Dict[_Any, _Any],
    ) -> TransformerPositionalEncodingOutput:
        coef = _rope.compute_rope_coefficients(
            positions=token_metadata.q_positions,
            dim=self.dim_per_head,
            theta=self.theta,
            dtype=embeddings.dtype,
        )
        attention_side_inputs["query_rope_coefficients"] = coef
        attention_side_inputs["key_rope_coefficients"] = coef

        return TransformerPositionalEncodingOutput(
            embeddings=embeddings, attention_side_inputs=attention_side_inputs
        )

    def extra_repr(self) -> str:
        return f"dim_per_head={self.dim_per_head}, theta={self.theta}"


class SinusoidalPositionalEmbedding(TransformerPositionalEncoding, _LayerMixin):
    """
    Positional encoding layer for Sinusoidal Positional Embeddings
    (`paper <https://arxiv.org/abs/1706.03762>`__). This layer computes sinusoidal
    positional encodings and adds them to the input embeddings.

    Args:
        min_timescale (:obj:`float`, optional): The minimum timescale used for the first half of the embedding channels.
                        Default is 1.0.
        max_timescale (:obj:`float`, optional): The maximum timescale used for the second half of the embedding
                        channels. Default is 10000.0.
    """

    def __init__(
        self,
        *,
        min_timescale: _Optional[float] = 1.0,
        max_timescale: _Optional[float] = 10000.0,
    ):
        super().__init__()

        self.min_timescale = min_timescale
        self.max_timescale = max_timescale

    def extra_repr(self) -> str:
        """Returns a string representation of the object for debugging purposes."""
        return f"min_timescale={self.min_timescale}, max_timescale={self.max_timescale}"

    def forward(
        self,
        *,
        token_metadata: _token_metadata.TokenMetadata,
        embeddings: _torch.Tensor,
        attention_side_inputs: _Dict[_Any, _Any],
    ) -> TransformerPositionalEncodingOutput:
        positions = token_metadata.q_positions
        # Get the embedding dimension directly from the input tensor
        dim = embeddings.shape[-1]
        num_timescales = dim // 2

        # Calculate the logarithmic timescale increment
        log_timescale_increment = _math.log(
            self.max_timescale / self.min_timescale
        ) / max(1, num_timescales - 1)

        # Generate the exponent values
        exponent = [i * -log_timescale_increment for i in range(num_timescales)]

        # Compute the exponential values
        exp_values = [_math.exp(x) for x in exponent]

        # Compute the inverse timescales for each dimension
        inv_timescales = self.min_timescale * _torch.tensor(
            exp_values, dtype=embeddings.dtype, device=positions.device
        )

        # Scale the positions by the inverse timescales
        scaled_time = positions[..., None] * inv_timescales

        # Concatenate sin and cosine of the scaled time to create the positional embeddings
        pos_embeddings = _torch.cat(
            [_torch.sin(scaled_time), _torch.cos(scaled_time)], dim=-1
        )

        # Add the positional embeddings to the input embeddings
        embeddings = embeddings + pos_embeddings

        return TransformerPositionalEncodingOutput(
            embeddings=embeddings, attention_side_inputs=attention_side_inputs
        )


class SequentialPositionalEncoding(_nn.Module, _LayerMixin):
    """
    A layer that computes multiple positional encodings in sequence.

    Args:
        named_layers (:obj:`dict`): A dictionary that maps the name of each positional encoding
            layer to a :obj:`.LayerBuilder` or :obj:`nn.Module`.
    """

    def __init__(
        self,
        named_layers: _Dict[str, _nn.Module],
    ):
        super().__init__()

        # Initialize and add named layers
        for layer_name, layer in list(named_layers.items()):
            if layer is not None:
                layer = _helpers.maybe_build_module(layer)
                self.add_module(layer_name, layer)
            else:
                setattr(self, layer_name, None)
                named_layers.pop(layer_name)

    @property
    def named_layers(self) -> _collections.abc.ItemsView:
        """The names and layers in the sequence as an :obj:`ItemsView`."""
        return self._modules.items()

    @property
    def layer_names(self) -> _collections.abc.KeysView:
        """The names of layers in the sequence as a :obj:`KeysView`."""
        return self._modules.keys()

    def forward(
        self,
        *,
        token_metadata: _token_metadata.TokenMetadata,
        embeddings: _torch.Tensor,
        attention_side_inputs: _Dict[_Any, _Any],
    ) -> TransformerPositionalEncodingOutput:
        output = TransformerPositionalEncodingOutput(
            embeddings=embeddings, attention_side_inputs=attention_side_inputs
        )

        for _, layer in self.named_layers:
            output = layer(
                token_metadata=token_metadata,
                embeddings=output.embeddings,
                attention_side_inputs=output.attention_side_inputs,
            )

        return output


class SecondaryPositionalEncodings(_nn.Module, _LayerMixin):
    """
    A layer that computes additional positional encodings in a
    :class:`.TransformerStack` (other than the stack's regular
    ``positional_encoding``).  This is helpful for models that mix
    positional encoding types (such as local and global attention).

    Args:
        named_layers (:obj:`dict`): A dictionary that maps child layer
            names to positional encoding layers.
    """

    def __init__(self, named_layers: _Dict[str, _ModuleOrBuilder]):
        super().__init__()
        _helpers.append_children(self, **named_layers)

    def forward(
        self,
        *,
        token_metadata: _token_metadata.TokenMetadata,
        embeddings: _torch.Tensor,
        attention_side_inputs: _Dict[_Any, _Any],
    ) -> _Dict[str, _Dict[str, _Any]]:
        """
        Arguments are the same as :meth:`.TransformerPositionalEncoding.forward`.

        Returns:
            A dictionary that maps the name of each child layer to its
            ``attention_side_inputs`` output.
        """

        result = {}
        for name, child in self.named_children():
            attention_side_inputs_copy = dict(attention_side_inputs.items())
            _, new_attention_side_inputs = child(
                token_metadata=token_metadata,
                embeddings=embeddings,
                attention_side_inputs=attention_side_inputs_copy,
            )
            result[name] = new_attention_side_inputs
        return result
