import enum as _enum
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch
import torch.nn as _nn

from tamm import _helpers
from tamm._helpers import case_insensitive_lookup
from tamm.ao.layers import functional as _tamm_ao_F
from tamm.layers import functional as _tamm_F


class FakeQuantizeObserverMode(str, _enum.Enum):
    """An enum for controlling observer usage in :obj:`FakeQuantize` layers."""

    ENABLED = "enabled"
    """
    Call the observer to update quantization params during very forward pass, even when
    in eval mode.
    """

    DISABLED = "disabled"
    """Never call the observer so that quantization params remain frozen."""

    ONLY_TRAINING = "only_training"
    """
    Only call the observer when the :obj:`FakeQuantize` layer is in training mode.
    """

    @classmethod
    def _missing_(cls, value):
        return case_insensitive_lookup(cls, value)


class FakeQuantize(_nn.Module):
    """
    A layer for applying fake quantization (quantization immediately followed by
    dequantization) to simulate the impact of quantization.  This layer is suitable for
    quantization-aware training, since gradients pass through the fake quantization op
    (i.e., the backward pass ignores the quantization).

    Args:
        observer (:obj:`nn.Module`): An observer layer, such as
            :obj:`.SimpleEMAMinMaxObserver` or
            :obj:`torch.ao.quantization.MinMaxObserver`.
            This layer must have a :meth:`calculate_qparams` method as well as
            :attr:`quant_min` and :attr:`quant_max` attributes.  Its forward pass should
            optionally update statistics for :meth:`calculate_qparams`.
        enable_observer (:obj:`FakeQuantizeObserverMode`, :obj:`str`, or :obj:`bool`):
            Option that controls when to call the observer to update quantization
            params.  Defaults to ``"only_training"``.  A ``True`` value resolves to
            ``"enabled"`` mode, and ``False`` resolves to ``"disabled"``.  Note that
            in dynamic mode, the forward pass always calls the observer, regardless of
            whether it is enabled.
        enable_fake_quant (:obj:`bool`, optional): A flag that when ``False`` bypasses
            the fake quantization during :meth:`forward`.  Defaults to ``True``.  This
            flag does not affect the behavior of ``enable_observer``.
        dynamic (:obj:`bool`): If True, quantization parameters are reset every
            iteration.
        cast_dtype (:obj:`torch.dtype`, optional): An optional dtype for casting the
            input tensor and scale prior to fake quantization.  Defaults to ``None``.
        reciprocal_mul (:obj:`bool`, optional): A flag to multiply the features by
            the reciprocal of the quantization scales instead of dividing.
    """

    def __init__(
        self,
        observer: _nn.Module,
        enable_observer: _Union[str, FakeQuantizeObserverMode, bool] = "only_training",
        enable_fake_quant: bool = True,
        dynamic=False,
        cast_dtype=None,
        reciprocal_mul=False,
    ):
        super().__init__()

        self.activation_post_process = observer
        self.observer_mode = self._resolve_observer_mode(enable_observer)
        self.is_fake_quant_enabled = enable_fake_quant
        self.is_dynamic = dynamic
        self.cast_dtype = cast_dtype
        self.use_reciprocal_mul = reciprocal_mul

    @property
    def is_observer_enabled(self) -> bool:
        if self.observer_mode is FakeQuantizeObserverMode.ENABLED:
            return True
        if self.observer_mode is FakeQuantizeObserverMode.DISABLED:
            return False
        if self.observer_mode is FakeQuantizeObserverMode.ONLY_TRAINING:
            return self.training
        raise ValueError(f"Observer mode {self.observer_mode} not supported")

    @is_observer_enabled.setter
    def is_observer_enabled(
        self, value: _Union[str, FakeQuantizeObserverMode, bool]
    ) -> None:
        self.observer_mode = self._resolve_observer_mode(value)

    @staticmethod
    def _resolve_observer_mode(
        value: _Union[str, FakeQuantizeObserverMode, bool]
    ) -> FakeQuantizeObserverMode:
        if value is True:
            return FakeQuantizeObserverMode.ENABLED
        if value is False:
            return FakeQuantizeObserverMode.DISABLED
        return _helpers.get_enum_member_from_name(FakeQuantizeObserverMode, value)

    @property
    def ch_axis(self):
        return getattr(self.activation_post_process, "ch_axis", None)

    def forward(self, tensor):  # pylint: disable=invalid-name
        """
        Calls the ``observer`` layer with ``tensor`` if the observer is enabled.  Then
        returns a fake-quantized version of ``tensor`` if fake quantization is enabled
        and a ``tensor`` unmodified if not.
        """

        if self.is_dynamic:
            self.activation_post_process.reset_parameters()

        if self.is_dynamic or self.is_observer_enabled:
            self.activation_post_process(tensor.detach())

        if not self.is_fake_quant_enabled:
            return tensor

        scale, zero_point = self.activation_post_process.calculate_qparams()
        if self.ch_axis is not None:
            if len(self.ch_axis) > 1:
                new_shape = [
                    i for i in range(len(tensor.shape)) if i not in self.ch_axis
                ] + [i for i in range(len(tensor.shape)) if i in self.ch_axis]
                tensor = tensor.permute(new_shape)
            else:
                tensor = tensor.transpose(self.ch_axis[0], -1)

        out = _tamm_ao_F.fake_quantize(
            tensor,
            scale=scale,
            zero_point=zero_point,
            quant_min=self.activation_post_process.quant_min,
            quant_max=self.activation_post_process.quant_max,
            cast_dtype=self.cast_dtype,
            reciprocal_mul=self.use_reciprocal_mul,
        )
        if self.ch_axis is not None:
            if len(self.ch_axis) > 1:
                out = _tamm_F.inverse_permute(out, new_shape)
            else:
                out = out.transpose(self.ch_axis[0], -1)

        return out


