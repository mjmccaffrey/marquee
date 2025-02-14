"""Marquee Lighted Sign Project - signs"""

import asyncio
import logging

from buttons import Button, ButtonPressed, PhysicalButtonPressed
from dimmers import Dimmer, DimmerChannel, RelayOverride
from relayboards import RelayBoard

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
            0:  9,  1: 13,  2: 14,
    9:  8,                          3: 15,
    8:  7,                          4:  2,
            7:  6,  6:  0,  5:  1,
}
LIGHT_COUNT = len(_LIGHT_TO_RELAY)
_DIMMER_ADDRESSES = [
    '192.168.51.111',
    '192.168.51.112',
    '192.168.51.113',
    '192.168.51.114',
    '192.168.51.115',
]
ALL_ON = "1" * LIGHT_COUNT
ALL_OFF = "0" * LIGHT_COUNT

class Sign:
    """Supports the physical devices."""

    def __init__(self):
        """Prepare devices and initial state."""
        self.dimmers: list[Dimmer] = [
            Dimmer(address)
            for address in _DIMMER_ADDRESSES
        ]
        self.dimmer_channels: list[DimmerChannel] = [
            channel
            for dimmer in self.dimmers
            for channel in dimmer.channels
        ]
        assert len(self.dimmer_channels) == LIGHT_COUNT
        self._relayboard: RelayBoard = RelayBoard(_LIGHT_TO_RELAY)
        self._button = Button()
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

    def set_lights(
            self, 
            pattern: str, 
            relay_override: RelayOverride = None
        ):
        """Set all lights per the supplied pattern.
           Set _current_pattern, always as a string
           rather than a list."""
        if (ro := relay_override) is not None:
            levels = {0: ro.level_off, 1: ro.level_on}
            transitions = {
                0: ro.transition_off * ro.pace_factor, 
                1: ro.transition_on * ro.pace_factor,
            }
            print(transitions)
            pattern = [int(p) for p in pattern]
            if relay_override.concurrent:
                commands = [
                    d.interpret_set_parameters(
                        level=levels[p],
                        transition=transitions[p],
                        # output=
                    )
                    for d, p in zip(self.dimmer_channels, pattern)
                ]
                asyncio.run(Dimmer.execute_multiple_commands(commands))
            else:
                for d, p in zip(self.dimmer_channels, pattern):
                    d.set(
                        level=levels[p],
                        transition=transitions[p],
                    )
        else:
            self._relayboard.set_state_of_devices(pattern)
        self._current_pattern = ''.join(str(e) for e in pattern)

    def set_dimmers(
            self, 
            dimmer_pattern: str,
        ):
        """ Set the dimmers per the supplied dimmer pattern. """
        for d, b in zip(self.dimmer_channels, [int(p, 16) * 10 for p in dimmer_pattern]):
            d.set(level=b)

    @property
    def current_pattern(self):
        """Return the active light pattern."""
        return self._current_pattern

    def wait_for_button_interrupt(
            self, 
            seconds: float,
        ):
        """Pause the thread until either the seconds have elapsed
           or the button has been pressed."""
        if self._button.pressed_event.wait(seconds):
            raise PhysicalButtonPressed

    def button_interrupt_reset(self):
        """Prepare for a button press."""
        self._button.reset()
