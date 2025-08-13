import functools as _functools
import importlib as _importlib
import logging as _logging
from typing import Any as _Any

from tamm import _warnings

_logger = _logging.getLogger(__name__)


class BackwardCompatibilityImporter:
    def __init__(self):
        self._registered_imports = []

    def register_backward_compatibility_import(
        self, target_module_name: str, object_name: str, source_import_path: str
    ) -> None:
        self._registered_imports.append(
            (target_module_name, object_name, source_import_path)
        )

    def execute_imports(self) -> None:
        for import_spec in self._registered_imports:
            target_module_name, object_name, source_import_path = import_spec
            try:
                obj = self._import_module_or_object(source_import_path)
            except Exception as e:
                _logger.debug(
                    "Caught exception during backward compatibility import for "
                    f"{target_module_name}.{object_name}: {e}"
                )
                continue

            if callable(obj):
                obj = _warnings.deprecate(alternative=source_import_path)(obj)

            target_module = _importlib.import_module(target_module_name)
            setattr(target_module, object_name, obj)

        del self._registered_imports[:]

    @staticmethod
    def _import_module_or_object(import_path: str) -> _Any:
        try:
            return _importlib.import_module(import_path)
        except ModuleNotFoundError:
            pass
        module_name, attribute_name = import_path.rsplit(".", 1)
        module = _importlib.import_module(module_name)
        return getattr(module, attribute_name)


@_functools.lru_cache
def get_backward_compatibility_importer() -> BackwardCompatibilityImporter:
    return BackwardCompatibilityImporter()


def register_backward_compatibility_import(
    target_module_name: str, object_name: str, source_import_path: str
) -> None:
    importer = get_backward_compatibility_importer()
    importer.register_backward_compatibility_import(
        target_module_name=target_module_name,
        object_name=object_name,
        source_import_path=source_import_path,
    )


def execute_backward_compatibility_imports() -> None:
    importer = get_backward_compatibility_importer()
    importer.execute_imports()
