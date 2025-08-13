import logging
from pathlib import Path as _Path
from typing import Union as _Union

import torch as _torch

from tamm.utils.uri import _URIHandler

_logger = logging.getLogger(__name__)


def fetch_file(
    remote_path: str,
) -> _Path:
    """
    Fetch large artifacts (e.g., model checkpoints, and tokenizer vocabs) from remote
    storage. Utilizes local diskcache as per implementation selected by URI handler.

    Args:
        remote_path: URI in string

    Returns: Local file path of the first successfully fetched remote path

    """

    return _URIHandler(use_cache=True).map_to_local(remote_path)


def fetch_checkpoint(
    remote_path: str,
    *,
    map_location: _Union[int, _torch.device] = None,
    weights_only: bool = True,
) -> dict:
    """
    Fetch Pytorch checkpoint from remote storage. Utilizes local diskcache as per
    implementation selected by URI handler.

    Args:
        remote_path (:obj:`str`): URI of remote checkpoint e.g., s3://bucket/ckpt.pt
        map_location(:obj:`Union[str,torch.device]`): It indicates the location where all tensors should be loaded.
        weights_only (:obj:`bool`): Indicates whether unpickler should be restricted to loading
            only tensors, primitive types, dictionaries and any types added via
            torch.serialization.add_safe_globals()

    Returns: Pytorch state dictionary

    """

    with _URIHandler(use_cache=True).open(remote_path, mode="rb") as fptr:
        state_dict = _torch.load(
            fptr, weights_only=weights_only, map_location=map_location
        )
    _logger.info("State dictionary is loaded into memory from the checkpoint file.")
    return state_dict
