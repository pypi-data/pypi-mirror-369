import tamm.utils.json as _tamm_json
from tamm.model_repo.exceptions import UnrecognizedModelIdentifierError
from tamm.model_repo.model_repo import BaseModelRepo
from tamm.model_repo.utils import get_model_config_from_any_tamm_object
from tamm.utils.uri import _URIHandler


class URIHandlerModelRepo(BaseModelRepo):
    def _get_configs_impl(self):
        return {}

    def clear_cache(self):
        ...

    def is_alive(self) -> bool:
        return True

    def create_model_config(self, model_name: str, *args, **kwargs):
        """
        Use _URIHandler to load model configs from any supported URI

        Args:
            model_name: URI like s3://bucket/tamm-config.json
            *args: model config arguments
            **kwargs: model config keyword arguments

        Returns: ModelConfig subclass instance

        """
        if not isinstance(model_name, str):
            raise UnrecognizedModelIdentifierError(
                f"model_name must be a string, got {type(model_name)}"
            )
        try:
            with _URIHandler().open(model_name, mode="r") as f:
                maybe_model_config = _tamm_json.load(f)
        except FileNotFoundError as e:
            # cfassetlib raises FileNotFoundError
            raise FileNotFoundError(f"No such file: {model_name}") from e
        except Exception as e:
            raise UnrecognizedModelIdentifierError(
                f"{self} cannot create {model_name}"
            ) from e

        model_config = get_model_config_from_any_tamm_object(maybe_model_config)
        model_config.update_configured_args(*args, **kwargs)
        return model_config
