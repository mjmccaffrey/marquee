"""Marquee Lighted Sign Project - sequencemode"""

from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
import itertools
from typing import Any, Iterable

from lightset_misc import ALL_ON
from .performancemode import PerformanceMode
from specialparams import ActionParams, ChannelParams

@dataclass(kw_only=True)
class SequenceMode(PerformanceMode):
    """Executes all sequence-based modes."""
    sequence: Callable[[], Iterable]
    pre_delay: float = 0.0
    delay: tuple[float, ...] | float | None = None
    stop: int | None = None
    repeat: bool = True
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()
        if isinstance(self.special, ChannelParams):
            self.lights.set_relays(ALL_ON)
            self.lights.set_channels(brightness=0, on=True, force=True)
        else:
            self.lights.set_channels(brightness=100, on=True, force=True)

    def execute(self, pre_delay_done=False) -> None:
        """Execute sequence with delay seconds between steps.
           If stop is specified, end the sequence 
           just before the nth pattern."""
        if self.pre_delay and not pre_delay_done:
            self.schedule(
                action = partial(self.execute, pre_delay_done=True),
                due_rel = self.pre_delay,
                name = "SequenceMode execute after pre_delay",
            )
            return
        # self.player.replace_kwarg_values(self.kwargs)
        delay_iter = (
            itertools.cycle(self.delay) 
                if isinstance(self.delay, Iterable) else
            itertools.repeat(self.delay)
        )
        for i, lights in enumerate(self.sequence(**self.kwargs)):
            if self.stop is not None and i == self.stop:
                break
            delay = next(delay_iter)

            if isinstance(self.special, ActionParams):
                action = partial(
                        self.special.action,
                        lights,
                )
            else:
                action = partial(
                    self.lights.set_relays,
                    lights, 
                    special=self.special,
                )
            self.schedule(
                action = action,
                due_rel = 0 if delay is None else i * delay,
                name = f"SequenceMode execute {i} {lights}",
            )
            if delay is None:
                print("Exiting sequencemode.play, delay is None")
                return
        if self.repeat: 
            self.schedule(
                action = self.execute,
                due_rel = (i + 1) * delay,
                name = "SequenceMode continue",
            )

