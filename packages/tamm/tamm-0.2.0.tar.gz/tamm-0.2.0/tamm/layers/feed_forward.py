"""
layers.feed_forward
^^^^^^^^^^^^^^^^^^^

This submodule implements general feed-forward layers.

.. autoclass:: tamm.layers.FeedForward
    :show-inheritance:
    :members: create_builder
"""

from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

from tamm import _adapters_v1
from tamm.layers import activation as _activation
from tamm.layers import dropout as _dropout
from tamm.layers import linear as _linear
from tamm.layers import norm as _norm
from tamm.layers import residual as _residual
from tamm.layers import sequential as _sequential
from tamm.layers.common import ConfigurableLayerMixin as _ConfigurableLayerMixin
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class FeedForward(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    A simple :obj:`FeedForward` network with any number of hidden layers.  The output
    is the result of the following layer sequence:

    * Hidden transform 0
    * Activation 0
    * Activation dropout 0
    * Hidden transform 1
    * Activation 1
    * Activation dropout 1
    * ...
    * Output transform
    * Output dropout

    Args:
        * hidden_transforms: A :obj:`list` of hidden transform layers
            (:obj:`.LayerBuilder` or :obj:`torch.nn.Module`).
        * activations: A :obj:`list` of activation layer specifications.  Each element
            must be a valid argument to
            :func:`.layers.activation.create_activation_layer`.  The length of this
            arg must match the length of ``hidden_transforms``.
        * activation_dropouts: An optional :obj:`list` of activation dropout layers.
            Defaults to ``None``, which omits activation dropout.  If provided, the
            length must match the length of ``activations``.
        * output_transform: The output transform layer.
        * output_dropout: The output dropout layer.
    """

    def __init__(
        self,
        *,
        hidden_transforms: _List[_ModuleOrBuilder],
        activations: _List[_ModuleOrBuilder],
        activation_dropouts: _Optional[_List[_ModuleOrBuilder]] = None,
        output_transform: _ModuleOrBuilder,
        output_dropout: _OptionalModuleOrBuilder = None,
    ):
        self._validate_hidden_layers(
            hidden_transforms, activations, activation_dropouts
        )

        layers = {}
        for idx, hidden_transform in enumerate(hidden_transforms):
            layers[f"hidden_transform_{idx}"] = hidden_transform
            layers[f"activation_{idx}"] = _activation.create_activation_layer(
                activations[idx]
            )
            layers[f"activation_dropout_{idx}"] = (
                activation_dropouts[idx] if activation_dropouts is not None else None
            )
        layers["output_transform"] = output_transform
        layers["output_dropout"] = output_dropout

        super().__init__(layers, unpack_tuple_inputs=True)

    def _validate_hidden_layers(self, transforms, activations, dropouts):
        if len(transforms) != len(activations):
            raise ValueError("hidden_transforms and activations have different lengths")
        if dropouts is None:
            return
        if len(activations) != len(dropouts):
            raise ValueError(
                "acitvations and activation_dropouts have different lengths"
            )

    @classmethod
    def create_basic_builder(
        cls,
        *,
        input_dim: int,
        hidden_dim: _Optional[_Union[int, _List[int]]] = None,
        output_dim: _Optional[int] = None,
        num_layers: int = 2,
        activation: _activation.ActivationSpecType = "relu",
        hidden_transform_bias: bool = False,
        output_transform_bias: bool = False,
        activation_dropout_p: float = 0.0,
        output_dropout_p: float = 0.0,
    ):  # pylint: disable=arguments-differ,too-many-locals
        """
        Creates a builder for a simple :obj:`.FeedForward` layer with linear hidden
        and output transforms.  The hidden dimension and activation is consistent
        across layers.

        Args:
            input_dim (:obj:`int`): The feature dimension of the inputs.
            hidden_dim (:obj:`int` or :obj:`List[int]`):
                The dimensions of the hidden transform(s).
                If a list is provided, the length must equal to `num_layers-1`.
                If an integer is provided, this implies all the hidden layer(s) will
                have the same dimension.  If ``None``, all the hidden layer(s)
                will use ``input_dim`` as their dimension(s).
            output_dim (:obj:`int`): The dimension of the outputs.  If ``None``, this
                defaults to ``input_dim``.
            num_layers (:obj:`int`): The depth of the network, i.e., the number of
                ``hidden_transform`` layers plus one.  Defaults to ``2``.
            activation: The activation spec.  This should be a valid argument to
                :func:`.layers.activation.create_activation_layer`.
            hidden_transform_bias (:obj:`bool`): A flag for including a bias parameter
                in the hidden transforms.  Defaults to ``False``.
            output_transform_bias (:obj:`bool`): A flag for including a bias parameter
                in the output transform.  Defaults to ``False``.
            activation_dropout_p (:obj:`float`): The dropout parameter for activation
                tensors.  Defaults to ``0``.
            output_dropout_p (:obj:`float`): The dropout parameter for output
                tensors.  Defaults to ``0``.

        Returns:
            The configured :obj:`.LayerBuilder`.
        """
        if hidden_dim is None:
            hidden_dim = input_dim

        if isinstance(hidden_dim, int):
            hidden_dim = [hidden_dim] * (num_layers - 1)

        if not isinstance(hidden_dim, list):
            raise ValueError(
                "Unsupport type for optional argument ``hidden_dim``. "
                "Supported types are `int` and `List[int]`."
            )
        if len(hidden_dim) != num_layers - 1:
            raise ValueError(
                "Length of ``hidden_dim`` must be ``num_layers``-1. Got "
                f"len(hidden_dim)={len(hidden_dim)} and num_layers={num_layers}."
            )
        hidden_dims = hidden_dim

        if output_dim is None:
            output_dim = input_dim

        hidden_transforms = []
        for dim in hidden_dims:
            if _activation.is_activation_gated(activation):
                hidden_transform = _linear.MultiOutputLinear.Builder(
                    input_dim,
                    2 * [dim],
                    bias=hidden_transform_bias,
                )
            else:
                hidden_transform = _linear.Linear.Builder(
                    input_dim, dim, bias=hidden_transform_bias
                )
            hidden_transforms.append(hidden_transform)
            input_dim = dim

        activations = [activation] * (num_layers - 1)

        activation_dropout = _dropout.Dropout.Builder(p=activation_dropout_p)
        activation_dropouts = [activation_dropout] * (num_layers - 1)

        output_transform = _linear.Linear.Builder(
            hidden_dims[-1] if len(hidden_dims) > 0 else input_dim,
            output_dim,
            bias=output_transform_bias,
        )

        output_dropout = _dropout.Dropout.Builder(p=output_dropout_p)

        return cls.Builder(
            hidden_transforms=hidden_transforms,
            activations=activations,
            activation_dropouts=activation_dropouts,
            output_transform=output_transform,
            output_dropout=output_dropout,
        )


class TransformerFeedForward(_sequential.Sequential, _ConfigurableLayerMixin):
    """
    Feed-forward layer with residual connection.  The output is the result of the
    following layer sequence:

    * Norm
    * Hidden transform
    * Activation
    * Dropout
    * Output transform
    * Dropout
    * Norm
    * Residual add
    * Norm

    Args:
        norm: The norm layer (:obj:`nn.Module`) or builder (callable that returns the
            norm layer when called without args).
        hidden_transform: The first transform layer or builder.
        activation: The activation layer or builder.  This can be any argument for
            ``tamm.layers.activation.create_activation_layer``.
        activation_dropout: The first dropout layer or builder.
        output_transform: The second transform layer or builder.
        output_dropout: The second dropout layer or builder.
        residual_connection: The residual connection layer of builder.


    Users can also create this layer using its :meth:`create` method, which has
    simpler args.  Alternatively, use :meth:`create_builder` to create the layer via
    a configurable builder.
    """

    def __init__(
        self,
        *,
        norm: _ModuleOrBuilder,
        hidden_transform: _ModuleOrBuilder,
        activation: _activation.ActivationSpecType,
        activation_dropout: _ModuleOrBuilder,
        output_transform: _ModuleOrBuilder,
        output_dropout: _ModuleOrBuilder,
        residual_connection: _ModuleOrBuilder,
        adapter_target_prefix_str: str,
    ):
        self.adapter_target_prefix_str = adapter_target_prefix_str
        activation = _activation.create_activation_layer(activation)
        named_layers = {
            "norm": norm,
            "hidden_transform": hidden_transform,
            "activation": activation,
            "activation_dropout": activation_dropout,
            "output_transform": output_transform,
            "output_dropout": output_dropout,
        }
        super().__init__(
            named_layers,
            unpack_tuple_inputs=True,
            residual_connection=residual_connection,
        )
        self._mark_adaptable_layers()

        # Segmented linear option accepts group_sizes side inputs
        self.register_side_input("hidden_transform", "group_sizes")
        self.register_side_input("output_transform", "group_sizes")

    @classmethod
    def create_basic_builder(
        cls,
        *,
        input_dim: int,
        hidden_dim: int,
        norm: _Union[str, _OptionalModuleOrBuilder] = "layer_norm",
        activation: _Optional[_activation.ActivationSpecType] = None,
        activation_dropout_p: float = 0.0,
        hidden_transform_bias: bool = False,
        output_transform_bias: bool = False,
        output_dropout_p: float = 0.0,
        apply_residual_add: bool = True,
        vec_dim: _Optional[_List[int]] = None,
        adapter_target_prefix_str: str = "",
        use_segmented_linear: bool = False,
        apply_pre_norm: bool = True,
        apply_pre_residual_norm: bool = False,
        apply_post_norm: bool = False,
    ):  # pylint: disable=arguments-differ,too-many-locals
        """
        Creates and returns a default builder for creating :obj:`TransformerFeedForward`
        objects.  The builder uses a :class:`LayerNorm` norm layer, linear transforms,
        and ReLU activation.

        Use :meth:`create` to directly create a feed forward layer.

        Args:
            input_dim (:obj:`int`): The input dimension.  This should equal the last
                value of the input shape.
            hidden_dim (:obj:`int`): The hidden dimension.
            norm: The norm layer (:obj:`nn.Module`) or builder (a callable that returns
                the norm layer when called without args).  If ``None``, this defaults to
                :class:`LayerNorm`.
            activation: The activation layer or builder.  This can be any argument for
                ``tamm.layers.activation.create_activation_layer``.  If ``None``, this
                defaults to :class:`ReLU`.
            activation_dropout_p (:obj:`float`): The dropout probability for
                activations.
            hidden_transform_bias (:obj:`bool`): Whether the hidden transform layers
                uses a bias or not.
            output_transform_bias (:obj:`bool`): Whether the output transform layer
                uses a bias or not.
            output_dropout_p (:obj:`float`): The dropout probability for outputs (prior
                to the residual add).
            apply_residual_add (:obj:`bool`): Whether the feed forward layer uses a
                residual connection or not.
            apply_pre_norm (:obj:`bool`): Whether to apply normalization before the
                feed forward computation. Defaults to ``True``.
            apply_pre_residual_norm (:obj:`bool`): Whether to apply normalization after the
                attention computation but before the residual connection. Defaults to ``False``.
                If ``True``, ``apply_residual_add`` must also be ``True``.
            apply_post_norm (:obj:`bool`): Whether to apply normalization after the
                residual connection using PostNormResidualConnection. When ``True``,
                requires ``apply_residual_add`` to also be ``True``. Defaults to ``False``.

        Returns:
            A configured :obj:`TransformerFeedForward.Builder`.
        """

        # High level args for vectorized linear / linear kwargs
        multioutput_linear_kwargs = {}
        linear_cls = _linear.Linear
        linear_kwargs = {}
        if vec_dim is not None:
            multioutput_linear_kwargs["vec_dim"] = vec_dim
            linear_kwargs["vec_dim"] = vec_dim
            linear_cls = _linear.VectorizedLinear

        # For segmented linear, linear class is segmented gemm, with vectorized dimension inputs
        if use_segmented_linear:
            linear_cls = _linear.SegmentedLinear
            multioutput_linear_kwargs["override_linear_cls"] = _linear.SegmentedLinear

        norm = _norm.create_norm_builder((input_dim,), spec=norm)
        if activation is None:
            activation = _activation.ReLU.Builder()

        if _activation.is_activation_gated(activation):
            hidden_transform = _linear.MultiOutputLinear.Builder(
                input_dim,
                2 * [hidden_dim],
                bias=hidden_transform_bias,
                **multioutput_linear_kwargs,
            )
        else:
            hidden_transform = linear_cls.Builder(
                input_dim, hidden_dim, bias=hidden_transform_bias, **linear_kwargs
            )
        activation_dropout = _dropout.Dropout.Builder(p=activation_dropout_p)

        output_transform = linear_cls.Builder(
            hidden_dim,
            input_dim,
            bias=output_transform_bias,
            **linear_kwargs,
        )
        output_dropout = _dropout.Dropout.Builder(p=output_dropout_p)

        norm = _norm.create_norm_builder((input_dim,), spec=norm)

        # pylint: disable-next=protected-access
        residual_connection = _residual._maybe_create_residual_add_builder(
            apply_residual_add=apply_residual_add,
            apply_pre_residual_norm=apply_pre_residual_norm,
            apply_post_norm=apply_post_norm,
            norm=norm,
        )

        return cls.Builder(
            norm=norm if apply_pre_norm else None,
            hidden_transform=hidden_transform,
            activation=activation,
            activation_dropout=activation_dropout,
            output_transform=output_transform,
            output_dropout=output_dropout,
            residual_connection=residual_connection,
            adapter_target_prefix_str=adapter_target_prefix_str,
        )

    def _mark_adaptable_layers(self):
        output_transform_layer_type = (
            "BatchedFeedForwardOutputTransform"
            if isinstance(self.output_transform, _linear.VectorizedLinear)
            else "FeedForwardOutputTransform"
        )
        _adapters_v1.annotate_layer(
            self.output_transform,
            [(output_transform_layer_type,)],
        )

        layers = (
            [self.hidden_transform.linear_0, self.hidden_transform.linear_1]
            if self.activation.is_gated
            else [self.hidden_transform]
        )

        for layer in layers:
            layer_type = (
                "BatchedFeedForwardHiddenTransform"
                if isinstance(layer, _linear.VectorizedLinear)
                else "FeedForwardHiddenTransform"
            )
            _adapters_v1.annotate_layer(
                layer,
                [(layer_type,)],
            )
