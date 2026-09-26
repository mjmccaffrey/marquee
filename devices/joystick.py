# """Marquee Lighted Sign Project - joystick"""

from dataclasses import dataclass, field
from enum import auto, StrEnum
import logging

import gpiozero

from schemas import Control

log = logging.getLogger('marquee.' + __name__)


class Direction(StrEnum):
    """"""
    CENTER = auto()
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UPRIGHT = auto()
    UPLEFT = auto()
    DOWNRIGHT = auto()
    DOWNLEFT = auto()


state_to_direction = {
    '0000': Direction.CENTER,
    '0001': Direction.LEFT,
    '0010': Direction.RIGHT,
    '0100': Direction.DOWN,
    '0101': Direction.DOWNLEFT,
    '0110': Direction.DOWNRIGHT,
    '1000': Direction.UP,
    '1001': Direction.UPLEFT,
    '1010': Direction.UPRIGHT,
}


@dataclass
class Joystick(Control):
    """"""
    up: gpiozero.Button
    down: gpiozero.Button
    left: gpiozero.Button
    right: gpiozero.Button
    override: Direction | None = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        self.override = None
        self._switches = (
            self.up, self.down, 
            self.right, self.left,
        )
        for switch in self._switches:
            switch.when_pressed = lambda: print(self.direction)
            switch.when_released = lambda: print(self.direction)

    @property
    def direction(self) -> Direction:
        """Return override direction, or actual direction."""
        if self.override is not None:
            return self.override
        else:
            values = ''.join(str(s.value) for s in self._switches)
            return state_to_direction[values]

