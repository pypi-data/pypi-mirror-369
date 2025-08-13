from typing import List, Union, cast

import tamm.utils.json as _tamm_json
from tamm.tokenizers.common import PublishedTokenizerConfig, Tokenizer, TokenizerConfig
from tamm.tokenizers.registry import TokenizerRegistry
from tamm.utils.uri.uri_handler import _URIHandler, is_uri_or_posix


class URIHandlerTokenizerRegistry(TokenizerRegistry):
    def _create_config(
        self, identifier: Union[str, "Tokenizer"], *args, **kwargs
    ) -> "TokenizerConfig":
        if not is_uri_or_posix(identifier):
            raise KeyError(
                f"{identifier} is neither a URL nor posix path, {self} cannot handle this"
            )

        with _URIHandler().open(identifier) as f:
            published_tokenizer_config = cast(
                PublishedTokenizerConfig, _tamm_json.load(f)
            )
        try:
            return published_tokenizer_config.tokenizer_config
        except AttributeError:
            return cast(TokenizerConfig, published_tokenizer_config)

    def list_(self, *args, **kwargs) -> List[str]:
        return []

    def describe(self, identifier: str, *args, **kwargs) -> str:
        if not is_uri_or_posix(identifier):
            raise KeyError(
                f"{identifier} is neither a URL nor posix path, {self} cannot handle this"
            )

        with _URIHandler().open(identifier) as f:
            published_tokenizer_config = _tamm_json.load(f)

        try:
            return published_tokenizer_config.description
        except AttributeError:
            return "<no_description>"
