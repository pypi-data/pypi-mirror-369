import copy as _copy

from torch import nn as _nn


class AttachConfigPostHook:
    def __init__(self, config):
        self.config = config

    def __call__(self, model: _nn.Module) -> None:
        if not self._should_attach_config(model):
            return
        model.config = _copy.deepcopy(self.config)

    @staticmethod
    def _should_attach_config(model: _nn.Module) -> bool:
        # pylint: disable=import-outside-toplevel
        from tamm.layers.sequential import Sequential
        from tamm.models.common import ModelMixin

        return isinstance(model, (ModelMixin, Sequential))
