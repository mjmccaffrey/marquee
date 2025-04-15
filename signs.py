"""Marquee Lighted Sign Project - signs"""

import asyncio
import logging

from buttons import Button
from definitions import *
from dimmers import (
    ShellyDimmer, DimmerChannel,
    TRANSITION_DEFAULT, TRANSITION_MINIMUM,
)
from instruments import BellSet, DrumSet
from relays import NumatoUSBRelayModule

class Sign:
    """Supports the physical devices."""

    def __init__(
        self,
        bell_set: BellSet,
        drum_set: DrumSet,
        dimmers: list[ShellyDimmer],
        light_relays: NumatoUSBRelayModule,
        buttons: list[Button],
        brightness_factor: float,
    ):
        """Set up the initial state."""
        print("Initializing sign")
        self.bell_set = bell_set
        self.drum_set = drum_set
        self.dimmers = dimmers
        self._light_relays = light_relays
        self._buttons = buttons
        self.brightness_factor = brightness_factor

        # channel[i] maps to light[i], 0 <= i < LIGHT_COUNT
        self.dimmer_channels: list[DimmerChannel] = [
            channel
            for dimmer in self.dimmers
            for channel in dimmer.channels
        ]
        for c in self.dimmer_channels:
            print(c)
        assert len(self.dimmer_channels) == LIGHT_COUNT
        full_pattern = self._light_relays.get_state_of_devices()
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
            self._light_relays.close()
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
            special: DimmerParams,
    ):
        """Set dimmers per the specified pattern and special."""
        bright_values: dict[int, int] = {
            0: int(special.brightness_off * self.brightness_factor), 
            1: int(special.brightness_on * self.brightness_factor),
        }
        assert special.transition_off is not None
        assert special.transition_on is not None
        trans_values: dict[int, float] = {
            0: max(TRANSITION_MINIMUM, 
                   special.transition_off * special.speed_factor), 
            1: max(TRANSITION_MINIMUM, 
                   special.transition_on * special.speed_factor),
        }
        light_pattern = [int(p) for p in light_pattern]
        brightnesses=[
            bright_values[p]
            for p in light_pattern
        ]
        transitions=[
            trans_values[p]
            for p in light_pattern
        ]
        if special.concurrent:
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
            special: SpecialParams | None = None,
        ):
        """Set all lights and extra relays per supplied patterns and special.
           Set light_pattern property, always as string
           rather than list."""
        assert len(light_pattern) == LIGHT_COUNT
        assert extra_pattern is None or len(extra_pattern) == EXTRA_COUNT
        light_pattern = ''.join(str(e) for e in light_pattern)
        if isinstance(special, DimmerParams):
            self._set_lights_relay_override(light_pattern, special)
        else:
            if extra_pattern is None:
                extra_pattern = self.extra_pattern
            else:
                extra_pattern = ''.join(str(e) for e in extra_pattern)
            full_pattern = light_pattern + extra_pattern
            self._light_relays.set_state_of_devices(full_pattern)
            self.extra_pattern = extra_pattern
            self.light_pattern = light_pattern

    def flip_extra_relays(self, *indices: int):
        """"""
        def flip(s):
            return '0' if s == '1' else '1'
        assert all(0 <= i < len(self.extra_pattern) for i in indices)
        extra = ''.join(
            flip(e) if i in indices else e
            for i, e in enumerate(self.extra_pattern)
        )
        self.set_lights(self.light_pattern, extra)

    def click(self):
        """Generate a small click sound by flipping
           an otherwise unused relay."""
        self.flip_extra_relays(5)

    def set_dimmers(
            self, 
            pattern: str | None = None,
            brightnesses: list[int] | None = None,
            transitions: list[float] | float = TRANSITION_DEFAULT,
            force_update: bool = False,
        ):
        """ Set the dimmers per the supplied pattern or brightnesses,
            and transition times. """
        assert pattern is None or len(pattern) == LIGHT_COUNT
        assert not (pattern and brightnesses), "Specify either pattern or brightnesses."
        if pattern is not None:
            bulb_adjustments = {  # !!! adjust for frosted 40 watt
                '0': 0, '1': 15, '2': 20, '3': 30, '4': 40,
                '5': 50, '6': 60, '7': 70, '8':80, '9': 90,
                'A': 100, 'F': 23,
            }
            brightnesses = [
                int(bulb_adjustments[p] * self.brightness_factor)
                for p in pattern
            ]
        if isinstance(transitions, float):
            transitions = [transitions] * LIGHT_COUNT
        assert brightnesses is not None
        assert isinstance(transitions, list)
        if force_update:
            updates = [t for t in zip(self.dimmer_channels, brightnesses, transitions)]
        else:
            updates = self._updates_needed(brightnesses, transitions)
        self.execute_dimmer_commands(updates)

    def execute_dimmer_commands(
            self,
            updates: list[tuple[DimmerChannel, int, float]],
    ):
        print("????????????????", updates)
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
