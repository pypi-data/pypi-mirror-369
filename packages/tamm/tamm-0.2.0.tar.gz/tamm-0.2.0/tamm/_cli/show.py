"""
Command for showing the model config when given its model id as input.
"""
import logging
import pprint
import warnings

import tamm
from tamm import _helpers
from tamm._adapters_v1.utils import get_num_adapter_params
from tamm._cli.common import argument, command
from tamm.utils import torch_utils as _torch_utils

logger = logging.getLogger(__name__)
# pylint: disable=redefined-builtin


@command("show", help_text="Print a tamm config")
@argument(
    "name",
    metavar="<OBJECT_ID>",
    type=str,
    help=(
        "Any identifiers recognized by tamm--use ``tamm ls models -l`` "
        "or ``tamm ls preprocessors``, etc., for available options"
    ),
)
def show_object(name):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            config = tamm.create_model_config(name)
        print(config)
        with _helpers.catch_and_log_exceptions(context_name="print model size"):
            _print_model_size(config)
        return
    except Exception:
        logger.debug("%s does not exist in model registry", name)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            config = tamm.create_tokenizer_config(name)
        print(config)
        return
    except Exception:
        logger.debug("%s does not exist in tokenizer registry", name)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            config = tamm.preprocessors.describe(name)
        pprint.pprint(config, compact=True, width=100)
        return
    except Exception:
        logger.debug("%s does not exist in preprocessors registry", name)

    print(f"{name} is neither a recognized model id, tokenizer id, nor preprocessor id")


def _print_model_size(config):
    model = config.create_model(device="meta")
    num_params = _torch_utils.get_num_params(model)
    num_adapter_params = get_num_adapter_params(model)
    print(f"Parameter count: {num_params}")
    print(f"Adapter parameter count: {num_adapter_params}")

    num_bytes = num_params * 2
    num_bytes = _helpers.size_in_bytes_to_string(num_bytes)
    print(f"Model size (fp16): {num_bytes}")
