# """Marquee Lighted Sign Project - joystick"""

from dataclasses import dataclass, field
from enum import auto, StrEnum
import logging

from gpiozero import Button as _Button  # type: ignore

log = logging.getLogger('marquee.' + __name__)

class Direction(StrEnum):
    """"""
    NONE = auto()
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UPRIGHT = auto()
    UPLEFT = auto()
    DOWNRIGHT = auto()
    DOWNLEFT = auto()

state_to_direction = {
    '0000': Direction.NONE,
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
class Joystick:
    """"""
    up: _Button
    down: _Button
    left: _Button
    right: _Button
    direction: Direction = field(init=False)

    def __post_init__(self) -> None:
        """"""
        self.switches = (
            self.up, self.down, 
            self.right, self.left,
        )
        for switch in self.switches:
            switch.when_pressed = self.update
            switch.when_released = self.update

    def update(self) -> None:
        """"""
        values = ''.join(str(s.value) for s in self.switches)
        self.direction = state_to_direction[values]
        print(values, self.direction)