class SimpleEMAMinMaxObserver(_nn.Module):
    """
    Computes the quantization scale parameter based on a moving average of the min
    and max values of recent inputs.

    Args:
        momentum (:obj:`float`, optional): The momentum parameter for the exponential
            moving average of min/max values across batches.  Defaults to ``0.9``.
        quant_min (:obj:`int`, optional): The smallest possible quantized integer value.
            Defaults to ``-128`` for symmetric ``int8`` quantization.
        quant_max (:obj:`int`, optional): The largest possible quantized integer value.
            Defaults to ``127`` for symmetric ``int8`` quantization.
        device (:obj:`torch.devce``, optional): The device for moving average
            parameters.
    """

    def __init__(
        self,
        momentum: float = 0.9,
        quant_min: int = -128,
        quant_max: int = 127,
        device: _Optional[_torch.device] = None,
    ):
        super().__init__()

        if momentum < 0 or momentum >= 1:
            raise ValueError(f"momentum ({momentum}) is not in [0, 1)")
        if quant_max <= 0:
            raise ValueError(f"quant_max ({quant_max}) is not greater than 0")
        if quant_min > 0:
            raise ValueError(f"quant_min ({quant_min}) is greater than 0")

        self.momentum = momentum
        self.quant_min, self.quant_max = quant_min, quant_max

        range_buffer = _torch.empty(2, dtype=_torch.float32, device=device)
        self.register_buffer("range", range_buffer)

        num_samples_buffer = _torch.empty((), dtype=_torch.int64, device=device)
        self.register_buffer("num_samples", num_samples_buffer)

        self.reset_parameters()

    def reset_parameters(self):
        self.range[0] = -1
        self.range[1] = 1
        self.num_samples.zero_()

    def forward(self, input):  # pylint: disable=redefined-builtin
        """
        Updates the moving average of min/max values and returns ``None``.
        """
        # Ensure parameters are in float32 without using self.to() which breaks torch.compile
        range_f32 = self.range.to(_torch.float32)

        min_max = _torch.stack([input.min(), input.max()]).to(_torch.float32)
        alpha = _torch.tensor(
            1 - self.momentum, dtype=_torch.float32, device=range_f32.device
        )
        one = _torch.ones_like(alpha)
        alpha = _torch.where(self.num_samples != 0, alpha, one)
        range_f32.add_(min_max - range_f32, alpha=alpha)
        self.num_samples.add_(input.size(0) if input.ndim > 0 else 1)

        # Copy back to original parameter
        self.range.copy_(range_f32)

    def calculate_qparams(self):
        """
        Returns ``0`` for the zero point and a scale based on the min/max moving
        average across past batches.  Specifically, the scale is maximum of
        ``min_avg / quant_min`` and ``max_avg / quant_max``.
        """

        if self.quant_min == 0:
            scale = self.range[1].float() * (1 / self.quant_max)
        else:
            denom = _torch.tensor(
                [1 / self.quant_min, 1 / self.quant_max], device=self.range.device
            )
            scale = _torch.max(self.range.float() * denom)
        zero_point = _torch.tensor([0], device=self.range.device)
        return scale, zero_point


