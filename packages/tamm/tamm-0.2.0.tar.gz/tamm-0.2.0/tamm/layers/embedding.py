"""
layers.embedding
----------------

This module provides embedding layers.

.. autoclass:: tamm.layers.ConcatEmbedding
    :show-inheritance:
    :members: forward, create_builder_with_embedding

.. autoclass:: tamm.layers.ConstantEmbedding
    :show-inheritance:
    :members: forward

.. autoclass:: tamm.layers.ConvEmbedding
    :show-inheritance:
    :members:

.. autoclass:: tamm.layers.Embedding
    :show-inheritance:
    :members:

.. autoclass:: tamm.layers.UnionEmbedding
    :show-inheritance:
    :members: forward
"""

import logging as _logging
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
from torch import nn as _nn

from tamm.layers import basic as _basic
from tamm.layers import common as _layers_common
from tamm.layers import convolution as _convolution
from tamm.layers import functional as _tamm_F
from tamm.layers import init as _init
from tamm.layers import linear as _linear
from tamm.layers import multi_path as _multi_path
from tamm.layers import sequential as _sequential
from tamm.layers.common import ConfigurableLayerMixin as _ConfigurableLayerMixin
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder

_logger = _logging.getLogger(__name__)


class Embedding(_nn.Embedding, _LayerMixin):
    """
    Extension of :class:`torch.nn.Embedding` with several extra features:

    * Support for multidimensional embeddings by specifying a :obj:`tuple` for
      ``embedding_dim``.
    * Variance-scaled parameter initialization.
    * A :meth:`resize` method for easily changing the vocab size.

    The args are the same as :class:`torch.nn.Embedding` except
    ``embedding_dim`` may also be a tuple.  In this case, the layer outputs
    a tensor with shape ``(input_length, *embedding_dim)``.
    """

    def __init__(
        self,
        num_embeddings: int,
        embedding_dim: _Union[int, _Tuple[int, ...]],
        padding_idx: _Optional[int] = None,
        max_norm: _Optional[float] = None,
        norm_type: float = 2.0,
        scale_grad_by_freq: bool = False,
        sparse: bool = False,
        device=None,
        dtype=None,
    ):
        try:
            embedding_dim = int(embedding_dim)
            self.embedding_shape = (embedding_dim,)
        except (ValueError, TypeError):
            self.embedding_shape = tuple(embedding_dim)
            embedding_dim = _torch.Size(self.embedding_shape).numel()
        super().__init__(
            num_embeddings=num_embeddings,
            embedding_dim=embedding_dim,
            padding_idx=padding_idx,
            max_norm=max_norm,
            norm_type=norm_type,
            scale_grad_by_freq=scale_grad_by_freq,
            sparse=sparse,
            device=device,
            dtype=dtype,
        )

    def forward(self, *args, **kwargs):  # pylint: disable=useless-parent-delegation
        x = super().forward(*args, **kwargs)
        if len(self.embedding_shape) > 1:
            x = x.reshape(-1, *self.embedding_shape)
        return x

    def reset_parameters(self) -> None:
        _init.shape_normalized_normal_(self.weight, dim=1)

    def resize(
        self,
        new_num_embeddings: _Optional[int] = None,
        pad_to_multiple_of: _Optional[int] = None,
    ):
        """
        Resizes the token embedding layer.

        Args:
            new_num_embeddings (:obj:`_Optional[int]`): The number of tokens for
                resizing the input token embeddings layer.
            pad_to_multiple_of (:obj:`_Optional[int]`): The value for padding to
                a multiple of when resizing the input token embeddings layer.

        Returns:
            The resized embedding layer.
        """

        if pad_to_multiple_of is not None:
            if not isinstance(pad_to_multiple_of, int):
                raise ValueError(
                    f"Asking to pad the embedding matrix to a multiple of "
                    f"`{pad_to_multiple_of}`, which is not an integer. "
                    f"Please ensure you provide an integer value."
                )
            if new_num_embeddings is None:
                new_num_embeddings = self.weight.shape[0]
            new_num_embeddings = (
                (new_num_embeddings + pad_to_multiple_of - 1) // pad_to_multiple_of
            ) * pad_to_multiple_of

        if new_num_embeddings is None:
            return self

        if self.num_embeddings == new_num_embeddings:
            return self

        new_embeddings = Embedding(
            new_num_embeddings,
            self.embedding_dim,
            device=self.weight.device,
            dtype=self.weight.dtype,
        )

        # numbers of tokens to copy
        n = min(self.num_embeddings, new_num_embeddings)

        # copy token embeddings from the previous weights
        new_embeddings.weight.data[:n, :] = self.weight.data[:n, :]

        old_embeddings_requires_grad = self.weight.requires_grad
        new_embeddings.requires_grad_(old_embeddings_requires_grad)
        self.weight = new_embeddings.weight
        self.num_embeddings = new_embeddings.num_embeddings

        return self

    def __repr__(self):
        rep = super().__repr__()
        if len(self.embedding_shape) > 1:
            pieces = rep.split(",")
            end = ")" if len(pieces) == 2 else ""
            pieces[1] = f" {self.embedding_shape}{end}"
            rep = ",".join(pieces)
        return rep


