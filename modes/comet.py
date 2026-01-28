"""Marquee Lighted Sign Project - comet"""

from dataclasses import dataclass
from collections.abc import Sequence

from color import Color
from .performancemode import PerformanceMode
            

@dataclass(kw_only=True)
class Comet(PerformanceMode):
    """Rotating comet with tail."""
    length: int
    colors: Sequence[Color]
    delay: float

    def __post_init__(self) -> None:
        super().__post_init__()
        self.head = -1
        self.schedule(action=self.execute, due=self.delay, repeat=True)

    def execute(self) -> None:
        """"""
        self.head += 1
        for l in range(self.length):
            index = (self.head - l) % self.lights.count
            self.lights.set_channels(
                brightness=80 - l * 10,
                transition=1.0,
                color=self.colors[l],
                on=True,
                channel_indexes={index},
            )
        for l in range(self.lights.count - self.length):
            index = (self.head - 1 - l) % self.lights.count
            self.lights.set_channels(
                on=False,
                channel_indexes={index},
            )

