# """Marquee Lighted Sign Project - tiltset"""

from dataclasses import dataclass, field
from enum import auto, StrEnum
import logging

from .device_schemas import Control
import gpiozero

log = logging.getLogger('marquee.' + __name__)

class Tilt(StrEnum):
    """"""
    NONE = auto()
    FRONT_LEFT_UP = auto()
    FRONT_RIGHT_UP = auto()
    ERROR = auto()

state_to_tilt = {
    '00': Tilt.NONE,
    '01': Tilt.FRONT_LEFT_UP,
    '10': Tilt.FRONT_RIGHT_UP,
    '11': Tilt.ERROR
}


@dataclass
class TiltSet(Control):
    """"""
    left: gpiozero.Button
    right: gpiozero.Button
    tilt: Tilt = field(init=False)

    def __post_init__(self) -> None:
        """"""
        self.tilt = Tilt.NONE
        self.switches = (self.right, self.left)
        for switch in self.switches:
            switch.when_pressed = self.update
            switch.when_released = self.update

    def update(self) -> None:
        """"""
        values = ''.join(str(s.value) for s in self.switches)
        self.tilt = state_to_tilt[values]
        print(values, self.tilt)

