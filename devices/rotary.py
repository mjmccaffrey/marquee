# """Marquee Lighted Sign Project - rotary"""

from dataclasses import dataclass
import logging

import gpiozero

from schemas import Control

log = logging.getLogger('marquee.' + __name__)


@dataclass
class RotaryEncoder100(Control):
    """"""
    a: gpiozero.DigitalInputDevice
    b: gpiozero.DigitalInputDevice

    def __post_init__(self) -> None:
        self._position = 0
        self.a.when_deactivated = self._a_falling

    @property
    def position(self) -> int:
        return self._position

    def _a_falling(self) -> None:
        if self.b.value:
            direction = +1
        else:
            direction = -1
        self._position += direction
        match self._position:
            case 100:
                self._position = 0
            case -1:
                self._position = 99
            case _:
                pass
        print(self.position)

