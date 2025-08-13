import copy as _copy
from typing import Dict as _Dict
from typing import Optional as _Optional

from tamm.layers.transformer.layer_sequence import vanilla as _vanilla
from tamm.typing import ModuleOrBuilder as _ModuleOrBuilder
from tamm.typing import OptionalModuleOrBuilder as _OptionalModuleOrBuilder


class UniformTransformerLayerSequence(_vanilla.TransformerLayerSequence):
    """
    A generic sequence of transformer layers.  Unlike :class:`TransformerLayerSequence`,
    the architecture remains consistent across layers.

    Args:
        layer_template: A template layer or builder.  The sequence layer deep copies
            this template to initialize itself.
        num_layers (:obj:`int`): The number of layers in the sequence.
        input_transform (:obj:`.LayerBuilder`, optional): An optional auxiliary
            layer for the start of the sequence.  Defaults to ``None``.
        output_transform (:obj:`.LayerBuilder`, optional): An optional auxiliary
            layer for the end of the sequence.  Defaults to ``None``.
        output_hidden_states (:obj:`bool`): A flag for including outputs from each
            layer in the sequence output.  Defaults to ``False``.
        attention_types (:obj:`dict`, optional): A dictionary that
            maps layer indices to their secondary attention types.  For example
            if ``attention_types={3: "global", 7: "global"},
            then layers 3 and 7 receive the arguments
            ``attention_side_inputs=secondary_attention_side_inputs["global"]``
            rather than ``attention_side_inputs=attention_side_inputs``.
    """

    def __init__(
        self,
        layer_template: _ModuleOrBuilder,
        *,
        num_layers: int = 1,
        input_transform: _OptionalModuleOrBuilder = None,
        output_transform: _OptionalModuleOrBuilder = None,
        output_hidden_states: bool = False,
        attention_types: _Optional[_Dict[int, str]] = None,
    ):
        sequence = [_copy.deepcopy(layer_template) for _ in range(num_layers)]
        for layer in sequence:
            try:
                layer.reset_parameters()
            except AttributeError:
                pass
        super().__init__(
            *sequence,
            input_transform=input_transform,
            output_transform=output_transform,
            output_hidden_states=output_hidden_states,
            attention_types=attention_types,
        )
