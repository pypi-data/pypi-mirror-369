import collections as _collections

import torch as _torch
from torch import nn as _nn


def _compile_friendly_get_parameter(module, parameter_name):
    """similar to module.get_parameter(parameter_name) but works with torch.compile"""
    module_or_param = module
    for name in parameter_name.split("."):
        module_or_param = getattr(module_or_param, name)
    return module_or_param


class TieableParamsDict:
    """
    A replacement of :class:`OrderedDict` for holding parameters in the ``_parameters``
    attribute of a :obj:`torch.nn.Module`.  This class implements special behavior for
    sharing parameters between modules to ensure that the parameters do not become
    untied.  It is also compatible with :func:`torch.compile` and FSDP.
    """

    def __init__(self, *args, **kwargs):
        self._params = _collections.OrderedDict(*args, **kwargs)
        self._tied_parameters = {}

    def register_tied_parameter(
        self, *, name: str, tied_module: _nn.Module, tied_param_name: str
    ):
        """
        Register a parameter from another module.

        Args:
            name (:obj:`str`): The name of the parameter to register.
            tied_module (:obj:`nn.Module`): The other module that owns the tied
                parameter to register.
            tied_param_name (:obj:`str`): The name of the parameter as it is
                registered on ``tied_module``.
        """
        self._tied_parameters[name] = (tied_module, tied_param_name)
        self._update_tied_params()

    def get_tied_value(self, key: str) -> _torch.Tensor:
        """
        A method for accessing the tied parameters.

        Args:
            key (:obj:`str`): The tied parameter name.

        Returns:
            The tied parameter.
        """
        if key in self._tied_parameters:
            module, name = self._tied_parameters[key]
            return _compile_friendly_get_parameter(module, name)
        return self._params[key]

    def _update_tied_params(self):
        for name, (tied_module, tied_param_name) in self._tied_parameters.items():
            value = _compile_friendly_get_parameter(tied_module, tied_param_name)
            if isinstance(value, _nn.Parameter):
                self._params[name] = value
            else:
                # As of torch 2.5, FSDP at times replaces each nn.Parameter with a
                # vanilla torch.Tensor, in which case, the tensor should not show
                # up in the parameters dict.
                self._params.pop(name, None)

    def __eq__(self, other):
        self._update_tied_params()
        return self._params.__eq__(other)

    def __ne__(self, other):
        self._update_tied_params()
        return self._params.__ne__(other)

    def __iter__(self):
        self._update_tied_params()
        return self._params.__iter__()

    def __reversed__(self):
        self._update_tied_params()
        return self._params.__reversed__()

    def __getitem__(self, key):
        if key in self._tied_parameters:
            self._update_tied_params()
        return self._params.__getitem__(key)

    def __setitem__(self, key, value):
        if key in self._tied_parameters:
            return
        self._params.__setitem__(key, value)

    def __delitem__(self, key):
        if key in self._tied_parameters:
            return
        self._params.__delitem__(key)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        params = {key: value for key in iterable}
        return cls(params)

    def setdefault(self, /, key, default=None):
        if key in self._tied_parameters:
            self._update_tied_params()
            return self[key]
        return self._params.setdefault(key, default=default)

    def pop(self, *args):
        key = args[0]
        if key in self._tied_parameters:
            self._update_tied_params()
            return self[key]
        return self._params.pop(*args)

    def popitem(self, last=True):
        self._update_tied_params()
        key, value = self._params.popitem(last=last)
        if key in self._tied_parameters:
            self._update_tied_params()
        return key, value

    def keys(self):
        self._update_tied_params()
        return self._params.keys()

    def values(self):
        self._update_tied_params()
        return self._params.values()

    def items(self):
        self._update_tied_params()
        return self._params.items()

    def clear(self):
        self._params.clear()
        self._update_tied_params()

    def move_to_end(self, key, last=True):
        self._update_tied_params()
        self._params.move_to_end(key, last=last)
