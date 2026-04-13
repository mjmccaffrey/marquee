"""Marquee Lighted Sign Project - sequencemode"""

from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from functools import partial
import itertools
import logging
from typing import Any, cast, Iterable

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
    baseline: LightSetBaseline | None = None
    color_set_name: str | None = None
    sequence_kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize."""
        self.baseline = self.baseline or DEFAULT_BASELINE
        color_sets = cast(dict, self.color_sets.by_set_name)
        self.color_set = color_sets.get(self.color_set_name)
        print(self.color_set)
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
        print("**************************************************")
        delay_iter = (
            itertools.cycle(self.delay) 
                if isinstance(self.delay, Iterable) else
            itertools.repeat(self.delay)
        )
        for i, pattern in enumerate(self.sequence(**self.sequence_kwargs)):
            if self.stop is not None and i == self.stop:
                break
            action = self.action_partial(pattern)
            delay = next(delay_iter)
            due = (
                self.pre_delay
                    if delay is None else 
                self.pre_delay + i * delay
            )
            print(i, delay, pattern)
            self.schedule(
                action = action,
                due = due,
                name = f"SequenceMode execute {i} {pattern}",
            )
            if delay is None:
                return
        if self.repeat: 
            self.schedule(
                action = self.execute,
                due = (i + 1) * delay,
                name = "SequenceMode continue",
            )

    def action_partial(self, pattern: str) -> Callable:
        """"""
        if isinstance(self.special, ActionParams):
            action = partial(self.special.action, pattern)
        elif self.color_set is not None:
            action = partial(
                self.set_color_lights,
                pattern, 
            )
        else:
            action = partial(
                self.lights.set_relays,
                pattern, 
                special=self.special,
            )
        return action

    def set_color_lights(self, pattern: str) -> None:
        """"""
        assert self.color_set is not None
        assert len(pattern) == self.lights.count
        assert all(
            int(p) in range(len(self.color_set.colors))
            for p in pattern
        )
        cs_kwargs = self.color_set.set_channels_kwargs
        kwargs = {
            'on': (False if p == '0' else True for p in pattern),
            'brightness': (
                None if p == '0' else cs_kwargs['brightness'][int(p)]
                for p in pattern
            ),
            'color': (
                None if p == '0' else cs_kwargs['color'][int(p)]
                for p in pattern
            ),
        }
        print(kwargs)
        self.lights.set_channels(**kwargs)

