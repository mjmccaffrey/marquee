"""Marquee Lighted Sign Project - fastchange"""

from dataclasses import dataclass
import logging
from typing_extensions import override

from .performancemode import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class FastChange(PerformanceMode):
    """"""
    delay: float
    transition: float

    def __post_init__(self) -> None:
        super().__post_init__()
        self.rotation = 0
        self.lights.set_channels(on=True, brightness=100)
    
    @override
    def execute(self):
        """"""
        self.single()

    def single(self):
        """"""
        self.lights.set_channels(
            color=self.lights.colors.random(),
            transition=self.transition,
            channel_indexes={self.rotation},
        )
        self.schedule(due=self.delay)

    def rotate(self):
        """"""
        self.lights.set_channels(
            color=self.lights.colors.random(),
            transition=self.transition,
            channel_indexes={self.rotation},
        )
        self.rotation = (self.rotation + 1) % 12
        self.schedule(due=self.delay)

