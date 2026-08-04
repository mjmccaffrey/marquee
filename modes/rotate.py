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
        self.lights.set_channels(
            on=True,
            brightness=0,
            color=EmulateParams.color_on,
        )
        assert self.lights.mirror is not None
        self.lights.mirror.set_state_of_devices(
            '1' * self.lights.count
        )

    @override
    def execute(self) -> None:
        """"""
        self.schedule(self.rotate, self.delay, repeat=True)

    def rotate(self) -> None:
        """"""
        current = next(self.sides)
        assert self.lights.mirror is not None
        self.lights.mirror.set_state_of_devices(
            ''.join(
                '1' if i in current else '0' 
                for i in range(self.lights.count)
            )
        )
        self.lights.set_channels(
            # on=True,
            brightness=EmulateParams.brightness_on,
            # color=EmulateParams.color_on,
            transition=EmulateParams.trans_on,
            index=current,
            # force=True,
        )
        self.lights.set_channels(
            # on=False,
            brightness=0,
            transition=EmulateParams.trans_off,
            index=self.previous,
        )
        self.previous = current

