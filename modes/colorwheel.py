"""Marquee Lighted Sign Project - colorwheel"""

from dataclasses import dataclass
import logging
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
        self.lights.set_channels(on=True)
    
    @override
    def execute(self):
        """"""
        self.lights.brightness_factor = 1 - self.rotation * .08
        self.lights.set_channels(
            brightness=100,
            color=(
                Colors.WHEEL[self.rotation:] + 
                Colors.WHEEL[:self.rotation]
            ),
            transition=self.delay,
        )
        self.rotation = (self.rotation + self.step) % 12
        self.schedule(due=self.delay)

