from tamm import _warnings as _tamm_warnings
from tamm.model_repo.publishing import PublishedModelConfig as _PublishedModelConfig


def _warn_deprecated_published_config(config: "_PublishedModelConfig"):
    if config.is_deprecated:
        msg = f"'{config.model_id}' model is deprecated."
        replacement_model_id = config.replacement_model_id
        if replacement_model_id:
            msg = msg + f" Please use '{replacement_model_id}' model instead."
        _tamm_warnings.deprecation(msg)
