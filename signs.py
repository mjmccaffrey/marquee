"""Marquee Lighted Sign Project - signs"""

import logging

import buttons
from buttons import (  # pylint: disable=unused-import
    ButtonPressed,
    PhysicalButtonPressed,
    VirtualButtonPressed,
)
import dimmers
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
_DIMMER_ADDRESSES = [
    '192.168.51.111',
    '192.168.51.112',
    '192.168.51.113',
    '192.168.51.114',
    '192.168.51.115',
]

class Sign:
    """Supports the physical devices."""

    def __init__(self):
        """Prepare devices and initial state."""
        self._dimmers = [
            dimmers.Dimmer(address, id)
            for address in _DIMMER_ADDRESSES
            for id in range(2)
        ]
        assert len(self._dimmers) == LIGHT_COUNT
        self._relayboard = relayboards.RelayBoard(_LIGHT_TO_RELAY)
        self._button = buttons.Button()
        self._current_pattern = self._relayboard.get_state_of_devices()

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
        """Set all lights per the supplied pattern.
           Set _current_pattern, always as a string
           rather than a list."""
        if self.use_dimmers:
            for d, l in zip(self._dimmers, pattern):  # !!!  USE set_dimmers
                if bool(int(l)):
                    d.set_brightness(level=100, transition=0.5)
                else:
                    d.set_brightness(level=0, transition=2.0)
        else:
            self._relayboard.set_state_of_devices(pattern)
        self._current_pattern = ''.join(str(e) for e in pattern)

    def set_dimmers(self, pattern):
        """ """
        for d, b in zip(self._dimmers, [int(p, 16) * 10 for p in pattern]):
            d.set_brightness(level=b)

    @property
    def current_pattern(self):
        """Return the active light pattern."""
        return self._current_pattern

    def wait_for_interrupt(self, seconds):
        """Pause the thread until either the seconds have elapsed
           or the button has been pressed."""
        if self._button.pressed_event.wait(seconds):
            raise PhysicalButtonPressed

    def interrupt_reset(self):
        """Prepare for a button press."""
        self._button.reset()
