from typing import Union as _Union

from tamm.layers.common.builder import LayerBuilder
from tamm.layers.common.config import ModuleConfig

LayerBuilderOrConfig = _Union[ModuleConfig, LayerBuilder]
