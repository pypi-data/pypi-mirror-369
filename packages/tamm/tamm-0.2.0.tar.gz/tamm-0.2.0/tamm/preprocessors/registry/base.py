import abc
import copy
import json
import logging
from itertools import chain
from typing import Any, List, Sequence, Union

import tamm.utils.json as tamm_json
from tamm.preprocessors.base import Preprocessor

logger = logging.getLogger(__name__)


class PreprocessorRegistry(abc.ABC):
    # pylint: disable-next=unused-argument
    def __init__(self, *args, **kwargs):
        del args, kwargs

    def create(self, identifier: Any, *args, **kwargs) -> "Preprocessor":
        """
        Creates a preprocessor referred by ``identifier``
        Args:
            identifier: :class:`Preprocessor` or the name of the preprocessor
            **kwargs: Extra keyword arguments
        Returns: Preprocessor instance
        """
        if isinstance(identifier, Preprocessor):
            preprocessor = identifier
        else:
            preprocessor = self._create(identifier, *args, **kwargs)
        # always use a shallow copy so that instances do not share configurable attributes
        preprocessor = copy.copy(preprocessor)
        for k, v in kwargs.items():
            setattr(preprocessor, k, v)
        return preprocessor

    def clear_cache(self):
        """
        Clears any local cache if setup by the concrete catalog
        """

    @abc.abstractmethod
    def _create(self, identifier: Any, *args, **kwargs) -> "Preprocessor":
        """
        Abstract method for creating a preprocessor.
        Shall be implemented by concrete class.
        """

    @abc.abstractmethod
    def list_objects(self, *args, **kwargs) -> List[str]:
        """
        Returns a list of preprocessors available
        *args: Extra positional arguments
        **kwargs: Extra keyword arguments
        Returns:
             list of preprocessor names
        """

    def describe(self, identifier: Any, *args, **kwargs) -> dict:
        """
        Describes a preprocessor referred by ``identifier``
        Args:
            identifier: :class:`Preprocessor` or the name of the preprocessor
            **kwargs: Extra keyword arguments
        Returns: Dictionary that describes preprocessor
        """
        preprocessor = identifier
        if isinstance(identifier, str):
            preprocessor = self._create(identifier, *args, **kwargs)
        return json.loads(tamm_json.dumps(preprocessor))

    def __add__(self, other: "PreprocessorRegistry") -> "PreprocessorRegistry":
        """
        Combines two PreprocessorCatalog instances into a composite catalog.

        The preprocessors defined in `self` take precedence over those in `other`
        for the same `model_id`.

        Args:
            other (:obj: `PreprocessorCatalog`): Another preprocessor catalog to combine.

        Returns:
            :obj: `PreprocessorCatalog`: A composite catalog combining `self` and `other`.
        """

        return ComposedPreprocessorRegistry(self, other)

    def __iadd__(self, other: "PreprocessorRegistry") -> "PreprocessorRegistry":
        """
        In-place version of __add__
        """
        return ComposedPreprocessorRegistry(self, other)


class ComposedPreprocessorRegistry(PreprocessorRegistry):
    """
    Represents a composite catalog combining two PreprocessorCatalog instances.
    """

    def __init__(self, *tokenizer_registries: "PreprocessorRegistry"):
        super().__init__()
        self._registries: Sequence["PreprocessorRegistry"] = tokenizer_registries

    def _create(
        self, identifier: Union[str, "Preprocessor"], *args, **kwargs
    ) -> "Preprocessor":
        """
        Creates a preprocessor by identifier.

        Args:
            identifier (:obj: `Union[str, Preprocessor]`): The identifier or preprocessor object.
            **kwargs: Additional keyword arguments for preprocessor creation.

        Returns:
            Preprocessor: The created preprocessor object.
        """
        for registry in self._registries:
            try:
                return registry.create(identifier, *args, **kwargs)
            except Exception as e:
                logger.debug("Cannot create %s with %s: %s", identifier, registry, e)
        raise KeyError(
            f"{identifier} is not found in all available preprocessor registries."
        )

    def list_objects(self, *args, **kwargs) -> List[str]:
        """
        Lists all preprocessor identifiers from both catalogs.

        Args:
            *args: Positional arguments (unused).
            **kwargs: Keyword arguments (unused).

        Returns:
            `List[str]`: A combined list of preprocessor identifiers.
        """
        iterators = [
            registry.list_objects(*args, **kwargs) for registry in self._registries
        ]
        return list(chain(*iterators))

    def clear_cache(self):
        for registry in self._registries:
            registry.clear_cache()
