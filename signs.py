"""Marquee Lighted Sign Project - signs"""

import logging

import buttons
from buttons import (  # pylint: disable=unused-import
    ButtonPressed,
    PhysicalButtonPressed,
    VirtualButtonPressed,
)
import relayboards

LIGHTS_BY_ROW = [
    [    0, 1, 2,    ],
    [ 9,          3, ],
    [ 8,          4, ],
    [    7, 6, 5,    ],
]
TOP_LIGHTS_LEFT_TO_RIGHT = [9, 0, 1, 2, 3]
BOTTOM_LIGHTS_LEFT_TO_RIGHT = [8, 7, 6, 5, 4]
LIGHTS_CLOCKWISE = [9, 0, 1, 2, 3, 4, 5, 6, 7, 8]
_LIGHT_TO_RELAY = {
    0:  9,
    1: 13,
    2: 14,
    3: 15,
    4:  2,
    5:  1,
    6:  0,
    7:  6,
    8:  7,
    9:  8,
}
LIGHT_COUNT = len(_LIGHT_TO_RELAY)

class Sign:
    """Supports the physical devices."""

    def __init__(self):
        """Prepare devices and initial state."""
        self._relayboard = relayboards.RelayBoard(_LIGHT_TO_RELAY)
        self._button = buttons.Button()
        self._current_pattern = None

    def close(self):
        """Clean up."""
        try:
            self._button.close()
        except Exception as e:
            logging.exception(e)
        try:
            self._relayboard.close()
        except Exception as e:
            logging.exception(e)

    def set_lights(self, pattern):
        """Set all lights per the supplied pattern."""
        self._relayboard.set_relays_from_pattern(pattern)
        self._current_pattern = pattern

    @property
    def current_pattern(self):
        """Return the currenly active light pattern."""
        return self._current_pattern.copy()

    def wait_for_interrupt(self, seconds):
        """Pause the thread until either the seconds have elapsed
           or the button has been pressed."""
        if self._button.pressed_event.wait(seconds):
            raise PhysicalButtonPressed

    def interrupt_reset(self):
        """Prepare for a button press."""
        self._button.reset()

    @staticmethod
    def is_valid_light_pattern(arg):
        """ Return True if arg is a valid light pattern, otherwise False. """
        return len(arg) == LIGHT_COUNT and all(e in {"0", "1"} for e in arg)
