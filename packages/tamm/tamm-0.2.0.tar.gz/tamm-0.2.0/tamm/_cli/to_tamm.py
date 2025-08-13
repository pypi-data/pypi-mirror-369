"""Command for converting model checkpoints from a different format to tamm"""

import logging
from typing import Optional

import torch

from tamm import converters
from tamm._cli.common import argument, command

logger = logging.getLogger(__name__)


@command(
    "to-tamm", help_text="Convert model checkpoints from a different format to tamm"
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
    help="Source path to the model state to convert to tamm",
)
@argument(
    "converter-id",
    type=str,
    help=(
        "A converter id that specifies how to do the conversion--use "
        "``tamm ls converters -l`` for descriptions of available converters"
    ),
)
def to_tamm(converter_id, source, dest, dtype: Optional[str] = None):
    state_dict = converters.load(source, converter=converter_id, dtype=dtype)
    logger.info("Saving tamm state dict to %s", dest)
    torch.save(state_dict, dest)
    logger.info("Done!")
