"""Marquee Lighted Sign Project - comet"""

from dataclasses import dataclass
from collections.abc import Sequence

from color import Color
from .performancemode import PerformanceMode
            

@dataclass(kw_only=True)
class Comet(PerformanceMode):
    """Rotating comet with tail."""
    colors: Sequence[Color]
    delay: float

    def __post_init__(self) -> None:
        super().__post_init__()
        self.head = -1
        self.schedule(action=self.execute, due=self.delay, repeat=True)

    def execute(self) -> None:
        """"""
        count = self.lights.count
        self.head = (self.head + 1) % count
        for i, c in enumerate(self.colors):
            self.lights.set_channels(
                brightness=100 - i * 25,
                transition=self.delay,
                color=self.colors[0],
                on=True,
                channel_indexes={(self.head - i) % count},
            )
        self.lights.set_channels(
            on=False,
            transition=self.delay,
            channel_indexes={(self.head - len(self.colors)) % count},
        )

