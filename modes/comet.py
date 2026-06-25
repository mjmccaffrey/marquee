"""Marquee Lighted Sign Project - comet"""

from dataclasses import dataclass
from itertools import repeat
import logging
from typing_extensions import override

from devices.color import Color
from . import PerformanceMode
            
log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class Comet(PerformanceMode):
    """Rotating comet with tail."""
    length: int
    delay: float
    color: Color | None = None
    wheel_divisions: int | None = None

    def __post_init__(self) -> None:
        """"""
        super().__post_init__()
        assert (self.color is None) ^ (self.wheel_divisions is None)
        self.head = -1
        if self.color is not None:
            self.colors = repeat(self.color)
        else:
            self.colors = iter(self.lights.colors.WHEEL)
        self.schedule(due=self.delay, repeat=True)

    @override
    def execute(self) -> None:
        """"""
        count = self.lights.count
        self.head = (self.head + 1) % count
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
            index=(self.head - 1) % count,
        )

