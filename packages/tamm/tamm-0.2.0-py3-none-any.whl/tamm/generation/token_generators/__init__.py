"""
generation.token_generators
===========================

.. autoclass:: tamm.generation.token_generators.TokenGenerator
    :members:
    :inherited-members:

.. autoclass:: tamm.generation.token_generators.GreedyTokenGenerator
    :members:
    :inherited-members:

.. autoclass:: tamm.generation.token_generators.SamplingTokenGenerator
    :members:
    :inherited-members:
"""

from tamm.generation.token_generators.base import TokenGenerator
from tamm.generation.token_generators.greedy import GreedyTokenGenerator
from tamm.generation.token_generators.sampling import SamplingTokenGenerator
from tamm.generation.token_generators.speculative import (
    SpeculativeDecodingTokenGenerator,
)
