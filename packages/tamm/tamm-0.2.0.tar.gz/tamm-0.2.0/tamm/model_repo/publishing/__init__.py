"""
Publishing
==========

.. autoclass:: tamm.model_repo.publishing.ModelPublisher
.. autoclass:: tamm.model_repo.publishing.PublishedModelConfig

"""

from tamm.model_repo.publishing.base import ModelPublisher
from tamm.model_repo.publishing.config import PublishedModelConfig

__all__ = ["PublishedModelConfig", "ModelPublisher"]