class ConcatEmbedding(_nn.Module, _LayerMixin):
    """
    A layer that concatenates embeddings to the start and/or end of its inputs.

    Args:
        dim (:obj:`int`): The embedding dimension.
        num_start (:obj:`int`): The number of embeddings to prepend to the layer's
            inputs.  Defaults to 0.
        num_end (:obj:`int`): The number of embeddings to append to the layer's inputs.
            Defaults to 0.
        device: The device for parameters.
        dtype: The type for parameters.
    """

    def __init__(
        self, dim: int, *, num_start: int = 0, num_end: int = 0, device=None, dtype=None
    ):
        super().__init__()

        self.dim = dim
        self.num_start = num_start
        self.num_end = num_end

        if num_start > 0:
            self.weight_start = _torch.nn.Parameter(
                _torch.empty(num_start, dim, device=device, dtype=dtype)
            )
        else:
            self.weight_start = None

        if num_end > 0:
            self.weight_end = _torch.nn.Parameter(
                _torch.empty(num_end, dim, device=device, dtype=dtype)
            )
        else:
            self.weight_end = None

        self.reset_parameters()

    def reset_parameters(self):
        if self.weight_start is not None:
            _init.shape_normalized_normal_(self.weight_start, dim=1)
        if self.weight_end is not None:
            _init.shape_normalized_normal_(self.weight_end, dim=1)

    def extra_repr(self):
        return f"dim={self.dim}, num_start={self.num_start}, " f"num_end={self.num_end}"

    def forward(self, inputs: _torch.Tensor) -> _torch.Tensor:
        """
        Concatenates the layer's embeddings to the start and end of ``inputs`` along
        the sequence dimension.

        Args:
            inputs (:obj:`torch.Tensor`): Input embeddings with shape
                ``(batch size, seq len, dim)``.
        """
        embeddings = [inputs]
        if self.weight_start is not None:
            embeddings.insert(
                0, self._transform_to_match_inputs(self.weight_start, inputs=inputs)
            )
        if self.weight_end is not None:
            embeddings.append(
                self._transform_to_match_inputs(self.weight_end, inputs=inputs)
            )
        if len(embeddings) == 1:
            return embeddings[0]
        return _torch.cat(embeddings, dim=1)

    @staticmethod
    def _transform_to_match_inputs(embeddings, *, inputs):
        """Updates embeddings to match the dtype and batch size of inputs"""
        embeddings = embeddings.type_as(inputs)
        if inputs.size(0) == 1:
            return embeddings[None, ...]  # pylint: disable=unsubscriptable-object
        return embeddings.tile(inputs.size(0), 1, 1)

    @classmethod
    def create_builder_with_embedding(
        cls,
        embedding_builder: _layers_common.LayerBuilder,
        *,
        embedding_name: str = "embedding",
        **kwargs,
    ):
        """
        Converts a builder for an embedding layer into a builder for a sequence of
        two layers: the original embedding and a :obj:`.ConcatEmbedding`.

        Args:
            embedding_builder (:obj:`LayerBuilder`): A builder for an embedding layer.
            embedding_name (:obj:`str`, optional): A name for the embedding layer.
                Defaults to ``"embedding"``.
            kwargs: Keyword arguments for :class:`.ConcatEmbedding`.
        """
        builder = cls.Builder(**kwargs)
        return _sequential.Sequential.Builder(
            {embedding_name: embedding_builder, "concat_embedding": builder}
        )


class ConstantEmbedding(_nn.Module, _LayerMixin):
    """
    A layer that returns trainable embeddings with a fixed shape.

    Args:
        num_embeddings (:obj:`int`): The number of trainable embeddings.
        dim (:obj:`int`): The dimension of each embedding.
        device: The device for parameters.
        dtype: The dtype for parameters.
    """

    def __init__(
        self,
        num_embeddings: int,
        dim: int,
        *,
        device=None,
        dtype=None,
    ):
        super().__init__()

        self.num_embeddings = num_embeddings
        self.dim = dim

        self.weight = _torch.nn.Parameter(
            _torch.empty(num_embeddings, dim, device=device, dtype=dtype)
        )
        self.reset_parameters()

    def reset_parameters(self) -> None:
        _init.shape_normalized_normal_(self.weight, dim=1)

    def extra_repr(self) -> str:
        return f"num_embeddings={self.num_embeddings}, dim={self.dim}"

    def forward(self, inputs: _torch.Tensor) -> _torch.Tensor:
        """
        Args:
            inputs (:obj:`torch.Tensor`): An input tensor where the first dimension
                is the batch size.

        Returns:
            A tensor with shape ``(batch_size, num_embeddings, dim)`` (the embeddings
            replicated along the batch dimension).
        """
        return _tamm_F.add_batch_dim(self.weight, batch_size=inputs.size(0))


