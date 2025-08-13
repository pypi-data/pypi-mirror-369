"""
utils.timer
===========

This submodule implements a :class:`.Timer` for timing PyTorch computation.

.. autoclass:: tamm.utils.timer.Timer
    :members:
"""

import collections as _collections
import contextlib as _contextlib
import functools as _functools
import logging as _logging
import time as _time
from typing import Any as _Any
from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union
from typing import cast as _cast

import torch as _torch
import wrapt as _wrapt

_logger = _logging.getLogger(__name__)


class Timer:
    """
    A class for measuring the time of PyTorch computation on CUDA, MPS, and CPU devices.
    It may add overhead.  It can also be imprecise, especially if measuring small timespans.

    The timer accounts for asynchronous execution using timing events (e.g., :obj:`torch.cuda.Event`).

    Args:
        device (:obj:`torch.device` or :obj:`str`): The device (or device type) for the
            computation (``"cuda"``, ``"mps"``, ``"cpu"``, etc.).
    """

    def __init__(self, device: _Union[str, _torch.device]):
        self._device_type = _torch.device(device).type
        self._is_enabled = True
        self.reset()

    @property
    def device_type(self) -> str:
        """The device type (a :obj:`str`)."""
        return self._device_type

    @property
    def is_enabled(self) -> bool:
        """Whether the timer is currently enabled."""
        return self._is_enabled

    def reset(self):
        """
        Resets the timer to its initial state, clearing all measurements and enabling the timer.
        """
        self._start_events = _collections.defaultdict(dict)
        self._end_events = _collections.defaultdict(dict)
        self._recorded_times = _collections.defaultdict(list)
        self.enable()

    @_contextlib.contextmanager
    def time_block(self, tag: str):
        """
        Yields a context manager for timing a code block.

        Args:
            tag (:obj:`str`): A string identifier for the measurement.
        """
        is_enabled = self.is_enabled
        start_event_id = None

        if is_enabled:
            start_event_id = self._record_start_event(tag)

        try:
            yield

        finally:
            if is_enabled:
                start_event_id = _cast(int, start_event_id)
                self._record_end_event(start_event_id, tag=tag)

    def _record_start_event(self, tag: str) -> int:
        """
        Creates a new timing event and appends it to _start_events.  Every start event
        must have a corresponding end event.
        """
        event = self._create_timing_event()
        event_id = len(self._start_events[tag])
        self._start_events[tag][event_id] = event
        return event_id

    def _record_end_event(self, start_event_id: int, *, tag: str) -> None:
        """Creates a new timing event and appends it to _end_events."""
        event = self._create_timing_event()
        self._end_events[tag][start_event_id] = event

    def _create_timing_event(self):
        if self.device_type == "cuda":
            event = _torch.cuda.Event(enable_timing=True)
        elif self.device_type == "mps":
            event = _torch.mps.Event(enable_timing=True)
        elif self.device_type in ("cpu", "meta"):
            event = _CPUEvent()
        else:
            raise RuntimeError(
                f"Timer does not support device type '{self.device_type}'"
            )
        event.record()
        return event

    def enable(self) -> None:
        """
        Enables the timer, reversing the effect of :meth:`disable`.  The timer is enabled
        by default upon initialization.
        """
        self._is_enabled = True

    def disable(self) -> None:
        """
        Disables the timer.  When disabled, the timer no longer makes measurements.
        """
        self._is_enabled = False

    def register_forward_hooks(
        self, module: _torch.nn.Module, *, tag: _Optional[str] = None
    ) -> None:
        """
        Attaches hooks to a PyTorch :obj:`nn.Module` to time its forward computation.

        Args:
            module (:obj:`torch.nn.Module`): The module to time.
            tag (:obj:`str`, optional): An optional string identifier for the module.
                If ``None``, this defaults to the class name of ``module``.

        Example:

            Time all layers in a model, grouped by layer type:

            .. code-block:: python

                with torch.device("cuda"):
                    inputs = torch.randn(8192, 1024)
                    model = torch.nn.Sequential(
                        *[torch.nn.Linear(1024, 1024) for _ in range(5)]
                    )

                timer = Timer(inputs.device)
                for module in model.modules():
                    timer.register_forward_hooks(module)

                model(inputs)
                timer.log_total_times()  # Sequential: 5.4516 ms, Linear: 5.4403 ms

        Example:

            Time a subset of layers using a custom tag:

            .. code-block:: python

                with torch.device("cuda"):
                    inputs = torch.randn(8192, 1024)
                    model = torch.nn.Sequential(
                        *[torch.nn.Linear(1024, 1024) for _ in range(5)]
                    )

                timer = Timer(inputs.device)
                for idx in [0, 2, 4]:
                    timer.register_forward_hooks(model[idx], tag="evens")

                model(inputs)
                timer.log_total_times()  # evens: 3.2092 ms
        """
        self._register_torch_module_hooks(
            module, tag=tag, forward_hooks=True, backward_hooks=False
        )

    def register_backward_hooks(
        self, module: _torch.nn.Module, *, tag: _Optional[str] = None
    ) -> None:
        """
        Attaches hooks to a PyTorch :obj:`nn.Module` to time its backward computation.

        .. caution::
            This method is recommended only for layers with inputs that require gradients,
            since it uses :meth:`module.register_full_backward_hook` to record the end of
            backward.  When inputs do not require gradients, this hook may fire before the
            full backward pass completes.

        Args:
            module (:obj:`torch.nn.Module`): The module to time.
            tag (:obj:`str`, optional): An optional string identifier for the module.
                If ``None``, this defaults to the class name of ``module``.
        """
        self._register_torch_module_hooks(
            module, tag=tag, forward_hooks=False, backward_hooks=True
        )

    def register_forward_backward_hooks(
        self, module: _torch.nn.Module, *, tag: _Optional[str] = None
    ) -> None:
        """
        Attaches hooks to a PyTorch :obj:`nn.Module` to time its forward and backward
        computation.

        .. caution::
            This method is recommended only for layers with inputs that require gradients,
            since it uses :meth:`module.register_full_backward_hook` to record the end of
            backward.  When inputs do not require gradients, this hook may fire before the
            full backward pass completes.

        Args:
            module (:obj:`torch.nn.Module`): The module to time.
            tag (:obj:`str`, optional): An optional string identifier for the module.
                If ``None``, this defaults to the class name of ``module``.
        """
        self._register_torch_module_hooks(
            module, tag=tag, forward_hooks=True, backward_hooks=True
        )

    def _register_torch_module_hooks(
        self,
        module: _torch.nn.Module,
        *,
        tag: _Optional[str] = None,
        forward_hooks: bool = True,
        backward_hooks: bool = True,
    ) -> None:
        if tag is None:
            tag = module.__class__.__name__

        if forward_hooks:
            helper = _TorchModuleTimingHelper(timer=self, tag=tag)
            module.register_forward_pre_hook(helper.pre_hook)
            module.register_forward_hook(helper.post_hook)

        if backward_hooks:
            helper = _TorchModuleTimingHelper(timer=self, tag=tag)
            module.register_full_backward_pre_hook(helper.pre_hook)
            module.register_full_backward_hook(helper.post_hook)

    def wrap_function(
        self, fn: _Optional[_Callable[..., _Any]] = None, *, tag: _Optional[str] = None
    ) -> _Callable[..., _Any]:
        """
        Wraps a function to time it when called.

        Args:
            fn (:obj:`callable`): The function to time.
            tag (:obj:`str`, optional): An optional string identifier for the function.
                If ``None``, this defaults to the name of the function.

        Returns:
            The wrapped function.

        Example:

            .. code-block:: python

                timer = Timer("cpu")

                @timer.wrap_function
                def sleep50():
                    time.sleep(50 / 1000)

                @timer.wrap_function(tag="s75")
                def sleep75():
                    time.sleep(75 / 1000)

                sleep50()
                sleep75()
                timer.log_total_times()  # sleep50: 51.6090 ms, s75: 76.9340 ms
        """

        if fn is None:
            return _functools.partial(self.wrap_function, tag=tag)

        if tag is None:
            tag = getattr(fn, "__name__", "Unnamed callable")

        @_wrapt.decorator
        def wrapper(wrapped, _instance, args, kwargs):
            with self.time_block(tag=tag):
                return wrapped(*args, **kwargs)

        return wrapper(fn)

    def get_times(self) -> _Dict[str, _List[float]]:
        """
        Returns a dictionary that maps each tag to a list of times (in milliseconds) measured for the tag.
        """
        self._flush_events()
        return self._recorded_times

    def get_total_times(self) -> _Dict[str, float]:
        """
        Returns a dictionary that maps each tag to the sum of times (in ms) measured for the tag.
        """
        all_times = self.get_times()
        return {tag: sum(times) for tag, times in all_times.items()}

    def log_total_times(self, *, level: int = _logging.INFO) -> None:
        """Logs the total time (in ms) measured for each tag."""
        times = self.get_total_times()
        if len(times) == 0:
            message = "No recorded times"
        else:
            message_parts = ["Total times:"]
            message_parts += [f"- {key}: {time:.4f} ms" for key, time in times.items()]
            message = "\n".join(message_parts)
        _logger.log(level, message)

    def _flush_events(self):
        """
        Flush the recorded events and update self._recorded_times with the elapsed time
        for each event.
        """
        self._synchronize_device()
        tags = list(self._start_events.keys())
        for tag in tags:
            start_events = self._start_events.pop(tag)
            end_events = self._end_events.pop(tag)
            if len(start_events) != len(end_events):
                raise RuntimeError(
                    f"Tag {tag} has {len(start_events)} start events but {len(end_events)} end events."
                )
            for start_event_id, start_event in start_events.items():
                end_event = end_events[start_event_id]
                try:
                    recorded_time = start_event.elapsed_time(end_event)
                except RuntimeError as e:
                    if "was not recorded after start event" not in str(e):
                        raise
                    recorded_time = 0.0
                self._recorded_times[tag].append(recorded_time)

    def _synchronize_device(self):
        if self.device_type == "cuda":
            _torch.cuda.synchronize()
        elif self.device_type == "mps":
            _torch.mps.synchronize()


