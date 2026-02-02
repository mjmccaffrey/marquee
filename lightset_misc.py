"""Marquee Lighted Sign Project - lightset_misc"""

"""Everything here except TOP_* and CLICK_* """
"""applies to the primary LightSet."""

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
LIGHTS_COL_B = [0, 8]
LIGHTS_COL_C = [1, 7]
LIGHTS_COL_D = [2, 6]
LIGHTS_BY_COL = [
    LIGHTS_LEFT, LIGHTS_COL_B, LIGHTS_COL_C, LIGHTS_COL_D, LIGHTS_RIGHT,
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
CLICK_TO_RELAY = {
     0: 2,  1: 3, 2: 11,
}
ALL_RELAYS = LIGHT_TO_RELAY | TOP_TO_RELAY | CLICK_TO_RELAY

HIGH, LOW = "A", "0"
ON, OFF = "1", "0"
LIGHT_COUNT = len(LIGHT_TO_RELAY)
ALL_HIGH = HIGH * LIGHT_COUNT
ALL_LOW = LOW * LIGHT_COUNT
ALL_ON = ON * LIGHT_COUNT
ALL_OFF = OFF * LIGHT_COUNT
