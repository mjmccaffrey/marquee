"""Marquee Lighted Sign Project - comet"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from itertools import chain

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
        self.wheel = chain(self.lights.colors.WHEEL)
        self.schedule(action=self.execute, due=self.delay, repeat=True)

    def execute(self) -> None:
        """"""
        count = self.lights.count
        self.head = (self.head + 1) % count
        print(self.head)
        if self.head == 0:
            color = next(self.wheel)
        for i, c in enumerate(self.colors):
            self.lights.set_channels(
                brightness=100 - i * 25,
                transition=self.delay,
                color=color,
                on=True,
                channel_indexes={(self.head - i) % count},
            )
        self.lights.set_channels(
            on=False,
            transition=self.delay,
            channel_indexes={(self.head - len(self.colors)) % count},
        )

