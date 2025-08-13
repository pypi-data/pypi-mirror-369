"""
layers.segmentation
^^^^^^^^^^^^^^^^^^^

This submodule implements layers for segmenting inputs.  Typically this involves
computing a padding mask.

.. autoclass:: tamm.layers.ConcatEmbeddingSegmentation
    :show-inheritance:
    :members: forward, create_builder_with_segmentation

.. autoclass:: tamm.layers.ConstantSegmentation
    :show-inheritance:
    :members: forward

.. autoclass:: tamm.layers.ConvEmbeddingPaddingTransform
    :show-inheritance:
    :members: forward

.. autoclass:: tamm.layers.TokensPaddingMask
    :show-inheritance:
    :members: forward

.. autofunction:: compute_right_padding_mask

.. autoclass:: tamm.layers.UnionSegmentation
    :show-inheritance:
    :members: forward
"""

from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

from tamm.layers import common as _layers_common
from tamm.layers import functional as _tamm_F
from tamm.layers import multi_path as _multi_path
from tamm.layers import sequential as _sequential
from tamm.layers.common import LayerMixin as _LayerMixin
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class ConstantSegmentation(_nn.Module, _LayerMixin):
    """
    A layer that returns segment IDs with a fixed shape.

    Args:
        length (:obj:`int`): The size of the output in the sequence dimension.
        segment_id (:obj:`int`, optional): The segment ID for the outputs.  Defaults to
            ``1``.
    """

    def __init__(self, length: int, *, segment_id: int = 1):
        super().__init__()
        self.length = length
        self.segment_id = segment_id

    def extra_repr(self) -> str:
        return f"length={self.length}, segment_id={self.segment_id}"

    def forward(self, inputs: _torch.Tensor) -> _torch.Tensor:
        """
        Args:
            inputs (:obj:`torch.Tensor`): An input tensor where the first dimension
                is the batch size.

        Returns:
            A tensor with shape ``(batch_size, length)`` filled with the ``segment_id``
            value.
        """

        batch_size = inputs.size(0)
        return _torch.full(
            (batch_size, self.length), fill_value=self.segment_id, device=inputs.device
        )


class TokensPaddingMask(_nn.Module, _LayerMixin):
    """
    A layer that computes a padding mask from input token IDs.  Currently this layer
    only supports right padding, and left padding is treated as non-padding.  The
    outputs take value ``0`` for padding and ``1`` otherwise.

    .. see also:: :func:`.compute_right_padding_mask`

    Args:
        pad_token_id (:obj:`int`): The ID of the padding token.  Defaults to ``0``.
            This can also be ``None``, in which case the mask is entirely non-padding.
    """

    def __init__(self, pad_token_id: _Union[int, None] = 0):
        super().__init__()
        self.pad_token_id = pad_token_id

    def forward(self, input_ids: _torch.Tensor) -> _torch.Tensor:
        """
        Args:
            input_ids (:obj:`torch.Tensor`): A tensor of token IDs with shape
                ``(batch_size, seq_len)``.

        Returns:
            A right-padding mask.  For each input sequence, trailing tokens with value
            ``pad_token_id`` receive a ``0`` value for padding, and non-padding tokens
            receive a ``1``.
        """
        return compute_right_padding_mask(input_ids, pad_token_id=self.pad_token_id)

    def extra_repr(self):
        return f"pad_token_id={self.pad_token_id}"


def compute_right_padding_mask(
    input_ids: _torch.Tensor, *, pad_token_id: _Union[int, None] = 0
) -> _torch.Tensor:
    """
    Computes a right-padding mask.  If ``pad_token_id``, then for an input

    ::

        3, 2, 3, 0, 0
        0, 0, 0, 0, 0
        0, 5, 0, 5, 0

    we expect output

    ::

        1, 1, 1, 0, 0
        0, 0, 0, 0, 0
        1, 1, 1, 1, 0

    Args:
        input_ids (:obj:`torch.Tensor`): Sequences of token IDs with shape
            ``(batch_size, seq_len)``.
        pad_token_id (:obj:`int`): The ID of the padding token.  Defaults to ``0``.
            This can also be ``None``, in which case there is no padding.

    Returns:
        A right-padding mask with ``0`` values for padding and ``1`` for non-padding.
    """
    if pad_token_id is None:
        return _torch.ones_like(input_ids)

    padding_mask = input_ids.ne(pad_token_id)
    return (
        padding_mask.fliplr()
        .cumsum(dim=1, dtype=_torch.int32)
        .ne(0)
        .fliplr()
        .type(input_ids.dtype)
        # use cumsum here instead of cummax bc MPS does not support cummax in torch 2.0
    )


class UnionSegmentation(_multi_path.MultiPath, _LayerMixin):
    """
    A layer for composing multiple child segmentation layers.

    Args:
        named_layers (:obj:`dict`): A dictionary that maps the name of each segmentation
            layer to a builder or :obj:`nn.Module`.
        flatten_outputs (:obj:`bool`): A flag for flattening outputs of the layer.
            Defaults to ``False``.
    """

    # pylint: disable=duplicate-code

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

    # pylint: disable-next=redefined-builtin,arguments-differ
    def forward(self, input: _Any) -> _Union[_torch.Tensor, _Dict[str, _Any]]:
        """
        Args:
            input: Inputs to the child segmentation layers.

        Returns:
            If ``flatten_outputs=False``, returns a :obj:`dict` that maps the name of
            each child layer to its output.  If ``flatten_outputs=True``, returns a
            single tensor with shape ``(batch_size, sequence_len)``.  This flat tensor
            results from flattening the sequence dimensions of each child output
            and then concatenating the outputs along the sequence dim in the order
            of the children.
        """
        result = super().forward(input)
        if self.flatten_outputs:
            return _tamm_F.maybe_flatten_sequence(result)
        return result


