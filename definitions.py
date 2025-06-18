"""Marquee Lighted Sign Project - definitions"""

from collections.abc import Callable
from dataclasses import dataclass

LIGHTS_BY_ROW = [
    [    0, 1, 2,    ],
    [ 11,         3, ],
    [ 10,         4, ],
    [ 9,          5, ],
    [    8, 7, 6,    ],
]
LIGHTS_TOP = [0, 1, 2,]
LIGHTS_LEFT = [11, 10, 9,]
LIGHTS_RIGHT = [3, 4, 5,]
LIGHTS_BOTTOM = [8, 7, 6,]
LIGHTS_CLOCKWISE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
LIGHT_TO_RELAY = {
            0:  6,  1:  7,  2:  8,
    11:  5,                        3:  9,
    10:  4,                        4: 12,
     9:  1,                        5: 13,
            8:  0,  7: 15,  6: 14,
}
EXTRA_TO_RELAY = {
     12: 2,  13: 3, 14: 10, 15: 11,
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
DIMMER_ADDRESSES = [
    '192.168.51.111',
    '192.168.51.112',
    '192.168.51.113',
    '192.168.51.114',
    '192.168.51.115',
    '192.168.51.116',
]

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
