from tamm import tokenizers
from tamm._cli._listers._base import BaseLister
from tamm._cli._listers._helpers import (
    PrettyPrintListedEntities as _PrettyPrintListedEntities,
)


class TokenizerLister(BaseLister):
    name = "tokenizers"

    def print(self):
        _PrettyPrintListedEntities(tokenizers.list_tokenizers).print(
            include_descriptions=self.long,
            filter_deprecated=not self.show_deprecated,
            wide=self.wide,
        )
