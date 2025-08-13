import logging as _logging
from typing import List, Union, cast

from tamm._plugin import utils as plugin_utils
from tamm.preprocessors.base import Preprocessor
from tamm.preprocessors.registry import (
    PreprocessorRegistry,
    URIHandlerPreprocessorRegistry,
)
from tamm.runtime_configuration import rc

_logger = _logging.getLogger(__name__)


def get_registry() -> PreprocessorRegistry:
    entrypoints = plugin_utils.discover_plugin_extras(
        rc.PLUGINS_EXTRAS_ENTRYPOINT_NAMES.preprocessor_registry
    )
    preprocessor_registry = cast(PreprocessorRegistry, URIHandlerPreprocessorRegistry())
    for entrypoint in entrypoints:
        extra_registry = plugin_utils.execute_plugin_object_reference(
            entrypoint.value,
            call_obj=True,
        )
        preprocessor_registry += cast(PreprocessorRegistry, extra_registry)

    return preprocessor_registry


def create(
    preprocessor_name: Union[str, "Preprocessor"], *args, **kwargs
) -> "Preprocessor":
    """
    Create a preprocessor instance for the specified preprocessor name.

    Args:
        preprocessor_name (:obj:`str`): The name of the preprocessor to be created.
        *args: Additional positional arguments for preprocessor creation.
        **kwargs: Additional keyword arguments for preprocessor creation.

    Returns:
        :obj:`Preprocessor`: Created preprocessor instance.
    """
    return get_registry().create(preprocessor_name, *args, **kwargs)


def describe(preprocessor_name: Union[str, "Preprocessor"], *args, **kwargs) -> dict:
    """
    Describe a preprocessor instance by a dictionary

    Args:
        preprocessor_name (:obj:`str`): The name of the preprocessor to be created.
        *args: Additional positional arguments for preprocessor creation.
        **kwargs: Additional keyword arguments for preprocessor creation.

    Returns:
        :obj:`dict`: Dictionary which describes a preprocessor.
    """
    return get_registry().describe(preprocessor_name, *args, **kwargs)


def list_objects() -> List[str]:
    """
    List available preprocessors


    Returns:
        Union[List[str], Dict[str, str]]: A list of preprocessors IDs if

    """
    return get_registry().list_objects()
