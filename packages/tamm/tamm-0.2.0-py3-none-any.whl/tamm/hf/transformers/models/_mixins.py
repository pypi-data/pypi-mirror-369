"""
Mixins for Hugging Face transformers wrappers.
"""

import logging as _logging
import os as _os
from typing import Optional as _Optional

import transformers as _transformers

from tamm import _helpers, model_repo
from tamm.hf.transformers.models import registry as _registry
from tamm.runtime_configuration import rc as _rc
from tamm.typing import PathLike as _PathLike

_logger = _logging.getLogger(__name__)


class FromModelIDMixin:
    """
    A mixin for adding :meth:`from_tamm_model_id` and
    :meth:`save_pretrained_for_tamm_model_id` methods to
    :class:`transformers.PreTrainedModel` subclasses.
    """

    @classmethod
    def from_tamm_model_id(
        cls, model_id: str, *model_args, **kwargs
    ) -> _transformers.PreTrainedModel:
        """
        Creates a Hugging Face version of a tamm model.  This method fetches pretrained
        weights and stores them locally in ``$HOME/.tamm`` to speed up future calls. It
        supports standard Hugging Face options for :meth:`from_pretrained`.

        Args:
            model_id (:obj:`str`): The tamm model id.
            *model_args, **kwargs: Arguments to pass to
                :meth:`transformers.PreTrainedModel.from_pretrained` when initializing
                the model.

        Returns:
            A :obj:`transformers.PreTrainedModel` instance of the tamm model.
        """
        save_directory = cls.save_pretrained_for_tamm_model_id(model_id)
        return cls.from_pretrained(save_directory, *model_args, **kwargs)

    @classmethod
    def save_pretrained_for_tamm_model_id(
        cls, model_id: str, save_directory: _Optional[_PathLike] = None
    ) -> _PathLike:
        """
        Saves a "pretrained" directory for loading tamm models with Hugging Face
        transformers :meth:`from_pretrained` methods.

        Args:
            model_id (:obj:`str`): The tamm model id.
            save_directory (:obj:`PathLike`, optional): The path for saving the
                pretrained model.  If ``None``, the method uses a default path in
                ``$HOME/.tamm``.  If the directory already exists, this function assumes
                it is a cached copy of the model and returns without saving a new one.

        Returns:
            The path to the pretrained model.
        """

        if save_directory is None:
            save_directory = _os.path.join(_rc.user_dir, "hf", model_id)
        lock_path = _os.path.join(_rc.user_dir, "hf", f"{model_id}.cache_lock")

        with _helpers.file_lock(lock_path):
            if _os.path.exists(save_directory):
                _logger.info("Found cached model at %s", save_directory)
                return save_directory

            config = model_repo.create_model_config(model_id)
            # pylint: disable-next=protected-access
            hf_cls = _registry._get_hf_model_type(config.__class__)
            model = hf_cls.from_tamm_config(config)

            _logger.info("Writing model to %s", save_directory)
            model.save_pretrained(save_directory)
            return save_directory
