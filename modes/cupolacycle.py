"""Marquee Lighted Sign Project - cupolacycle"""

from dataclasses import dataclass
from itertools import cycle
import logging
from typing_extensions import override

from light_defs import EXTRA_CUPOLA
from . import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class CupolaSequence(PerformanceMode):
    """Set cupola light to sequence of colors."""
    background: bool = True
    color_set_name: str
    brightness: int | None = None
    transition: float
    delay: float
    wheel_divisions: int | None = None

    @override
    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        if self.wheel_divisions is not None:
            wheel = self.lights.colors.wheel_colors(self.wheel_divisions)
            self.colors = cycle(wheel)
        else:
            cs = self.color_sets.by_set_name[self.color_set_name]
            self.colors = cycle(cs.colors)

    @override
    def execute(self):
        """Change to next color."""
        assert self.extra is not None
        color = next(self.colors)
        self.extra.set_channels(
            index=EXTRA_CUPOLA,
            color=color,
            brightness=self.brightness,
            on=True,
            transition=self.transition,
            force=True,
        )
        self.schedule(due=self.delay)

