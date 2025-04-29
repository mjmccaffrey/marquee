"""Marquee Lighted Sign Project - definitions"""

from collections.abc import Callable
from dataclasses import dataclass

LIGHTS_BY_ROW = [
    [    0, 1, 2,    ],
    [ 9,          3, ],
    [ 8,          4, ],
    [    7, 6, 5,    ],
]
TOP_LIGHTS_LEFT_TO_RIGHT = [9, 0, 1, 2, 3]
BOTTOM_LIGHTS_LEFT_TO_RIGHT = [8, 7, 6, 5, 4]
CORNER_LIGHTS_CLOCKWISE = [(9, 0), (2, 3), (4, 5), (7, 8)]
LIGHTS_CLOCKWISE = [9, 0, 1, 2, 3, 4, 5, 6, 7, 8]
LIGHT_TO_RELAY = {
            0:  9,  1: 13,  2: 14,
    9:  8,                          3: 15,
    8:  7,                          4:  2,
            7:  6,  6:  0,  5:  1,
}
EXTRA_TO_RELAY = {
    10:10, 11:11, 
    12:12, 13:3, 14:4, 15:5,
}
ALL_RELAYS = LIGHT_TO_RELAY | EXTRA_TO_RELAY
LIGHT_COUNT = len(LIGHT_TO_RELAY)
EXTRA_COUNT = len(EXTRA_TO_RELAY)
HIGH, LOW = "A", "0"
ON, OFF = "1", "0"
ALL_HIGH = HIGH * LIGHT_COUNT
ALL_LOW = LOW * LIGHT_COUNT
ALL_ON = ON * LIGHT_COUNT
ALL_OFF = OFF * LIGHT_COUNT

@dataclass
class SpecialParams:
    """Base class for special parameters."""

@dataclass
class ActionParams(SpecialParams):
    """Parameters for an arbitrary action."""
    action: Callable

@dataclass
class DimmerParams(SpecialParams):
    """Parameters for using dimmers rather than relays."""
    concurrent: bool = True
    brightness_on: int = 100
    brightness_off: int = 0
    speed_factor: float = 1.0
    transition_on: float | None = None
    transition_off: float | None = None
