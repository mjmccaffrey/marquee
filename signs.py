"""Marquee Lighted Sign Project - signs"""

import asyncio
import logging

from buttons import Button, ButtonPressed, PhysicalButtonPressed
from dimmers import Dimmer, DimmerChannel, RelayOverride, TRANSITION_MINIMUM
from relayboards import RelayBoard

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
_LIGHT_TO_RELAY = {
            0:  9,  1: 13,  2: 14,
    9:  8,                          3: 15,
    8:  7,                          4:  2,
            7:  6,  6:  0,  5:  1,
}
_EXTRA_RELAYS = {
    10:10, 11:11, 12:12, 13: 3, 14: 4, 15: 5,
}
_ALL_RELAYS = _LIGHT_TO_RELAY | _EXTRA_RELAYS
LIGHT_COUNT = len(_LIGHT_TO_RELAY)
_DIMMER_ADDRESSES = [
    '192.168.51.111',
    '192.168.51.112',
    '192.168.51.113',
    '192.168.51.114',
    '192.168.51.115',
]
ALL_HIGH = "A" * LIGHT_COUNT
ALL_LOW = "0" * LIGHT_COUNT
ALL_ON = "1" * LIGHT_COUNT
ALL_OFF = "0" * LIGHT_COUNT

class Sign:
    """Supports the physical devices."""

    def __init__(self):
        """Prepare devices and initial state."""
        print("Initializing sign")
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
        self._relayboard: RelayBoard = RelayBoard(_ALL_RELAYS)
        self._button = Button()
        full_pattern = self._relayboard.get_state_of_devices()
        self.light_pattern = full_pattern[:LIGHT_COUNT]
        self.extra_pattern = full_pattern[LIGHT_COUNT:]

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

    def _set_lights_relay_override(
            self,
            light_pattern: str, 
            relay_override: RelayOverride,
    ):
        """"""
        ro = relay_override
        brightnessses = {0: ro.brightness_off, 1: ro.brightness_on}
        transitions = {
            0: max(TRANSITION_MINIMUM, ro.transition_off * ro.speed_factor), 
            1: max(TRANSITION_MINIMUM, ro.transition_on * ro.speed_factor),
        }
        # print(transitions)
        light_pattern = [int(p) for p in light_pattern]
        if ro.concurrent:
            commands = [
                d.make_set_command(
                    brightness=brightnessses[p],
                    transition=transitions[p],
                )
                for d, p in zip(self.dimmer_channels, light_pattern)
            ]
            asyncio.run(Dimmer.execute_multiple_commands(commands))
        else:
            for d, p in zip(self.dimmer_channels, light_pattern):
                d.set(
                    brightness=brightnessses[p],
                    transition=transitions[p],
                )

    def set_lights(
            self, 
            light_pattern: str,
            extra_pattern: str = None,
            relay_override: RelayOverride = None,
        ):
        """Set all lights per the supplied light_pattern.
           Set light_pattern, always as a string
           rather than a list."""
        light_pattern = ''.join(str(e) for e in light_pattern)
        if relay_override is not None:
            self._set_lights_relay_override(light_pattern, relay_override)
        else:
            if extra_pattern is None:
                extra_pattern = self.extra_pattern
            else:
                extra_pattern = ''.join(str(e) for e in extra_pattern)
            full_pattern = light_pattern + extra_pattern
            self._relayboard.set_state_of_devices(full_pattern)
            self.extra_pattern = extra_pattern
        self.light_pattern = light_pattern

    def set_dimmers(
            self, 
            pattern: str = None,
            brightnesses: list[int] = None,
        ):
        """ Set the dimmers per the supplied pattern or brightnesses. """
        assert not (pattern and brightnesses), "Specify either pattern or brightnesses."
        if pattern is not None:
            adjustments = {  # !!! adjust for frosted 40 watt
                '0': 0, '1': 15, '2': 20, '3': 30, '4': 40,
                '5': 50, '6': 60, '7': 70, '8':80, '9': 90,
                'A': 100, 'F': 23,
            }
            brightnesses = [
                adjustments[p]
                for p in pattern
            ]
            # current = self.dimmer_brightnesses()
            updates = [
                (c, b)
                for c, b in zip(
                    self.dimmer_channels,
                    brightnesses,
                )
                if c.brightness != b
            ]
            print(updates)
        commands = [
            c.make_set_command(output=True, brightness=b)
            for c, b in updates
        ]
        asyncio.run(Dimmer.execute_multiple_commands(commands))

    @property
    def light_pattern(self):
        """Return the active light pattern."""
        return self._light_pattern
    
    @light_pattern.setter
    def light_pattern(self, value):
        """Update the active light pattern."""
        self._light_pattern = value
        # print(f"Current_pattern is now:{self._light_pattern}")

    def dimmer_brightnesses(self):
        """"""
        return [
            channel.brightness
            for dimmer in self.dimmers
            for channel in dimmer.channels
        ]

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
