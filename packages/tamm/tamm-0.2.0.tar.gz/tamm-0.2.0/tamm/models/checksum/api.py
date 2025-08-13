import logging as _logging
from typing import Callable as _Callable
from typing import Optional as _Optional
from typing import Union as _Union

from torch import nn as _nn

from tamm import model_repo
from tamm._adapters_v1.utils import maybe_rekey_state_dict
from tamm.layers import ModuleConfig as _ModuleConfig
from tamm.model_repo.publishing import PublishedModelConfig as _PublishedModelConfig
from tamm.models.checksum import _checksum

_logger = _logging.getLogger(__name__)


class UnmatchedSourceKeyError(RuntimeError):
    pass


def _get_source_module(
    model_spec: _Union[_nn.Module, _Callable[..., _nn.Module]],
    source_spec: _Optional[
        _Union[_nn.Module, str, _ModuleConfig, _PublishedModelConfig]
    ] = None,
    device="cpu",
) -> _nn.Module:
    """
    Get a fully instantiated source model on CPU for hashing
    """
    create_kwargs = {"pretrained": True, "device": device}
    if source_spec is not None:
        if isinstance(source_spec, _nn.Module):
            return source_spec
        if isinstance(source_spec, str):
            # source_spec is model ID
            return model_repo.get_model_repo_lazy().create_model(
                source_spec, **create_kwargs
            )
        if isinstance(source_spec, _ModuleConfig):
            return source_spec.create_model(**create_kwargs)
        if isinstance(source_spec, _PublishedModelConfig):
            return source_spec.model_config.create_model(**create_kwargs)
        raise ValueError(
            f"Unknown source_spec {source_spec} " f"(type {type(source_spec)})"
        )
    _logger.debug(
        "source_spec is None, using model metadata to determine the source model"
    )
    if isinstance(source_spec, _nn.Module):
        model = model_spec
    else:
        # model_spec is a Callable
        # create model on meta because we only need metadata
        model = model_spec(pretrained=False, device="meta")
    try:
        source_model_id = model.metadata.source_model_tamm_id
    except AttributeError as e:
        raise AttributeError(
            "source_spec required, if model doesn't have ``source_tamm_model_id``"
        ) from e

    model_config = model_repo.get_model_repo_lazy().create_model_config(source_model_id)
    return model_config.create_model(**create_kwargs)


def compare_checksum_with_source(
    model: _nn.Module,
    source_spec: _Optional[
        _Union[_nn.Module, str, _ModuleConfig, _PublishedModelConfig]
    ] = None,
) -> bool:
    # pylint:disable=line-too-long
    """
    Compares ``model`` weights with ``source model``'s weights

    By default, ``model.metadata.source_model_tamm_id`` will
    be used to determine source model weights to compare with.
    Optionally, user can supply ``source_spec``
    to compare source model's weights against weights defined by another
    ``source_model``, ``source_model_config`` or ``source_model_id``

    Args:
        model (:obj:`nn.Module`): Any |tamm| model
        source_spec (:obj:`nn.Module` or model ID :obj:`str` or :obj:`PublishedModelConfig` or :obj:`ModuleConfig`, optional):
            alternate source of the model to compare with

    Examples:

        * Compare model's **backbone** with another pretrained-model:

        Suppose you want to compare a LoRA fine-tuned model with its backbone,you
        may use this utility function with an explicit reference to the backbone model
        (i.e., model w/o adapter), like below

        .. code-block:: python

            model = tamm.create_model(model_id)
            compare_checksum_to_source(
                model,
                source_spec=model.metadata.source_model_details["backbone_tamm_model_id"]
            )

        Note that the specification ``source_spec=model.metadata.source_model_details["backbone_tamm_model_id"]`` is required because
        by default, this function uses ``model.metadata.source_model_tamm_id`` as a comparison target.

        .. tip::

            ``source_spec`` can be model config or the model instance if needed. e.g.,

            .. code-block:: python

                compare_checksum_to_source(
                    model,
                    source_spec=tamm.create_model_config(model_id)

                )

            or

            .. code-block:: python

                compare_checksum_to_source(
                    model,
                    source_spec=tamm.create_model(model_id)
                )

        * Compare a model with its original copy:

        Suppose you want to compare a fine-tuned model
        with the original copy from |tamm|, use

        .. code-block:: python

            model = tamm.create_model(model_id)
            # apply changes to the model, such as fine-tuning
            assert not compare_checksum_to_source(
                model
            ) # the output is expected to be False because the model is altered

    Returns:
        ``True`` if ``model``'s weights are the same as the reference
        source, otherwise ``False``

    """

    def model_factory(pretrained, device):  # pylint: disable=unused-argument
        return model

    return compare_factory_checksum_with_source(model_factory, source_spec=source_spec)


def compare_factory_checksum_with_source(
    model_factory: _Callable[..., _nn.Module],
    source_spec: _Optional[
        _Union[_nn.Module, str, _ModuleConfig, _PublishedModelConfig]
    ] = None,
) -> bool:
    """
    Compares ``model`` weights with ``source model``'s weights, using model factory
    to defer the creation of candidate model.

    model_factory(...) is expected to return the actual model. This function requires
    half of the peak memory then :meth:`compare_checksum_with_source` because
    ``model`` and ``source model`` are sequentially loaded.

    Args:
        model_factory: A callable which understands argument
            pretrained(=[True, False]) and device(=["meta", "cpu"]).
        source_spec: See :meth:`compare_checksum_with_source`

    .. tip::

        model_factory can be a partially evaluated :meth:`tamm.create_model`

        .. code-block:: python

            from functools import partial

            model_factory = partial(tamm.create_model, model_id)
            assert compare_checksum_with_source_factory(model_factory)

    Returns:
         ``True`` if ``model``'s weights are the same as the reference
         source, otherwise ``False``
    """
    # pylint:enable=line-too-long
    source_model = _get_source_module(model_factory, source_spec)
    source_sd = source_model.state_dict()
    source_keys = frozenset(source_sd.keys())

    def _compute_checksum(_model, name):
        """
        Only compute checksum within the subset of state dictionary filtered by
        ``source_keys``
        """
        _logger.debug("model has keys:")
        for key in sorted(list(_model.keys())):
            _logger.debug("\t%s", key)
        _logger.debug("Computing checksum for %s on keys:", name)
        for key in sorted(list(source_keys)):
            _logger.debug("\t%s", key)
        return _checksum.state_dict_checksum(_model, source_keys)

    source_checksum = _compute_checksum(source_sd, "source_model")
    _logger.debug("source_checksum = %s", source_checksum)
    del source_sd  # free memory once source model has been hashed
    candidate_model = model_factory(pretrained=True, device="cpu")
    candidate_state_dict = candidate_model.state_dict()
    candidate_state_dict = maybe_rekey_state_dict(source_model, candidate_state_dict)
    del source_model  # free memory once source model has been hashed
    unmatched_source_keys = source_keys - frozenset(candidate_state_dict.keys())
    if unmatched_source_keys:
        raise UnmatchedSourceKeyError(
            f"source model has the following keys which don't "
            f"exist in 'model': "
            f"'{unmatched_source_keys}'"
        )

    model_checksum = _compute_checksum(candidate_state_dict, "model")
    _logger.debug("model_checksum = %s", model_checksum)
    return model_checksum == source_checksum
