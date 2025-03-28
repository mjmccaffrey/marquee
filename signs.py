"""Marquee Lighted Sign Project - signs"""

import asyncio
import logging

from buttons import Button
from dimmers import (
    ShellyDimmer, DimmerChannel, RelayOverride, 
    TRANSITION_DEFAULT, TRANSITION_MINIMUM,
)
from relays import NumatoUSBRelayModule

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
CLICK_RELAY = 12
GRACE_RELAYS = [13, 14, 15]
EXTRA_TO_RELAY = {
    10:10, 11:11, 
    12:12, 13:3, 14:4, 15:5,
}
ALL_RELAYS = LIGHT_TO_RELAY | EXTRA_TO_RELAY
LIGHT_COUNT = len(LIGHT_TO_RELAY)
EXTRA_COUNT = len(EXTRA_TO_RELAY)
ALL_HIGH = "A" * LIGHT_COUNT
ALL_LOW = "0" * LIGHT_COUNT
ALL_ON = "1" * LIGHT_COUNT
ALL_OFF = "0" * LIGHT_COUNT

class Sign:
    """Supports the physical devices."""

    def __init__(
        self,
        dimmers: list[ShellyDimmer],
        relaymodule: NumatoUSBRelayModule,
        buttons: list[Button],
    ):
        """Set up the initial state."""
        print("Initializing sign")
        self.dimmers = dimmers
        self._relaymodule = relaymodule
        self._buttons = buttons

        # channel[i] maps to light[i], 0 <= i < LIGHT_COUNT
        self.dimmer_channels: list[DimmerChannel] = [
            channel
            for dimmer in self.dimmers
            for channel in dimmer.channels
        ]
        assert len(self.dimmer_channels) == LIGHT_COUNT
        full_pattern = self._relaymodule.get_state_of_devices()
        self.light_pattern = full_pattern[:LIGHT_COUNT]
        self.extra_pattern = full_pattern[LIGHT_COUNT:]

    def close(self):
        """Clean up."""
        try:
            for button in self._buttons:
                button.close()
        except Exception as e:
            logging.exception(e)
        try:
            self._relaymodule.close()
        except Exception as e:
            logging.exception(e)

    def _updates_needed(
        self, 
        brightnesses: list[int], 
        transitions: list[float],
    ) -> list[tuple[DimmerChannel, int, float]]:
        """Return delta between current state and desired state."""
        return [
            (c, b, t)
            for c, b, t in zip(
                self.dimmer_channels,
                brightnesses,
                transitions,
            )
            if c.brightness != b
        ]

    def _set_lights_relay_override(
            self,
            light_pattern: list | str, 
            override: RelayOverride,
    ):
        """Set dimmers per the specified pattern and override."""
        bright_values = {
            0: override.brightness_off, 
            1: override.brightness_on
        }
        assert override.transition_off is not None
        assert override.transition_on is not None
        trans_values = {
            0: max(TRANSITION_MINIMUM, 
                   override.transition_off * override.speed_factor), 
            1: max(TRANSITION_MINIMUM, 
                   override.transition_on * override.speed_factor),
        }
        light_pattern = [int(p) for p in light_pattern]
        #print(f"light_pattern:{light_pattern}")
        brightnesses=[
            bright_values[p]
            for p in light_pattern
        ]
        transitions=[
            trans_values[p]
            for p in light_pattern
        ]
        if override.concurrent:
            self.set_dimmers(
                brightnesses=brightnesses, 
                transitions=transitions,
            )
        else:
            updates = self._updates_needed(brightnesses, transitions)
            for c, b, t in updates:
                c.set(brightness=b, transition=t)
            
    def set_lights(
            self, 
            light_pattern: str,
            extra_pattern: str | None = None,
            override: RelayOverride | None = None,
        ):
        """Set all lights and extra relays per supplied patterns and override.
           Set light_pattern property, always as string
           rather than list."""
        light_pattern = ''.join(str(e) for e in light_pattern)
        if override is not None:
            self._set_lights_relay_override(light_pattern, override)
        else:
            if extra_pattern is None:
                extra_pattern = self.extra_pattern
            else:
                extra_pattern = ''.join(str(e) for e in extra_pattern)
            full_pattern = light_pattern + extra_pattern
            print(light_pattern, extra_pattern)
            self._relaymodule.set_state_of_devices(full_pattern)
            self.extra_pattern = extra_pattern
            self.light_pattern = light_pattern

    def set_dimmers(
            self, 
            pattern: str | None = None,
            brightnesses: list[int] | None = None,
            transitions: list[float] | float = TRANSITION_DEFAULT,
            force_update: bool = False,
        ):
        """ Set the dimmers per the supplied pattern or brightnesses,
            and transition times. """
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
        if isinstance(transitions, float):
            transitions = [transitions] * LIGHT_COUNT
        assert brightnesses is not None
        assert isinstance(transitions, list)
        if force_update:
            updates = zip(self.dimmer_channels, brightnesses, transitions)
        else:
            updates = self._updates_needed(brightnesses, transitions)
        commands = [
            c.make_set_command(
                brightness=b,
                transition=t,
            )
            for c, b, t in updates
        ]
        asyncio.run(ShellyDimmer.execute_multiple_commands(commands))
        for command in commands:
            command.channel.brightness = command.params['brightness']

    def click(self):
        """Generate a small click sound by flipping
           an otherwise unused relay."""
        extra = self.extra_pattern
        extra = extra[:-1] + ("0" if extra[-1] == "1" else "1")
        self.set_lights(self.light_pattern, extra)

    @property
    def light_pattern(self) -> str:
        """Return the active light pattern."""
        return self._light_pattern
    
    @light_pattern.setter
    def light_pattern(self, value):
        """Update the active light pattern."""
        self._light_pattern = value

    def dimmer_brightnesses(self) -> list[int]:
        """Return the active dimmer pattern."""
        return [
            channel.brightness
            for dimmer in self.dimmers
            for channel in dimmer.channels
        ]
