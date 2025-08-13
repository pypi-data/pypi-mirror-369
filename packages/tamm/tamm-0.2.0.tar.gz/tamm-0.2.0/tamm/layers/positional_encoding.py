"""
layers.positional_encoding
--------------------------

This module implements layers for encoding positions into tensors.

.. autoclass:: tamm.layers.AbsolutePositionalEmbedding
    :show-inheritance:
    :members: create_builder, forward

.. autoclass:: tamm.layers.SpatialPositionalEmbedding
    :show-inheritance:
    :members: forward
"""

import enum as _enum
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

import tamm.layers.functional
from tamm import _helpers
from tamm.layers import basic as _basic
from tamm.layers import embedding as _embedding
from tamm.layers import init as _init
from tamm.layers.common import ConfigurableLayerMixin as _ConfigurableLayerMixin
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.typing import ModuleBuilder as _ModuleBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class AbsolutePositionalEmbedding(_torch.nn.Module, _ConfigurableLayerMixin):
    """
    Layer for absolute positional embeddings.  This layer maps positions to trainable
    embedding tensors and then adds these embeddings to the token embeddings.

    Args:
        embedding: An embedding layer (or builder) that maps positions to embeddings.
        sequence_start (:obj:`int`, optional): An option that controls which tokens
            receive positional embeddings.  If ``sequence_start > 0``, then the first
            ``sequence_start`` tokens do not receive positional embeddings.
    """

    def __init__(
        self,
        embedding: _ModuleBuilder,
        sequence_start: _Optional[int] = None,
    ):
        super().__init__()
        self.embedding = _helpers.maybe_build_module(embedding)
        self.sequence_start = sequence_start

    @classmethod
    def create_basic_builder(  # pylint: disable=arguments-differ
        cls,
        num_embeddings: int,
        embedding_dim: int,
        *,
        sequence_start: _Optional[int] = None,
    ) -> _ModuleBuilder:
        """
        Creates and returns a builder for :class:`AbsolutePositionalEmbedding` layers.

        Args:
            num_embeddings (:obj:`int`): The number of embeddings in the positional
                embedding table.
            embedding_dim (:obj:`int`): The dimension of the embeddings.
            sequence_start (:obj:`int`, optional): The ``sequence_start`` option for the
                layer.

        Returns:
            The configured :obj:`LayerBuilder`.
        """
        embedding = _embedding.Embedding.Builder(
            num_embeddings=num_embeddings,
            embedding_dim=embedding_dim,
        )
        return cls.Builder(
            embedding=embedding,
            sequence_start=sequence_start,
        )

    def _maybe_broadcast_embedding(
        self, inputs: _torch.Tensor, pos_embeddings: _torch.Tensor
    ) -> _torch.Tensor:
        """
        If there's a dimension mismatch between inputs and pos_embeddings,
        we broadcast pos_embeddings to match with inputs.
        """
        num_dim = len(inputs.shape)
        while num_dim - 1 > len(pos_embeddings.shape):
            pos_embeddings = pos_embeddings.unsqueeze(1)
        return pos_embeddings

    def forward(
        self,
        inputs: _torch.Tensor,
        *,
        positions: _Optional[_torch.Tensor] = None,
    ) -> _torch.Tensor:
        """
        Args:
            inputs (:obj:`torch.Tensor`): Input embeddings with shape
                ``(batch_size, sequence_len, dim)``.
            positions (:obj:`torch.Tensor`): Optional position integers with shape
                ``(batch_size, sequence_len)``.  Defaults to ``0, 1, ...`` for each
                sequence.
        """

        if self.sequence_start in (None, 0):
            start_inputs = None
        else:
            start_inputs = inputs[:, : self.sequence_start]
            inputs = inputs[:, self.sequence_start :]
            if positions is not None:
                positions = positions[:, self.sequence_start :]

        if positions is None:
            positions = _torch.arange(inputs.size(1), device=inputs.device)

        pos_embeddings = self.embedding(positions)
        pos_embeddings = self._maybe_broadcast_embedding(
            inputs=inputs, pos_embeddings=pos_embeddings
        )
        pos_embeddings = pos_embeddings.type_as(inputs)
        outputs = inputs + pos_embeddings

        if start_inputs is not None:
            return _torch.cat([start_inputs, outputs], dim=1)
        return outputs

    def extra_repr(self) -> str:
        if self.sequence_start in (None, 0):
            return ""
        return f"sequence_start={self.sequence_start}"


class SpatialPositionalEmbeddingCropMode(str, _enum.Enum):
    """
    Options for the crop behavior of :class`.SpatialPositionalEmbedding` layers.
    """

    #: Keep the top-left pieces of the weight parameter.
    TOP_LEFT = "TOP_LEFT"


