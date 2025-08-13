import abc
import copy
import logging
from itertools import chain
from typing import Any, List, Sequence, Union

from tamm.tokenizers.common import Tokenizer, TokenizerConfig

logger = logging.getLogger(__name__)


def validate_tokenizer_identifier(identifier: Any):
    if identifier is None or identifier == "":
        raise ValueError(
            f"TokenizerRegistry().create_config() requires an identifier, got {identifier}"
        )
    if isinstance(identifier, (int, float, bool)):
        raise ValueError(f"Tokenizer identifier cannot be {type(identifier).__name__}")


class TokenizerRegistry(abc.ABC):
    def __init__(self, *args, **kwargs):
        del args, kwargs

    def create_config(
        self, identifier: Union[str, "TokenizerConfig"], *args, **kwargs
    ) -> "TokenizerConfig":
        """
        Creates a Tokenizer referred by ``identifier``

        Args:
            identifier: :class:`TokenizerConfig` or the name of the Tokenizer
            **kwargs: Extra keyword arguments

        Returns:
            Tokenizer config instance
        """
        validate_tokenizer_identifier(identifier)
        if isinstance(identifier, TokenizerConfig):
            tokenizer = identifier
        else:
            if not isinstance(identifier, str):
                raise ValueError(
                    f"Expected a string tokenizer identifier, got '{type(identifier).__name__}'"
                )
            tokenizer = self._create_config(identifier, *args, **kwargs)
        # always use a shallow copy so that instances do not share configurable attributes
        tokenizer = copy.copy(tokenizer)
        for k, v in kwargs.items():
            setattr(tokenizer, k, v)
        return tokenizer

    def create(
        self, identifier: Union[str, "Tokenizer"], *args, **kwargs
    ) -> "Tokenizer":
        """
        Creates a Tokenizer referred by ``identifier``

        Args:
            identifier: :class:`Tokenizer` or the name of the Tokenizer
            **kwargs: Extra keyword arguments

        Returns: Tokenizer instance
        """
        validate_tokenizer_identifier(identifier)

        if isinstance(identifier, Tokenizer):
            return identifier

        tokenizer_config = self.create_config(identifier, *args, **kwargs)
        return tokenizer_config.create_tokenizer(**kwargs)

    def clear_cache(self):
        """
        Clears any local cache if setup by the concrete registry
        """

    @abc.abstractmethod
    def _create_config(
        self, identifier: Union[str, "Tokenizer"], *args, **kwargs
    ) -> "TokenizerConfig":
        """
        Abstract method for creating a Tokenizer.
        Shall be implemented by concrete class.
        """

    @abc.abstractmethod
    def list_(self, *args, **kwargs) -> List[str]:
        """
        Returns a list of Tokenizers available

        Args:
            *args: Extra positional arguments
            **kwargs: Extra keyword arguments

        Returns:
             list of Tokenizer names
        """

    @abc.abstractmethod
    def describe(self, identifier: str, *args, **kwargs) -> str:
        """
        Describe a tokenizer

        Args:
            identifier: name of the tokenizer
            *args: Extra positional arguments
            **kwargs: Extra keyword arguments

        Returns:
             Description of the tokenizer
        """

    def __add__(self, other: "TokenizerRegistry") -> "TokenizerRegistry":
        """
        Combines two TokenizerRegistryBase instances into a composite registry.

        The Tokenizers defined in `self` take precedence over those in `other`
        for the same `model_id`.

        Args:
            other (:obj: `TokenizerRegistryBaseBase`): Another Tokenizer registry to combine.

        Returns:
            :obj: `TokenizerRegistryBaseBase`: A composite registry combining `self` and `other`.
        """
        return ComposedTokenizerRegistry(self, other)

    def __iadd__(self, other: "TokenizerRegistry") -> "TokenizerRegistry":
        """
        In place version if __add__

        Args:
            other (:obj: `TokenizerRegistryBase`): Another Tokenizer registry to combine.

        Returns:
            :obj: `TokenizerRegistryBase`: A composite registry combining `self` and `other`.
        """
        return ComposedTokenizerRegistry(self, other)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(...)"


class ComposedTokenizerRegistry(TokenizerRegistry):
    """
    Represents a composite registry combining multiple TokenizerRegistryBase instances.
    """

    def __init__(self, *tokenizer_registries: "TokenizerRegistry"):
        super().__init__()
        self._registries: Sequence["TokenizerRegistry"] = tokenizer_registries

    def clear_cache(self) -> None:
        for registry in self._registries:
            registry.clear_cache()

    def _create_config(
        self, identifier: Union[str, "TokenizerConfig"], *args, **kwargs
    ) -> "TokenizerConfig":
        for registry in self._registries:
            try:
                return registry.create_config(identifier, *args, **kwargs)
            except Exception as e:
                logger.debug("Cannot create %s with %s: %s", identifier, registry, e)
        raise KeyError(
            f"{identifier} is not found in all available tokenizer registries: {self._registries}"
        )

    def list_(self, *args, **kwargs) -> List[str]:
        iterators = [registry.list_(*args, **kwargs) for registry in self._registries]
        return list(chain(*iterators))

    def describe(self, identifier: str, *args, **kwargs) -> str:
        for registry in self._registries:
            try:
                return registry.describe(identifier, *args, **kwargs)
            except Exception as e:
                logger.debug("%ss cannot describe %s: %s", registry, identifier, e)
        raise KeyError(
            f"{identifier} cannot be described by any tokenizer registry: {self._registries}"
        )

    def __repr__(self):
        composed = ", ".join([str(registry) for registry in self._registries])
        return f"{self.__class__.__name__}({composed})"
