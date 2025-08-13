from tamm._cli._listers._base import BaseLister
from tamm._cli._listers._helpers import (
    PrettyPrintListedEntities as _PrettyPrintListedEntities,
)
from tamm.model_repo import get_model_repo_lazy


class ModelsLister(BaseLister):
    name = "models"

    # pylint: disable=redefined-builtin
    def __init__(self, all, long, wide, show_deprecated):
        super().__init__(all=all, long=long, wide=wide, show_deprecated=show_deprecated)
        kwargs = {"certified_tags": None} if self.all else {}
        self._model_repo = get_model_repo_lazy(**kwargs)
        self._listing_function = self._model_repo.list_models

    def print(self):
        _PrettyPrintListedEntities(self._listing_function).print(
            include_descriptions=self.long,
            filter_deprecated=not self.all,
            wide=self.wide,
        )


class AdaptedModelsLister(ModelsLister):
    name = "adapted-models"

    # pylint: disable=redefined-builtin
    def __init__(self, all, long, wide, show_deprecated):
        super().__init__(all=all, long=long, wide=wide, show_deprecated=show_deprecated)
        self._listing_function = self._model_repo.list_adapted_models