class SpatialPositionalEmbedding(_nn.Module, _LayerMixin):
    """
    A layer for applying absolute positional embeddings to spatial inputs, such as
    NCHW image tensors.

    Args:
        spatial_shape (:obj:`tuple` of :obj:`int`): The spatial dimensions of the
            inputs.  For images, this is ``(height, width)``.
        dim (:obj:`int`): The embedding dimension (i.e., number of channels).
        interpolation (:obj:`.LayerBuilder` or :obj:`str`, optional): An
            :obj:`.Interpolation` layer for rescaling the spatial embeddings to match
            the shape of the layer's inputs.  If a :obj:`str`, this must be an
            interpolation mode, such as ``"bicubic"``.  Defaults to ``None``.
        interpolation_shape (:obj:`tuple` of :obj:`int`): The target size for
            interpolating positional embeddings.  Defaults to ``auto``.
            - If `"auto"`, the positional embedding weight is resized to match the input shape.
            - If a tuple is provided, the weight is resized to the given shape.
        input_features_dim (:obj:`int`): The index of the features (channels)
            dimension of the inputs.  This is ``1`` by default (for channels-first
            inputs).  Set this to ``-1`` for channels-last inputs.
        weight_crop_mode: (:obj:`str`, optional): Set to ``"top_left"`` to crop
            the (possibly interpolated) weight parameter when its size exceeds the size
            of the inputs.  Defaults to ``None``.
        device: The device for parameters.
        dtype: The dtype for parameters.
    """

    def __init__(
        self,
        spatial_shape: _Tuple[int, ...],
        dim: int,
        *,
        interpolation: _Union[_OptionalModuleOrBuilder, str] = None,
        interpolation_shape: _Union[str, _Tuple[int, ...]] = "auto",
        input_features_dim: int = 1,
        weight_crop_mode: _Optional[str] = None,
        device=None,
        dtype=None,
    ):
        super().__init__()

        self.spatial_shape = spatial_shape
        self.dim = dim

        if isinstance(interpolation, str):
            interpolation = _basic.Interpolation(mode=interpolation)
        self.interpolation = _helpers.maybe_build_module(interpolation)

        if interpolation_shape != "auto":
            interpolation_shape = tuple(interpolation_shape)
        self.interpolation_shape = interpolation_shape
        if self.interpolation is not None and self.interpolation_shape is None:
            raise ValueError(
                "interpolation_size should be specified when interpolation is needed"
            )

        self.input_features_dim = input_features_dim

        if weight_crop_mode is not None:
            weight_crop_mode = _helpers.get_enum_member_from_name(
                SpatialPositionalEmbeddingCropMode, weight_crop_mode
            )
        self.weight_crop_mode = weight_crop_mode

        weight_shape = (dim, *spatial_shape)
        self.weight = _torch.nn.Parameter(
            _torch.empty(weight_shape, device=device, dtype=dtype)
        )
        self.reset_parameters()

    def reset_parameters(self) -> None:
        _init.shape_normalized_normal_(self.weight, dim=0)

    def extra_repr(self) -> str:
        return (
            f"shape={self.spatial_shape}, "
            f"dim={self.dim}, "
            f"interpolation_shape={self.interpolation_shape}, "
            f"weight_crop_mode={self.weight_crop_mode}"
        )

    def forward(self, inputs: _torch.Tensor) -> _torch.Tensor:
        """
        Args:
            inputs (:obj:`torch.Tensor`): Inputs with shape
                ``(batch_size, dim, *spatial_shape)``.

        Returns:
            The sum of the inputs and (possibly interpolated) positional embeddings.
        """

        weight = self.weight[None, ...]

        input_features_dim = self.input_features_dim % inputs.ndim
        inputs_spatial_shape = tuple(
            x
            for idx, x in enumerate(inputs.shape)
            if idx not in (0, input_features_dim)
        )

        if self.interpolation is not None:
            if (
                self.interpolation_shape == "auto"
                and weight.shape[2:] != inputs_spatial_shape
            ):
                weight = self.interpolation(weight, size=inputs_spatial_shape)
            elif weight.shape[2:] != self.interpolation_shape:
                weight = self.interpolation(weight, size=self.interpolation_shape)

        if self.weight_crop_mode is SpatialPositionalEmbeddingCropMode.TOP_LEFT:
            weight = tamm.layers.functional.crop(weight, shape=inputs_spatial_shape)

        if input_features_dim != 1:
            weight = weight.movedim(1, self.input_features_dim)

        return inputs + weight
