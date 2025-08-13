from pathlib import Path
from typing import Union

import tamm.utils.json as tamm_json
from tamm.model_repo.exceptions import UnrecognizedModelIdentifierError
from tamm.model_repo.model_repo import BaseModelRepo
from tamm.model_repo.utils import get_model_config_from_any_tamm_object


class FileModelRepo(BaseModelRepo):
    def _get_configs_impl(self):
        return {}

    def clear_cache(self):
        ...

    def is_alive(self) -> bool:
        return True

    def create_model_config(self, model_name: Union[str, Path], *args, **kwargs):
        if not isinstance(model_name, (str, Path)):
            raise UnrecognizedModelIdentifierError(
                f"model_name must be str, Path, not {type(model_name).__name__}"
            )
        if isinstance(model_name, str) and model_name.lower().startswith("file://"):
            core_model_name = model_name[len("file://") :]
            if not Path(core_model_name).is_file():
                raise FileNotFoundError(f"No such file: {model_name}")
            model_name = core_model_name

        if Path(model_name).is_file():
            config_path = Path(model_name)
        else:
            raise UnrecognizedModelIdentifierError(f"{self} cannot create {model_name}")

        with open(config_path, "r", encoding="utf-8") as fptr:
            maybe_model_config = tamm_json.load(fptr)

        model_config = get_model_config_from_any_tamm_object(maybe_model_config)
        model_config.update_configured_args(*args, **kwargs)
        return model_config
