"""Marquee Lighted Sign Project - rotate"""

from dataclasses import dataclass
from itertools import cycle, repeat
import logging
from typing_extensions import override

from devices.color import Color
from devices.specialparams import EmulateParams
from light_defs import LIGHTS_BY_SIDE
from . import PerformanceMode
            
log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class RotateSides(PerformanceMode):
    """Rotate sides with relay and incandescent emulation."""
    delay: float

    def __post_init__(self) -> None:
        """"""
        super().__post_init__()
        self.sides = cycle(LIGHTS_BY_SIDE)
        self.previous = next(self.sides)
        self.lights.set_channels(on=False)

    @override
    def execute(self) -> None:
        """"""
        self.schedule(self.rotate, self.delay, repeat=True)

    def rotate(self) -> None:
        """"""
        current = next(self.sides)
        self.lights.set_channels(
            on=True,
            brightness=EmulateParams.brightness_on,
            color=EmulateParams.color_on,
            transition=EmulateParams.trans_on,
            index=current,
        )
        self.lights.set_channels(
            on=False,
            # transition=EmulateParams.trans_off,
            index=self.previous,
        )
        self.previous = current

