"""Command for converting model checkpoints from tamm to other formats."""

import collections as _collections
import logging
from typing import Optional

import torch as _torch

from tamm import converters
from tamm._cli.common import argument, command

logger = logging.getLogger(__name__)


def parse_extra_metadata(metadata: str) -> dict:
    """Helper method to convert a metadata string to a dictionary,
    metadata string should follow the format "key1=val1,key2=val2".
    """
    expected_keys = {"num_heads": int, "num_kv_heads": int}

    metadata = dict([item.split("=") for item in metadata.split(",")])
    results = {}
    for key, cast_type in expected_keys.items():
        val = metadata.pop(key, None)
        if val:
            results[key] = cast_type(val)
    return results


@command("from-tamm", help_text="Convert model checkpoints from tamm to a new format")
@argument(
    "--metadata",
    type=str,
    help="Optional metadata for the state dict in the format key1=val1,key2=val2",
)
@argument(
    "--dtype",
    type=str,
    help="Optional output dtype, such as float16, float32, etc",
)
@argument("dest", type=str, help="Destination path for the converted model state")
@argument(
    "source",
    type=str,
    help="Source path to a tamm model state dict (saved by :func:`torch.save`)",
)
@argument(
    "converter-id",
    type=str,
    help=(
        "A converter id that specifies how to do the conversion--use "
        "``tamm ls converters -l`` for descriptions of available converters"
    ),
)
def from_tamm(
    converter_id: str,
    source: str,
    dest: str,
    dtype: Optional[str] = None,
    metadata: str = None,
    weights_only: bool = True,
) -> None:
    logger.info(f"Initiating conversion: Loading tamm state dict from {source}.")
    state_dict = _torch.load(source, weights_only=weights_only)

    if metadata is not None:
        metadata = parse_extra_metadata(metadata)
        if len(metadata) > 0:
            state_dict = _collections.OrderedDict(state_dict)
            # pylint: disable=protected-access
            metadata.update(
                state_dict._metadata if hasattr(state_dict, "_metadata") else {}
            )
            state_dict._metadata = metadata
            logger.info(f"Added extra metadata {metadata} to state dict.")

    converters.save(state_dict, dest, converter=converter_id, dtype=dtype)
    logger.info(f"Conversion completed: Model state saved to {dest}.")
