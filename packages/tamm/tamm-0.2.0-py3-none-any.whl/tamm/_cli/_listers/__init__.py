import sys as _sys
from typing import Callable as _Callable
from typing import List as _List
from typing import Mapping as _Mapping

from tamm._cli._listers.converters import ConverterLister
from tamm._cli._listers.models import AdaptedModelsLister, ModelsLister
from tamm._cli._listers.preprocessors import PreprocessorLister
from tamm._cli._listers.tokenizers import TokenizerLister

__all__ = [
    "AdaptedModelsLister",
    "ConverterLister",
    "ModelsLister",
    "TokenizerLister",
    "PreprocessorLister",
]


def get_registered_listers() -> _Mapping[str, _Callable]:
    """
    Automatically discover all listers from the imported names of this module

    Returns:
        A dictionary maps lister name to :class:`tamm._cli._listers._base.BaseLister`
    """
    listers = [getattr(_sys.modules[__name__], lister) for lister in __all__]
    return {lister.name: lister for lister in listers}


def get_registered_listers_names() -> _List[str]:
    return sorted(list(get_registered_listers().keys()))
