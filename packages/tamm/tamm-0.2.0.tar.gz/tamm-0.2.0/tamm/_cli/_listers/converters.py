from tamm._cli._listers._base import BaseLister
from tamm._cli._listers._helpers import (
    PrettyPrintListedEntities as _PrettyPrintListedEntities,
)
from tamm.converters import list_converters


class ConverterLister(BaseLister):
    name = "converters"

    # pylint: disable=redefined-builtin
    def __init__(self, all, long, wide, show_deprecated):
        super().__init__(all=all, long=long, wide=wide, show_deprecated=show_deprecated)
        self._listing_function = list_converters

    def print(self):
        _PrettyPrintListedEntities(self._listing_function).print(
            include_descriptions=self.long,
            filter_deprecated=not self.all,
            wide=self.wide,
        )
