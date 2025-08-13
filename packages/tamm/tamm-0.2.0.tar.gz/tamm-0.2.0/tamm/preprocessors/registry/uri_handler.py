import json
from typing import Any, Dict, List

import tamm.utils.json as _tamm_json
from tamm.preprocessors.base import Preprocessor
from tamm.preprocessors.registry import PreprocessorRegistry
from tamm.utils.uri.uri_handler import _URIHandler, is_uri_or_posix


class URIHandlerPreprocessorRegistry(PreprocessorRegistry):
    def _create(self, identifier: str, *args, **kwargs) -> "Preprocessor":
        if not is_uri_or_posix(identifier):
            raise KeyError(
                f"{identifier} is neither a URL nor posix path, {self} cannot handle this"
            )

        with _URIHandler().open(identifier) as f:
            return _tamm_json.load(f)

    def list_objects(self, *args, **kwargs) -> List[str]:
        return []

    def describe(self, identifier: str, *args, **kwargs) -> Dict[str, Any]:
        if not is_uri_or_posix(identifier):
            raise KeyError(
                f"{identifier} is neither a URL nor posix path, {self} cannot handle this"
            )

        with _URIHandler().open(identifier) as f:
            return json.load(f)