class SimpleEMAPerChannelMinMaxObserver(_nn.Module):
    """
    Computes the channel-wise quantization scale parameter based on a moving average of
    the min and max values of recent inputs.

    Args:
        ch_axis (:obj:`int` or :obj:`list`): Axis or axes to keep quantization
            parameters independent.
        num_channels (:obj:`int` or :obj:`list`): Expected number of channels,
            corresponding to the axes in ch_axis.
        momentum (:obj:`float`, optional): The momentum parameter for the exponential
            moving average of min/max values across batches.  Defaults to ``0.9``.
        quant_min (:obj:`int`, optional): The smallest possible quantized integer value.
            Defaults to ``-128`` for symmetric ``int8`` quantization.
        quant_max (:obj:`int`, optional): The largest possible quantized integer value.
            Defaults to ``127`` for symmetric ``int8`` quantization.
        device (:obj:`torch.devce``, optional): The device for moving average
            parameters.
    """

    def __init__(
        self,
        ch_axis: _Union[int, list],
        num_channels: _Union[int, list],
        momentum: float = 0.9,
        quant_min: int = -128,
        quant_max: int = 127,
        device: _Optional[_torch.device] = None,
    ):
        super().__init__()

        if isinstance(ch_axis, list):
            assert len(ch_axis) == len(num_channels)
        else:
            assert isinstance(ch_axis, int) and isinstance(num_channels, int)
            ch_axis = [ch_axis]
            num_channels = [num_channels]

        if momentum < 0 or momentum >= 1:
            raise ValueError(f"momentum ({momentum}) is not in [0, 1)")
        if quant_max <= 0:
            raise ValueError(f"quant_max ({quant_max}) is not greater than 0")
        if quant_min > 0:
            raise ValueError(f"quant_min ({quant_min}) is greater than 0")

        self.momentum = momentum
        self.quant_min, self.quant_max = quant_min, quant_max

        range_shape = (*num_channels, 2)

        self.ch_axis = ch_axis
        self.num_channels = num_channels

        range_buffer = _torch.empty(range_shape, dtype=_torch.float32, device=device)
        self.register_buffer("range", range_buffer)

        num_samples_buffer = _torch.empty((), dtype=_torch.int64, device=device)
        self.register_buffer("num_samples", num_samples_buffer)

        self.reset_parameters()

    def reset_parameters(self):
        self.range[..., 0] = -1
        self.range[..., 1] = 1
        self.num_samples.zero_()

    def forward(self, input):  # pylint: disable=redefined-builtin
        """
        Updates the moving average of min/max values and returns ``None``.
        """
        # Ensure parameter is in float32 without using self.to() which breaks torch.compile
        range_f32 = self.range.to(_torch.float32)

        if len(self.ch_axis) > 1:
            new_shape = [i for i in range(len(input.shape)) if i in self.ch_axis] + [
                i for i in range(len(input.shape)) if i not in self.ch_axis
            ]
            flattened_input = input.permute(tuple(new_shape))
            flattened_input = flattened_input.flatten(start_dim=len(self.ch_axis))
            flattened_input = flattened_input.flatten(end_dim=len(self.ch_axis) - 1)
        else:
            flattened_input = input.transpose(0, self.ch_axis[0]).flatten(start_dim=1)

        min_max = _torch.stack(
            [flattened_input.min(dim=-1)[0], flattened_input.max(dim=-1)[0]], dim=1
        )
        min_max = min_max.to(_torch.float32).reshape(range_f32.shape)
        alpha = _torch.tensor(
            1 - self.momentum, dtype=_torch.float32, device=range_f32.device
        )
        one = _torch.ones_like(alpha)
        alpha = _torch.where(self.num_samples != 0, alpha, one)
        range_f32.add_(min_max - range_f32, alpha=alpha)
        self.num_samples.add_(input.size(0) if input.ndim > 0 else 1)

        self.range.copy_(range_f32)

    def calculate_qparams(self):
        """
        Returns ``0`` for the zero point and a scale based on the min/max moving
        average across past batches.  Specifically, the scale is maximum of
        ``min_avg / quant_min`` and ``max_avg / quant_max``.
        """

        # Ensure parameter is in float32 without using self.to() which breaks torch.compile
        range_f32 = self.range.to(_torch.float32)

        if self.quant_min == 0:
            scale = range_f32[..., 1] * (1 / self.quant_max)
        else:
            denom = _torch.tensor(
                [1 / self.quant_min, 1 / self.quant_max], device=self.range.device
            )
            scale = _torch.max(range_f32 * denom.unsqueeze(0), dim=-1)[0]
        zero_point = _torch.zeros(self.range.shape[:-1], device=self.range.device)
        return scale, zero_point

    def extra_repr(self) -> str:
        return f"ch_axis={self.ch_axis}, num_channels={self.num_channels}"
