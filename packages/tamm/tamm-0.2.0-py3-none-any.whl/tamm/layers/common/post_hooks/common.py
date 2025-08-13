from typing import Callable

from torch import nn as _nn


class CompositePostHook:
    def __init__(self, *hooks: "Callable"):
        self.hooks = hooks

    def __call__(self, model: "_nn.Module") -> "_nn.Module":
        for hook in self.hooks:
            model = hook(model)
        return model


class IdentityPostHook:
    def __call__(self, x):
        return x
