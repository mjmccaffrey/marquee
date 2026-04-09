"""Marquee Lighted Sign Project - sequencemode"""

from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from functools import partial
import itertools
import logging
from typing import Any, Iterable

from devices.color import Color, Colors
from devices.specialparams import ActionParams, EmulateParams
from .performancemode import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass
class LightSetBaseline:
    """"""
    relay: bool | None = None
    brightness: int | None = None
    color: Color | None = None
    on: bool | None = None
    transition: float | None = None

DEFAULT_BASELINE = LightSetBaseline(
    relay=False,
    brightness=100,
    color=Colors.WHITE,
    on=True,
    transition=0.0,
)


@dataclass(kw_only=True)
class SequenceMode(PerformanceMode):
    """Executes all sequence-based modes."""
    sequence: Callable[[], Iterable]
    pre_delay: float = 0.0
    delay: tuple[float, ...] | float | None = None
    stop: int | None = None
    repeat: bool = True
    baseline: LightSetBaseline | None = DEFAULT_BASELINE
    sequence_kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize."""
        self.sequence_kwargs = self.replace_kwarg_values(self.sequence_kwargs)
        if self.lights.smart_bulbs and self.special is None:
            log.info("SequenceMode: emulating incandescent.")
            self.special = EmulateParams()
        if self.baseline is not None:
            params = asdict(self.baseline)
            self.lights.set_relays(params.pop('relay'))
            self.lights.set_channels(**params)
            # self.lights.set_channels(
            #     brightness=bl.brightness,
            #     color=bl.color,
            #     on=bl.on,
            #     transition=bl.transition,
            # )

    def execute(self) -> None:
        """Execute sequence with delay seconds between steps.
           If stop is specified, end the sequence 
           just before the nth pattern."""
        # self.player.replace_kwarg_values(self.kwargs)
        delay_iter = (
            itertools.cycle(self.delay) 
                if isinstance(self.delay, Iterable) else
            itertools.repeat(self.delay)
        )
        for i, lights in enumerate(self.sequence(**self.sequence_kwargs)):
            if self.stop is not None and i == self.stop:
                break
            delay = next(delay_iter)

            if isinstance(self.special, ActionParams):
                action = partial(self.special.action, lights)
            else:
                action = partial(
                    self.lights.set_relays,
                    lights, 
                    special=self.special,
                )
            due = (
                self.pre_delay
                    if delay is None else 
                self.pre_delay + i * delay
            )
            name = f"SequenceMode execute {i} {lights}"
            self.schedule(
                action = action,
                due = due,
                name = name,
            )
            if delay is None:
                return
        if self.repeat: 
            self.schedule(
                action = self.execute,
                due = (i + 1) * delay,
                name = "SequenceMode continue",
            )