class ConvEmbeddingPaddingTransform(_nn.Module, _LayerMixin):
    """
    A layer for pooling padding values when using a :obj:`ConvEmbedding` layer.
    """

    def __init__(
        self,
        *,
        kernel_size: _Union[_Tuple[int, ...], int],
        stride: _Optional[_Union[_Tuple[int, ...], int]] = None,
        padding: _Optional[_Union[_Tuple[int, ...], int]] = 0,
        dilation: _Optional[_Union[_Tuple[int, ...], int]] = 1,
    ):
        super().__init__()
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.dilation = dilation

    def extra_repr(self):
        def check_all_equal(option, value):
            """Option may be either a tuple or a number"""
            try:
                for x in option:
                    if x != value:
                        return False
                return True
            except TypeError:
                return option == value

        extras = [f"kernel_size={self.kernel_size}", f"stride={self.stride}"]
        if not check_all_equal(self.padding, 0):
            extras.append(f"padding={self.padding}")
        if not check_all_equal(self.dilation, 1):
            extras.append(f"dilation={self.dilation}")
        return ", ".join(extras)

    @classmethod
    def create_builder_from_convolution_layer(
        cls, convolution
    ) -> _layers_common.LayerBuilder:
        """
        Creates a builder for a :obj:`ConvEmbeddingPaddingTransform` from a
        convolution layer.  This input must have ``kernel_size``, ``stride``,
        ``padding``, and ``dilation`` attributes.
        """
        return cls.Builder(
            kernel_size=convolution.kernel_size,
            stride=convolution.stride,
            padding=convolution.padding,
            dilation=convolution.dilation,
        )

    def forward(self, padding_mask: _torch.Tensor) -> _torch.Tensor:
        """
        Args:
            padding_mask (:obj:`torch.Tensor`): An ``n+1`` dimensional padding mask
                where ``n`` is the dimension of the convolution.  The first dimension
                is the batch dimension and the remaining dimensions must match the shape
                of the convolution's inputs along the conv dimensions (such as the
                height and width in the 2D case).  The mask should have ``0`` values for
                padding inputs and ``1`` otherwise.

        Returns:
            A max-pooled padding mask of shape ``(batch_size, seq_len)``.  Tokens have
            value ``1`` if they correspond to patches with at least one non-padding
            value.  Otherwise they have value ``0``.
        """
        input_dtype = padding_mask.dtype
        padding_mask = padding_mask.float()  # max_pool ops do not work with ints

        ndim = padding_mask.ndim - 1
        if ndim == 1:
            op = _torch.max_pool1d
        elif ndim == 2:
            op = _torch.max_pool2d
        elif ndim == 3:
            op = _torch.max_pool3d
        else:
            raise RuntimeError("Expected padding_mask to have 2, 3, or 4 dimensions")

        padding_mask = op(
            padding_mask,
            kernel_size=self.kernel_size,
            stride=self.stride,
            padding=self.padding,
            dilation=self.dilation,
        )

        padding_mask = padding_mask.type(input_dtype)
        return padding_mask.reshape(padding_mask.size(0), -1)


class ConcatEmbeddingSegmentation(_nn.Module, _LayerMixin):
    """
    A segmentation layer to use with :obj:`.ConcatEmbedding` layers.  To account for
    concatenated embeddings, this layer concats extra segment IDs to the beginning
    and/or end of segment ID inputs.
    """

    def __init__(self, *, segment_id: int = 1, num_begin: int = 0, num_end: int = 0):
        super().__init__()
        self.num_begin = num_begin
        self.num_end = num_end
        self.segment_id = segment_id

    def extra_repr(self):
        return (
            f"segment_id={self.segment_id}, num_begin={self.num_begin}, "
            f"num_end={self.num_end}"
        )

    def forward(self, segment_ids: _torch.Tensor) -> _torch.Tensor:
        """
        Prepends and appends ``segment_id`` values to ``segment_ids`` along the sequence
        dimension.

        Args:
            segment_ids (:obj:`torch.Tensor`): Segment IDs with shape
                ``(batch size, seq len)``.
        """
        batch_size = segment_ids.size(0)
        pieces = [segment_ids]

        if self.num_begin > 0:
            begin_piece = _torch.full(
                size=(batch_size, self.num_begin),
                fill_value=self.segment_id,
                dtype=segment_ids.dtype,
                device=segment_ids.device,
            )
            pieces.insert(0, begin_piece)

        if self.num_end > 0:
            end_piece = _torch.full(
                size=(batch_size, self.num_end),
                fill_value=self.segment_id,
                dtype=segment_ids.dtype,
                device=segment_ids.device,
            )
            pieces.append(end_piece)

        if len(pieces) == 1:
            return pieces[0]
        return _torch.cat(pieces, dim=1)

    @classmethod
    def create_builder_with_segmentation(
        cls,
        segmentation_builder: _layers_common.LayerBuilder,
        *,
        segmentation_name: str = "segmentation",
        **kwargs,
    ):
        """
        Converts a builder for a segmentation layer into a builder for a sequence of
        two layers: the original segmentation and a :obj:`.ConcatEmbeddingSegmentation`.

        Args:
            segmentation_builder (:obj:`LayerBuilder`): A builder for a segmentation
                layer.
            segmentation_name (:obj:`str`, optional): A name for the segmentation layer.
                Defaults to ``"segmentation"``.
            kwargs: Keyword arguments for :class:`.ConcatEmbeddingSegmentation`.
        """
        builder = cls.Builder(**kwargs)
        layers = {
            segmentation_name: segmentation_builder,
            "concat_embedding_segmentation": builder,
        }
        return _sequential.Sequential.Builder(layers)