class _TorchModuleTimingHelper:
    def __init__(self, *, timer: Timer, tag: str):
        self.timer = timer
        self.tag = tag
        self._start_event_id: _Union[int, None] = None

    def record_start_event(self):
        if self._start_event_id is not None:
            raise RuntimeError(
                "record_start_event called multiple times before record_end_event"
            )
        # pylint: disable-next=protected-access
        self._start_event_id = self.timer._record_start_event(self.tag)

    def pre_hook(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.record_start_event()

    def record_end_event(self):
        if self._start_event_id is None:
            raise RuntimeError("record_end_event called before record_start_event")
        # pylint: disable-next=protected-access
        self.timer._record_end_event(self._start_event_id, tag=self.tag)
        self._start_event_id = None

    def post_hook(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.record_end_event()


class _CPUEvent:
    """A class analogous to :class:`torch.cuda.Event` but for CPU."""

    def __init__(self):
        self._recorded_time = None

    def record(self) -> None:
        """Records the current time."""
        self._recorded_time = _time.perf_counter_ns() / 1e6

    def elapsed_time(self, end_event: "_CPUEvent") -> float:
        """
        Returns the time elapsed in milliseconds after the event was recorded and before
        the end_event was recorded.
        """
        # pylint: disable=protected-access
        if self._recorded_time is None:
            raise RuntimeError("The start event has not been recorded.")
        if end_event._recorded_time is None:
            raise RuntimeError("The end event has not been recorded.")
        return max(end_event._recorded_time - self._recorded_time, 0)
