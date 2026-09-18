"""Marquee Lighted Sign Project - light_defs"""

from enum import IntEnum

class Light(IntEnum):
    TL =  0  # Top
    TM =  1
    TR =  2
    RT =  3  # Right
    RM =  4
    RB =  5
    BR =  6  # Bottom
    BM =  7
    BL =  8
    LB =  9  # Left
    LM = 10
    LU = 11
    ML = 12  # Middle
    MM = 13
    MR = 14
    CP = 15  # Cupola

LIGHTS_BY_ROW = [
    [    0, 1, 2,    ],
    [ 11,         3, ],
    [ 10,         4, ],
    [ 9,          5, ],
    [    8, 7, 6,    ],
]
LIGHTS_TOP = [0, 1, 2,]
LIGHTS_RIGHT = [3, 4, 5,]
LIGHTS_BOTTOM = [6, 7, 8,]
LIGHTS_LEFT = [9, 10, 11]
LIGHTS_MIDDLE = [12, 13, 14]
LIGHTS_BY_SIDE = [
    LIGHTS_TOP, LIGHTS_RIGHT, LIGHTS_BOTTOM, LIGHTS_LEFT,
]
LIGHTS_COLUMN_B = [0, 8]
LIGHTS_COLUMN_C = [1, 7]
LIGHTS_COLUMN_D = [2, 6]
LIGHTS_BY_COLUMN = [
    LIGHTS_LEFT, LIGHTS_COLUMN_B, LIGHTS_COLUMN_C, LIGHTS_COLUMN_D, LIGHTS_RIGHT,
]
LIGHTS_CLOCKWISE = [
    i for side in LIGHTS_BY_SIDE for i in side
]
LIGHT_COUNT = 16
ALL_HIGH = "A" * LIGHT_COUNT
ALL_LOW = "0" * LIGHT_COUNT
ALL_ON = "1" * LIGHT_COUNT
ALL_OFF = "0" * LIGHT_COUNT

