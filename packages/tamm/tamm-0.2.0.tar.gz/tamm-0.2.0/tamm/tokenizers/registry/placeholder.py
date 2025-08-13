from typing import List, Union

from tamm.tokenizers.common import Tokenizer, TokenizerConfig
from tamm.tokenizers.registry import TokenizerRegistry


class PlaceholderTokenizerRegistry(TokenizerRegistry):
    def _create_config(
        self, identifier: Union[str, "Tokenizer"], *args, **kwargs
    ) -> "TokenizerConfig":
        raise KeyError(f"{identifier} is not found.")

    def list_(self, *args, **kwargs) -> List[str]:
        return []

    def describe(self, identifier: str, *args, **kwargs) -> str:
        raise KeyError(f"{identifier} is not found, cannot describe.")

    def __iadd__(self, other):
        return other

    def __add__(self, other):
        return other
