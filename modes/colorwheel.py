"""Marquee Lighted Sign Project - colorwheel"""

from dataclasses import dataclass
import logging
from typing_extensions import override

from .performancemode import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ColorWheel(PerformanceMode):
    """"""
    delay: float

    def __post_init__(self) -> None:
        super().__post_init__()
        self.rotation = 0
        self.lights.set_channels(on=True)
    
    @override
    def execute(self):
        """"""
        values = (
            (100, 0, 0),
            (100, 50, 0),
            (100, 100, 0),
            (50, 80, 0),
            (0, 100, 0),
            (0, 100, 50),
            (0, 100, 100),
            (0, 60, 100),
            (0, 0, 100),
            (50, 0, 100),
            (100, 0, 100),
            (100, 0, 50),
        )
        for i, (r, g, b) in enumerate(values):
            self.lights.set_channels(
                brightness=100, # int(100 / 12 * ((i + self.rotation + 1) % 12)),
                color=self.lights.colors.rgb(
                    int(r / 100 * 255),
                    int(g / 100 * 255),
                    int(b / 100 * 255),
                ),
                transition=self.delay * 2,
                channel_indexes={(i + self.rotation) % 12},
            )
        self.rotation = (self.rotation + 1) % 12
        self.schedule(due=self.delay)

