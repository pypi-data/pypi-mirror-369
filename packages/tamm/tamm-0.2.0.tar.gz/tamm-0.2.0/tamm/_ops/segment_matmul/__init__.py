"""
segment matrix multiplication
=============================

This module provides functionality for performing grouped matrix multiplication
(aka grouped gemm) on segmented input tensors. This is useful for MoE models.

.. autofunction:: tamm.layers.segment_matmul.segment_matmul

https://github.com/pytorch/FBGEMM
https://github.com/tgale96/grouped_gemm
https://triton-lang.org/main/getting-started/tutorials/08-grouped-gemm.html
"""

from tamm._ops.segment_matmul.interface import segment_matmul

__all__ = [
    "segment_matmul",
]
