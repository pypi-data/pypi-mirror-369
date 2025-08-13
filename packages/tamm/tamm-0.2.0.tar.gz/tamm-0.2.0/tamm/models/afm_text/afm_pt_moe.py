from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

from tamm import layers as _L
from tamm.layers import mixture_of_experts as _moe_layers
from tamm.layers.transformer.layer_sequence import parallel_track as _pt_layers


class AFMParallelTrackMoEConfig(_L.ModuleConfig):
    """
    A parallel track mixture-of-experts language model. This model combines multiple
    smaller transformers (tracks) that process tokens independently.  The model groups
    transformer layers into segments, and the tracks synchronize after each segment by
    averaging the hidden states across tracks.

    The model interleaves local and global attention layers.  The local attention layers
    combine rotary positional encodings (RoPE) with sliding window attention.  The
    global attention layers use no positional encodings (NoPE), including no windowing.

    The model also interleaves dense and sparse (MoE) feed forward layers.  For the MoE
    layers, each track has its own set of experts.

    This model implementation is vectorized, meaning that it stacks parameters and
    intermediate states from across tracks into single tensors.  Generally it uses
    fused ops to compute layer outputs from all tracks simultaneously.
    """

    vocab_size: int = 153600
    """The vocab size."""

    num_tracks: int = 8
    """The number of parallel tracks (paths) in the transformer sequence."""

    num_layers_per_track: int = 48
    """The number of transformer layers in each track."""

    num_layers_per_track_per_sync_point: int = 4
    """
    The size of each segment (block) in the transformer sequence.  The parallel
    tracks synchronize only at the end of each segment.
    """

    hidden_dim: int = 2048
    """The number of features in each transformer layer's inputs/outputs."""

    attention_hidden_dim: int = 512
    """The hidden dimension within attention layers."""

    dense_feed_forward_hidden_dim: int = 5888
    """The hidden dimension of dense (non-MoE) feed forward layers."""

    sparse_feed_forward_hidden_dim: int = 2944
    """
    The hidden dimension (per expert) of sparse (mixture-of-experts) feed forward
    layers."""

    num_heads: int = 4
    """The number of attention heads."""

    num_kv_heads: _Optional[int] = None
    """
    The number of key-value attention heads for grouped query attention.  If ``None``,
    this defaults to ``num_heads``.  If not ``None``, this value must evenly divide
    ``num_heads``.
    """

    rope_theta: float = 500000.0
    """
    The ``theta`` value for :class:`.RotaryPositionalEmbedding`.  Defaults to ``500000``.
    """

    attention_layer_pattern: _Tuple[str, ...] = (
        "local_rope",
        "local_rope",
        "local_rope",
        "global_nope",
    )
    """
    The specification of local (sliding window + RoPE) or global attention (NoPE) for
    each layer. This is a tuple containing any number of ``"local_rope"`` and
    ``"global_nope"`` strings.  In each track, transformer layer ``i`` uses attention
    type ``attention_layer_pattern[i % pattern_len]`` (where ``pattern_len`` is the
    length of this list).
    """

    local_attention_window_size: int = 4096
    """
    The length of the attention window for local attention layers.  This window size
    excludes the current token, meaning that the attention actually happens among
    ``local_attention_window_size + 1`` tokens (following the convention of
    FlashAttention and others).
    """

    sdpa_implementation: str = "auto"
    """The :class:`.SDPAImplementationChoice` for attention layers."""

    feed_forward_layer_pattern: _Tuple[str, ...] = ("dense", "sparse")
    """
    The specification of sparse (mixture-of-experts) or dense feed forward for each
    transformer layer.  This is a tuple containing any number of ``"sparse"`` and
    ``"dense"`` strings.  In each track, transformer layer ``i`` uses feed forward
    type ``feed_forward_layer_pattern[i % pattern_len]`` (where ``pattern_len`` is the
    length of this list).
    """

    num_experts: int = 40
    """
    The number of experts (per track) in sparse feed forward layers.  Each track has
    its own sets of experts.
    """

    num_experts_per_token: int = 2
    """
    The number of experts (per track) to evaluate for each token in each sparse feed
    forward layer.
    """

    experts_router_logits_cap: float = 50.0
    """
    The cap value for soft capping logits in the router of MoE layers (prior to the
    softmax).  Set to ``None`` for no soft capping.
    """

    pre_norm: _Union[str, None] = "rms_norm"
    """
    The pre-norm type for attention and feed forward layers, such as ``"rms_norm"``
    or ``"pre_scale_rms_norm"``.  This is a vectorized norm that happens at the
    start of these layers. Set to ``None`` for no pre-norm.
    """

    post_norm: _Union[str, None] = None
    """
    The post-norm type for attention and feed forward layers (after the residual
    add).  This is a vectorized norm.  Set to ``None`` for no post-norm.
    """

    pre_residual_norm: _Union[str, None] = None
    """
    The pre-residual norm type for attention and feed forward layers.  This is
    a vectorized norm that happens immediately before the residual add in these
    layers. Set to ``None`` for no pre-residual norm.
    """

    tracks_dispatch_norm: _Union[str, None] = None
    """
    The vectorized norm type applied to the outputs of "dispatch" layers at the
    start of each segment.  The dispatch layer replicates hidden states across tracks,
    and each track has its own set of norm parameters.  Defaults to ``None``.
    """

    tracks_combine_norm: _Union[str, None] = None
    """
    The vectorized norm type applied to the inputs of "combine" layers at the
    end of each segment.  Each track has its own set of norm parameters, and
    the combine layer averages hidden states across tracks.  Defaults to ``None``.
    """

    scale_qk_norm: bool = True
    """
    A flag for adding trainable weight parameters to QK norm layers.  Defaults to
    ``True``.
    """

    norm_eps: float = 1e-5
    """The epsilon value for norm layers, which prevents division by zero."""

    tracks_combine_op: str = "mean"
    """
    The op for reducing tracks at the end of each segment.  Must be either ``"mean"``
    or ``"sum"``.
    """

    hidden_dropout_p: float = 0.0
    """The dropout probability for hidden states."""

    attention_dropout_p: float = 0.0
    """The dropout probability for attention scores."""

    output_hidden_states: bool = False
    """
    A flag for including hidden states in the model's output.  This is a list of
    ``num_layers_per_track`` tensors that includes the initial embeddings and the
    output of each layer.
    """

    output_attentions: bool = False
    """
    A flag for including attention scores in the model's output.  Specifically, this
    is a list of ``num_layers`` tensors that includes attention scores from each
    attention layer.
    """

    output_expert_assignments: bool = False
    """
    A flag that when ``True`` results in the inclusion of expert assignments in the
    model model's output. This is a list of expert assignments from each sparse
    feed forward layer.
    """

    @property
    def dim_per_head(self) -> int:
        """The number of features per token per head in attention layers."""
        if self.attention_hidden_dim % self.num_heads != 0:
            raise ValueError(
                f"num_heads ({self.attention_hidden_dim}) does not evenly divide "
                f"attention_hidden_dim ({self.attention_hidden_dim})"
            )
        return self.attention_hidden_dim // self.num_heads

    @property
    def num_segments(self) -> int:
        """The number of synchronization points in the layer sequence."""
        segment_size = self.num_layers_per_track_per_sync_point
        if self.num_layers_per_track % segment_size != 0:
            raise ValueError(
                f"num_layers_per_track_per_sync_point ({segment_size}) does not "
                f"evenly divide num_layers_per_track ({self.num_layers_per_track})"
            )
        return self.num_layers_per_track // segment_size

    def create_basic_builder(self) -> _L.common.LayerBuilder:
        builder = _L.CausalLMTransformer.Builder()
        builder.embedding = _L.Embedding.Builder(
            num_embeddings=self.vocab_size,
            embedding_dim=self.hidden_dim,
            padding_idx=0,
        )
        builder.attention_mask = _L.transformer.AttentionMask.Builder(is_causal=True)
        builder.positional_encoding = self._create_local_rope_positional_encoding()
        builder.secondary_positional_encodings = _L.SecondaryPositionalEncodings.Builder(
            {"global_nope": _L.NoPositionalEncoding()}
            # the model mixes local and global attention (where global uses NoPE)
            # we represent the global attention as a secondary positional encoding
        )
        builder.layers = self._create_transformer_layers_builder()
        builder.output_norm = _L.RMSNorm.Builder([self.hidden_dim], eps=self.norm_eps)
        builder.output_transform_build_mode = "pass_embedding"
        builder.output_transform = _L.TiedWeightLinear.Builder(parameter_name="weight")
        return builder

    def _create_local_rope_positional_encoding(self):
        """Combines RoPE with sliding window attention"""
        named_layers = {
            "rope": _L.RotaryPositionalEmbedding.Builder(
                dim_per_head=self.dim_per_head, theta=self.rope_theta
            ),
            "sliding_window": _L.SlidingWindowPositionalEncoding.Builder(
                self.local_attention_window_size
            ),
        }
        return _L.SequentialPositionalEncoding.Builder(named_layers)

    def _create_transformer_layers_builder(self):
        """
        The layers are a sequence of segments (blocks), where each sequence is a
        :class:`.ParallelTrackTransformerLayerSequence`.
        """
        layers = []
        layer_idx_to_attention_type = {}

        for layer_idx in range(self.num_layers_per_track):
            attention_type = self._get_attention_type_for_layer(layer_idx)
            if attention_type in ("local", "local_rope"):
                attention = self._create_local_rope_attention()
            elif attention_type == "global_nope":
                attention = self._create_global_nope_attention()
                layer_idx_to_attention_type[layer_idx] = "global_nope"
            else:
                raise ValueError(f"Attention type '{attention_type}' not recognized")

            feed_forward_type = self._get_feed_forward_type_for_layer(layer_idx)
            if feed_forward_type == "sparse":
                ff = self._create_sparse_feed_forward()
            elif feed_forward_type == "dense":
                ff = self._create_dense_feed_forward()
            else:
                raise ValueError(
                    f"Feed forward type '{feed_forward_type}' not recognized"
                )

            layer = _L.TransformerLayer.Builder(attention=attention, feed_forward=ff)
            layers.append(layer)

        return _pt_layers.ParallelTrackTransformerLayerSequenceConfig.create_builder(
            sequence=layers,
            num_tracks=self.num_tracks,
            num_layers_per_track_per_sync_point=self.num_layers_per_track_per_sync_point,
            dispatch=self._create_track_merger_dispatch(),
            combine=self._create_track_merger_combine(),
            attention_types=layer_idx_to_attention_type,
            output_hidden_states=self.output_hidden_states,
        )

    def _get_attention_type_for_layer(self, layer_idx):
        pattern_len = len(self.attention_layer_pattern)
        return self.attention_layer_pattern[layer_idx % pattern_len]

    def _get_feed_forward_type_for_layer(self, layer_idx):
        pattern_len = len(self.feed_forward_layer_pattern)
        return self.feed_forward_layer_pattern[layer_idx % pattern_len]

    def _create_track_merger_dispatch(self):
        if self.tracks_dispatch_norm is None:
            return None  # use the default dispatch
        return _L.Sequential.Builder(
            {
                "dispatch": _L.ExpandDim.Builder(
                    self.num_tracks, dim=1, unsqueeze=True
                ),
                "norm": self._create_vectorized_norm(
                    self.tracks_dispatch_norm, dim=self.hidden_dim
                ),
            }
        )

    def _create_track_merger_combine(self):
        if self.tracks_combine_op.lower() == "mean":
            combine = _L.Mean.Builder(dim=1)
        elif self.tracks_combine_op.lower() == "sum":
            combine = _L.Sum.Builder(dim=1)
        else:
            raise ValueError(f"Combine op f{self.tracks_combine_op} not recognized")

        if self.tracks_combine_norm is None:
            return combine
        return _L.Sequential.Builder(
            {
                "norm": self._create_vectorized_norm(
                    self.tracks_combine_norm, dim=self.hidden_dim
                ),
                "combine": combine,
            }
        )

    def _create_vectorized_norm(self, norm_spec, *, dim):
        return _L.norm.create_vectorized_norm_builder(
            (self.num_tracks, dim), norm_spec, vectorized_dim=1, eps=self.norm_eps
        )

    def _create_residual_connection(self):
        """
        Creates a builder for the residual connection in attention and feed forward
        layers.
        """
        if self.pre_residual_norm is None and self.post_norm is None:
            return _L.ResidualAdd.Builder()
        pre_residual_norm = self._create_vectorized_norm(
            self.pre_residual_norm, dim=self.hidden_dim
        )
        post_norm = self._create_vectorized_norm(self.post_norm, dim=self.hidden_dim)
        return _L.residual.NormalizedResidualConnection.Builder(
            pre_residual_norm=pre_residual_norm, post_norm=post_norm
        )

    def _create_local_rope_attention(self):
        builder = _L.TransformerAttention.create_builder(
            target_dim=self.hidden_dim,
            num_heads=self.num_heads,
            num_kv_heads=self.num_kv_heads,
            norm=self._create_vectorized_norm(self.pre_norm, dim=self.hidden_dim),
            attention_dropout_p=self.attention_dropout_p,
            hidden_dropout_p=self.hidden_dropout_p,
            output_attentions=self.output_attentions,
            sdpa_implementation=self.sdpa_implementation,
            apply_rope=True,
            apply_qk_norm=True,
            atten_hidden_dim=self.attention_hidden_dim,
            vec_dim=(self.num_tracks,),
        )
        if self.scale_qk_norm:
            builder.qk_norm.query_norm = self._create_vectorized_norm(
                "rms_norm", dim=self.dim_per_head
            )
            builder.qk_norm.key_norm = self._create_vectorized_norm(
                "rms_norm", dim=self.dim_per_head
            )
        else:
            builder.qk_norm.query_norm = _L.RMSNorm(eps=self.norm_eps)
            builder.qk_norm.key_norm = _L.RMSNorm(eps=self.norm_eps)
        builder.residual_connection = self._create_residual_connection()
        return builder

    def _create_global_nope_attention(self):
        builder = self._create_local_rope_attention()
        builder.rope_transform = None
        return builder

    def _create_sparse_feed_forward(self):
        builder = _L.mixture_of_experts.MixtureOfExperts.Builder(
            output_expert_assignments=self.output_expert_assignments
        )
        builder.norm = self._create_vectorized_norm(self.pre_norm, dim=self.hidden_dim)
        builder.router = _moe_layers.MixtureOfExpertsRouter.create_builder(
            input_dim=self.hidden_dim,
            num_experts=self.num_experts,
            num_experts_per_token=self.num_experts_per_token,
            logits_cap=self.experts_router_logits_cap,
            include_logits_loss=False,
            include_load_balance_loss=False,
        )
        builder.router.input_transform = _L.linear.VectorizedLinear.Builder(
            in_features=self.hidden_dim,
            out_features=self.num_experts,
            vec_dim=[self.num_tracks],
        )
        builder.dispatcher = _moe_layers.DroplessMixtureOfExpertsDispatcher.Builder(
            num_experts=self.num_experts, track_dim=1
        )
        builder.experts = _L.TransformerFeedForward.create_builder(
            input_dim=self.hidden_dim,
            hidden_dim=self.sparse_feed_forward_hidden_dim,
            activation="swi_glu",
            norm=None,
            apply_residual_add=False,
            vec_dim=(self.num_tracks, self.num_experts),
            activation_dropout_p=self.hidden_dropout_p,
            output_dropout_p=self.hidden_dropout_p,
            use_segmented_linear=True,
        )
        builder.residual_connection = self._create_residual_connection()
        return builder

    def _create_dense_feed_forward(self):
        builder = _L.TransformerFeedForward.create_builder(
            input_dim=self.hidden_dim,
            hidden_dim=self.dense_feed_forward_hidden_dim,
            norm=self._create_vectorized_norm(self.pre_norm, dim=self.hidden_dim),
            activation=_L.SwiGLU.Builder(),
            vec_dim=(self.num_tracks,),
            activation_dropout_p=self.hidden_dropout_p,
            output_dropout_p=self.hidden_dropout_p,
        )
        builder.residual_connection = self._create_residual_connection()
        return builder
