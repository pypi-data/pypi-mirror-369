import warnings as _warnings

_TAMM_CONFIG_TYPE_TO_HF_MODEL_TYPE = {}


def _register_hf_model_type(*, tamm_config_type):
    """
    Associates a HF model type with a tamm config type so that we can create the HF
    model from the tamm config.
    """

    def decorator(hf_cls):
        if tamm_config_type in _TAMM_CONFIG_TYPE_TO_HF_MODEL_TYPE:
            _warnings.warn(f"Overwriting HF model type for {tamm_config_type}")

        _TAMM_CONFIG_TYPE_TO_HF_MODEL_TYPE[tamm_config_type] = hf_cls
        return hf_cls

    return decorator


def _get_hf_model_type(tamm_config_type):
    return _TAMM_CONFIG_TYPE_TO_HF_MODEL_TYPE.get(tamm_config_type)
