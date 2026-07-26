"""Marquee Lighted Sign Project - comet"""

from dataclasses import dataclass
from itertools import cycle, repeat
import logging

from devices.color import Color
from light_defs import EXTRA_CUPOLA
from . import PerformanceMode
            
log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class Comet(PerformanceMode):
    """Rotating comet with tail."""
    length: int
    delay: float
    color: Color | None = None
    wheel_divisions: int | None = None
    cupola_delay: float | None = None
    direction: int = 1

    def __post_init__(self) -> None:
        """"""
        super().__post_init__()
        assert (self.color is None) ^ (self.wheel_divisions is None)
        self.lights.set_channels(color=self.color, force=True)
        self.head = -1
        if self.color is not None:
            self.colors = repeat(self.color)
        else:
            assert self.wheel_divisions is not None
            self.colors = cycle(
                self.lights.colors.wheel_colors(self.wheel_divisions)
            )
        self.cupola_lit = False
        self.schedule(
            self.execute_12, due=self.delay, repeat=True,
        )
        if self.cupola_delay is not None:
            self.schedule(
                self.execute_cupola, due=self.cupola_delay, repeat=True,
            )

    def execute_cupola(self) -> None:
        """Cycle cupola."""
        if self.cupola_lit:
            self.extra.set_channels(
                brightness=0,
                transition=self.cupola_delay,
                index=EXTRA_CUPOLA,
            )
        else:
            self.extra.set_channels(
                brightness=100,
                transition=self.cupola_delay,
                color=self.color,
                on=True,
                index=EXTRA_CUPOLA,
                force=True,
            )
        self.cupola_lit = not self.cupola_lit

    def execute_12(self) -> None:
        """"""
        count = self.lights.count
        self.head = (self.head + self.direction) % count
        if self.head == 0:
            self.color = next(self.colors)
        self.lights.set_channels(
            brightness=100,
            transition=self.delay,
            color=self.color,
            on=True,
            index=self.head,
        )
        self.lights.set_channels(
            brightness=0,
            transition=self.delay * self.length,
            color=self.color,
            on=True,
            index=(self.head - self.direction) % count,
        )

