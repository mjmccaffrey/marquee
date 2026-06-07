"""Marquee Lighted Sign Project - colorwheel"""

from dataclasses import dataclass
import logging
from typing_extensions import override

from devices.color import Colors
from .performancemode import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ColorWheel(PerformanceMode):
    """"""
    delay: float

    def __post_init__(self) -> None:
        """"""
        super().__post_init__()
        self.rotation = 0
        self.lights.set_channels(on=True)
    
    @override
    def execute(self):
        """"""
        self.lights.set_channels(
            brightness=100,
            color=Colors.WHEEL[:self.rotation][self.rotation:],
            transition=self.delay * 2,
        )
        self.rotation = (self.rotation + 1) % 12
        self.schedule(due=self.delay)

