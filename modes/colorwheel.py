"""Marquee Lighted Sign Project - colorwheel"""

from dataclasses import dataclass
import logging
import random
from typing_extensions import override

from devices.color import Colors
from . import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ColorWheel(PerformanceMode):
    """"""
    delay: float
    step: int

    def __post_init__(self) -> None:
        """"""
        super().__post_init__()
        self.rotation = 0
        self.colors = list(Colors.WHEEL[:])
        self.lights.set_channels(on=True)
    
    @override
    def execute(self):
        """"""
        # random.shuffle(self.colors)
        self.lights.brightness_factor = 1000
        # 1 - self.rotation * .08
        self.lights.set_channels(
            brightness=100,
            color=self.colors,
            # (
            #     self.colors[self.rotation:] + 
            #     self.colors[:self.rotation]
            # ),
            transition=self.delay,
        )
        self.rotation = (self.rotation + self.step) % 12
        self.schedule(due=self.delay)

