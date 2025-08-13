import os as _os
from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

from tamm.utils.optional_bool import OptionalBool

ModuleBuilder = _Callable[[], _nn.Module]
ModuleOrBuilder = _Union[_nn.Module, ModuleBuilder]
OptionalModuleOrBuilder = _Optional[ModuleOrBuilder]

DtypeOrString = _Union[_torch.dtype, str]
DeviceOrString = _Union[_torch.device, str]
OptionalDtypeOrString = _Optional[DtypeOrString]
OptionalDeviceOrString = _Optional[DeviceOrString]
LenientOptionalBool = _Optional[_Union[bool, OptionalBool]]
PathLike = _Union[str, bytes, _os.PathLike]

OptionalTensor = _Optional[_torch.Tensor]

StateDictType = _Dict[str, _torch.Tensor]
