"""
This module dynamically aggregates model config classes so that we can document them
with Sphinx autodoc.  We do not recommend using this module to access the config
classes (use ``model_cls.Config`` instead).
"""

from tamm import models as _models


def _attach_model_configs_to_module():
    model_objects = (getattr(_models, obj_name) for obj_name in dir(_models))
    config_classes = (
        getattr(model_cls, "Config")
        for model_cls in model_objects
        if hasattr(model_cls, "Config")
    )
    for cls in config_classes:
        globals()[cls.__name__] = cls


_attach_model_configs_to_module()
