import torch as _torch
import torch.nn as _nn

from tamm import layers as _layers
from tamm.ao.arch_optimizers import common as _common
from tamm.utils import OptionalBool as _OptionalBool


class LowRankEmbeddingsOptimizer(_common.ArchOptimizer):
    """
    An :class:`.ArchOptimizer` that applies low rank embeddings to the model.
    """

    rank: int = 64

    def _optimize_impl(
        self,
        model: _nn.Module,
        *,
        pretrained: "_OptionalBool" = _OptionalBool.NOTSET,
    ) -> None:
        """
        prduces a low rank embedding model from a high rank embedding model
        """
        full_embedding = model.embedding.weight.detach()
        pad_token_id = model.embedding.padding_idx

        vocab_size, hidden_dim = full_embedding.shape

        in_embed, proj_embed = self.reset_from_high_rank(full_embedding, rank=self.rank)

        assert in_embed.shape == (vocab_size, self.rank)
        assert proj_embed.shape == (hidden_dim, self.rank)

        low_rank_embedding = _layers.LowRankFactorizedEmbedding.create(
            num_embeddings=vocab_size,
            rank=self.rank,
            output_dim=hidden_dim,
            padding_idx=pad_token_id,
        )

        low_rank_embedding.embedding.weight.data.copy_(in_embed.data)
        low_rank_embedding.projection.weight.data.copy_(proj_embed.data)
        low_rank_output_transform = _layers.TiedWeightLinearSequence(
            module=low_rank_embedding,
            parameter_names=["projection.weight", "embedding.weight"],
            transpose_flags=[True, False],
        )
        model.embedding = low_rank_embedding
        model.output_transform = low_rank_output_transform

    def reset_from_high_rank(
        self, high_rank_matrix, rank=64
    ) -> tuple[_torch.Tensor, _torch.Tensor]:
        """
        Decompose a high-rank matrix into two low-rank matrices using SVD.

        Args:
            high_rank_matrix (torch.Tensor): The matrix to decompose.
            rank (int): Target rank for decomposition.

        Returns:
            tuple[torch.Tensor, torch.Tensor]: Low-rank matrices for input and projection embeddings.
        """
        # pylint: disable=not-callable
        u_matrix, singular_values, vt_matrix = _torch.linalg.svd(
            high_rank_matrix, full_matrices=False
        )
        u_reduced = u_matrix[:, :rank]
        s_reduced = singular_values[:rank]
        vt_reduced = vt_matrix[:rank, :]

        input_embedding = u_reduced * _torch.sqrt(s_reduced)
        projection_embedding = _torch.sqrt(s_reduced).unsqueeze(1) * vt_reduced

        return input_embedding.clone(), projection_embedding.T.clone()
