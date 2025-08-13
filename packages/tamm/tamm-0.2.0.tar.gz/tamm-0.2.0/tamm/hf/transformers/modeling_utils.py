from transformers import modeling_utils as _transformers_modeling_utils

from tamm import layers as _layers


class PreTrainedModel(_transformers_modeling_utils.PreTrainedModel):
    """
    Subclass of :class:`PreTrainedModel` from :mod:`transformers` for implementing bug
    fixes or additional functionality related to |tamm|.
    """

    # pylint: disable=abstract-method

    @property
    def _tied_weights_keys(self):
        tied_module_names = [
            name
            for name, module in self.named_modules()
            if isinstance(module, _layers.TiedWeightLinear)
        ]
        return [f"{name}.weight" for name in tied_module_names]
