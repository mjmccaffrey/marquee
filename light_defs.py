"""Marquee Lighted Sign Project - light_defs"""

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
LIGHT_TO_RELAY = {
            0:  6,  1:  7,  2:  8,
    11:  5,                        3:  9,
    10:  4,                        4: 12,
     9:  1,                        5: 13,
            8:  0,  7: 15,  6: 14,
}
TOP_TO_RELAY = {
    0: 10,
}
LIGHT_COUNT = len(LIGHT_TO_RELAY)
ALL_HIGH = "A" * LIGHT_COUNT
ALL_LOW = "0" * LIGHT_COUNT
ALL_ON = "1" * LIGHT_COUNT
ALL_OFF = "0" * LIGHT_COUNT
