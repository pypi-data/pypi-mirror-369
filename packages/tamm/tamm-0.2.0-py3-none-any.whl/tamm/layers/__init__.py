"""
tamm.layers
-----------
"""

from tamm.layers import common, functional, init, mixture_of_experts, torch_nn
from tamm.layers.activation import (
    CELU,
    ELU,
    GEGLU,
    GELU,
    GLU,
    SELU,
    BilinearActivation,
    HardSigmoid,
    HardSwish,
    HardTanh,
    LambdaActivation,
    LeakyReLU,
    Mish,
    PReLU,
    QuickGELU,
    ReGLU,
    ReLU,
    ReLU6,
    RReLU,
    Sigmoid,
    SiLU,
    Softmax,
    Softplus,
    SoftShrink,
    Softsign,
    SwiGLU,
    Tanh,
    TanhShrink,
)
from tamm.layers.attention import (
    KVReuseTransformerAttention,
    QKNorm,
    QKVLinear,
    RoPETransform,
    ScaledDotProductAttention,
    TransformerAttention,
)
from tamm.layers.basic import (
    ChannelsFirstToLast,
    ChannelsLastToFirst,
    ExpandDim,
    Flatten,
    Index,
    Interpolation,
    InversePermute,
    Map,
    Mean,
    MoveDim,
    MultiplyByScale,
    PadToMultiple,
    Permute,
    SelectByKey,
    SoftCap,
    Sum,
    Transpose,
    Unflatten,
    Union,
)
from tamm.layers.common import ModuleConfig
from tamm.layers.convolution import (
    CausalConv1d,
    Conv1d,
    Conv2d,
    ResNetBlock,
    ResNetStage,
    SqueezeExcitation,
)
from tamm.layers.decoding import KVCacher
from tamm.layers.dropout import Dropout
from tamm.layers.embedding import (
    ConcatEmbedding,
    ConstantEmbedding,
    ConvEmbedding,
    Embedding,
    LowRankFactorizedEmbedding,
    UnionEmbedding,
)
from tamm.layers.feed_forward import FeedForward, TransformerFeedForward
from tamm.layers.lambda_layer import Lambda
from tamm.layers.linear import (
    FusedMultiOutputLinear,
    Linear,
    MultiOutputLinear,
    SegmentedLinear,
    TiedWeightLinear,
    TiedWeightLinearSequence,
    VectorizedLinear,
)
from tamm.layers.loss import FlattenedCrossEntropyLoss
from tamm.layers.multi_path import MultiPath
from tamm.layers.norm import BatchNorm, CausalGroupNorm, L2Norm, LayerNorm, RMSNorm
from tamm.layers.pooler import (
    AdaptiveConvPooler,
    CAbstractorPooler,
    ConvPooler,
    SimpleAdaptiveAvgPooler,
)
from tamm.layers.positional_encoding import (
    AbsolutePositionalEmbedding,
    SpatialPositionalEmbedding,
)
from tamm.layers.residual import (
    GatedActivationResidualConnection,
    NormalizedResidualConnection,
    ResidualAdd,
    ResidualScaledAdd,
    ShortcutAddActResidualConnection,
)
from tamm.layers.segmentation import (
    ConcatEmbeddingSegmentation,
    ConstantSegmentation,
    ConvEmbeddingPaddingTransform,
    TokensPaddingMask,
    UnionSegmentation,
)
from tamm.layers.sequential import Sequential
from tamm.layers.side_outputs import OutputWithSideOutputs
from tamm.layers.transformer import (
    ALiBiPositionalEncoding,
    AttentionMask,
    AudioTransformerEncoder,
    CausalLMTransformer,
    ExtendedTransformerStack,
    KVReuseTransformerLayerSequence,
    NoPositionalEncoding,
    RotaryPositionalEmbedding,
    SecondaryPositionalEncodings,
    SegmentedTransformerLayerSequence,
    SequentialPositionalEncoding,
    SinusoidalPositionalEmbedding,
    SlidingWindowPositionalEncoding,
    TextTransformerEncoder,
    TransformerAbsolutePositionalEmbedding,
    TransformerLayer,
    TransformerLayerSequence,
    TransformerPositionalEncoding,
    TransformerStack,
    TransformerTokenTypeEmbedding,
    TransformerTokenTypeEncoding,
    UniformTransformerLayerSequence,
    VisionTransformerEncoder,
    kv_cache,
)