class ConvEmbedding(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    A layer for extracting embeddings via a convolution.  This is a convolution layer
    followed by optional positional encoding and rearrange layers (typically a
    :class:`.ChannelsFirstToLast`).
    """

    def __init__(
        self,
        *,
        convolution: _ModuleOrBuilder,
        positional_encoding: _OptionalModuleOrBuilder = None,
        rearrange: _OptionalModuleOrBuilder = None,
        norm: _OptionalModuleOrBuilder = None,
    ):
        layers = {
            "convolution": convolution,
            "positional_encoding": positional_encoding,
            "rearrange": rearrange,
            "norm": norm,
        }
        super().__init__(layers)

    @classmethod
    def create_basic_builder(  # pylint: disable=arguments-differ
        cls,
        *,
        input_dim: int,
        output_dim: int,
        kernel_size: _Union[_Tuple[int, ...], int],
        stride: _Optional[_Union[_Tuple[int, ...], int]] = None,
        bias: bool = False,
        apply_positional_embedding: bool = False,
        positional_embedding_shape: _Tuple[int, ...] = None,
    ) -> _layers_common.LayerBuilder:
        """
        Creates and returns a builder for a :obj:`ConvEmbedding` that maps 2D images
        in NCHW format to embeddings.

        Args:
            input_dim (:obj:`int`): The number of input channels to the convolution.
            output_dim (:obj:`int`): The dimension of the output embeddings.
            kernel_size (:obj:`tuple` of :obj:`int`): The kernel size for the
                convolution.
            stride (:obj:`tuple` of :obj:`int`, optional): The stride for the
                convolution.  If ``None``, this defaults to the kernel size.
            bias (:obj:`bool`, optional): A flag for including a bias parameter in the
                convolution when ``True``.  Defaults to ``False``.
            apply_positional_embedding (:obj:`bool`, optional): A flag for including a
                :class:`SpatialPositionalEmbedding` layer.  Defaults to ``False``.
            positional_embedding_shape (:obj:`tuple` of :obj:`int`): The spatial shape
                for the positional embedding layer if
                ``apply_positional_embedding=True``.

        Returns:
            The newly created :obj:`LayerBuilder`.
        """
        if stride is None:
            stride = kernel_size
        conv = _convolution.Conv2d.Builder(
            in_channels=input_dim,
            out_channels=output_dim,
            kernel_size=kernel_size,
            stride=stride,
            bias=bias,
        )

        if apply_positional_embedding:
            # pylint: disable-next=import-outside-toplevel,cyclic-import
            from tamm.layers import positional_encoding as _positional_encoding

            pos_encoding = _positional_encoding.SpatialPositionalEmbedding.Builder(
                positional_embedding_shape, dim=output_dim
            )
        else:
            pos_encoding = None

        rearrange = _basic.ChannelsFirstToLast.Builder()

        return cls.Builder(
            convolution=conv, positional_encoding=pos_encoding, rearrange=rearrange
        )


class UnionEmbedding(_multi_path.MultiPath, _LayerMixin):
    """
    A layer for composing multiple child embedding layers.

    Args:
        named_layers (:obj:`dict`): A dictionary that maps the name of each embedding
            layer to a builder or :obj:`nn.Module`.
        flatten_outputs (:obj:`bool`): A flag for flattening outputs of the layer.
            Defaults to ``False``.
    """

    def __init__(
        self,
        named_layers: _Dict[str, _OptionalModuleOrBuilder],
        *,
        flatten_outputs: bool = False,
    ):
        super().__init__(named_layers, combine="dict")
        self.flatten_outputs = flatten_outputs

    def extra_repr(self) -> str:
        return f"flatten_outputs={self.flatten_outputs}"

    def forward(self, inputs: _Any) -> _Union[_torch.Tensor, _Dict[str, _Any]]:
        """
        Args:
            inputs: Inputs to the child embedding layers.

        Returns:
            If ``flatten_outputs=False``, returns a :obj:`dict` that maps the name of
            each child layer to its output.  If ``flatten_outputs=True``, returns a
            single tensor with shape ``(batch_size, sequence_len, dim)``.  This flat
            tensor results from flattening the sequence dimensions of each child output
            and then concatenating the outputs along the sequence dim in the order
            of the children.
        """
        result = super().forward(inputs)
        if self.flatten_outputs:
            return _tamm_F.maybe_flatten_embeddings(result)
        return result


class LowRankFactorizedEmbedding(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    Low rank embeddings to reduce overhead associated with increased vocab.
    """

    def __init__(self, embedding: _ModuleOrBuilder, projection: _ModuleOrBuilder):
        named_layers = {"embedding": embedding, "projection": projection}
        super().__init__(named_layers)

    @classmethod
    def create_basic_builder(  # pylint: disable=arguments-differ
        cls,
        *,
        num_embeddings: int,
        rank: int,
        output_dim: int,
        padding_idx: _Optional[int] = None,
    ):
        if rank > output_dim:
            raise ValueError(f"rank={rank} exceeds output_dim={output_dim}")
        embedding = Embedding.Builder(
            num_embeddings=num_embeddings, embedding_dim=rank, padding_idx=padding_idx
        )
        projection = _linear.Linear.Builder(rank, output_dim, bias=False)
        return cls.Builder(embedding=embedding, projection=projection)
