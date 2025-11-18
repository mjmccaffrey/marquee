"""Marquee Lighted Sign Project - lightset"""

from dataclasses import dataclass, InitVar

from bulb import SmartBulb
from lightcontroller import LightController, LightChannel, Color
from relays import RelayModule
from specialparams import DimmerParams, MirrorParams, SpecialParams


@dataclass
class LightSet:
    """Supports all of the light-related devices."""
    relays: RelayModule
    light_relays: set[int]
    click_relays: set[int]
    controller: LightController
    brightness_factor_init: InitVar[float]

    def __post_init__(self, brightness_factor_init: float) -> None:
        """Initialize."""
        self.light_count = len(self.light_relays)

        # channel[i] maps to light[i], 0 <= i < light_count
        self.dimmer_channels: list[LightChannel] = [
            channel
            for channel in self.controller.channels
        ]


        assert len(self.dimmer_channels) == self.light_count
        full_pattern = self.relays.get_state_of_devices()
        self.relay_pattern = full_pattern[:self.light_count]



        self.extra_pattern = full_pattern[self.light_count:]



        self.brightness_factor = brightness_factor_init

    @property
    def brightness_factor(self) -> float:
        return self._brightness_factor
    
    @brightness_factor.setter
    def brightness_factor(self, value) -> None:
        self._brightness_factor = value
        print("Brightness factor is ", self._brightness_factor)

    def _updates_needed(
        self, 
        brightnesses: list[int], 
        transitions: list[float],
        colors: list['Color | None'],
    ) -> list[tuple[LightChannel, int, float, 'Color | None']]:
        """Return delta between current state and desired state."""
        return [
            (chan, b, t, c)
            for chan, b, t, c in zip(
                self.dimmer_channels,
                brightnesses,
                transitions,
                colors,
            )
            if chan.brightness != b and chan.color != c
        ]

    def _set_channels_instead_of_relays(
            self,
            light_pattern: list | str, 
            special: DimmerParams,
    ) -> None:
        """Set channels per the specified pattern and special.
           Adjust for brightness_factor."""
        bright_values: dict[int, int] = {
            0: int(special.brightness_off * self._brightness_factor), 
            1: int(special.brightness_on * self._brightness_factor),
        }
        assert special.transition_off is not None
        assert special.transition_on is not None
        trans_values: dict[int, float] = {
            0: max(self.controller.transition_minimum, 
                   special.transition_off * special.speed_factor), 
            1: max(self.controller.transition_minimum, 
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
            
    def set_relays(
            self, 
            light_pattern: str,
            extra_pattern: str | None = None,
            special: SpecialParams | None = None,
            smart_bulb_override: bool = False,
        ) -> None:
        """Set all lights and extra relays per supplied patterns and special.
           Set light_pattern property, always as string
           rather than list."""
        assert len(light_pattern) == self.light_count
        assert (
                extra_pattern is None
             or len(extra_pattern) == len(self.extra_pattern)
        )
        light_pattern = ''.join(str(e) for e in light_pattern)
        if isinstance(special, DimmerParams):
            self._set_dimmers_instead_of_relays(light_pattern, special)
        else:
            if extra_pattern is None:
                extra_pattern = self.extra_pattern
            else:
                extra_pattern = ''.join(str(e) for e in extra_pattern)
            full_pattern = light_pattern + extra_pattern
            if (
                    isinstance(self.controller.bulb_compatibility, SmartBulb)
                and not smart_bulb_override
            ):
                raise TypeError("Light relay change request refused.")
            self.relays.set_state_of_devices(full_pattern)
            if isinstance(special, MirrorParams):
                special.func(full_pattern)
            self.extra_pattern = extra_pattern
            self.relay_pattern = light_pattern

    def set_channels(
            self, 
            pattern: str | None = None,
            brightnesses: list[int] | None = None,
            transitions: list[float] | float = 0.0,
            force_update: bool = False,
        ) -> None:
        """Set the dimmers per the supplied pattern or brightnesses,
           and transition times.  If pattern, apply bulb_adjustments.
           Adjust for brightness_factor."""
        assert pattern is None or len(pattern) == self.light_count
        assert not (pattern and brightnesses), "Specify either pattern or brightnesses."
        if not transitions:
            transitions = self.controller.transition_default
        if pattern is not None:
            brightnesses = [
                self.controller.bulb_model.adjustments[p]
                for p in pattern
            ]
        if isinstance(transitions, float):
            transitions = [transitions] * self.light_count
        assert brightnesses is not None
        brightnesses = [
            int(b * self._brightness_factor)
            for b in brightnesses
        ]
        assert isinstance(transitions, list)
        if force_update:
            updates = [t for t in zip(self.dimmer_channels, brightnesses, transitions)]
        else:
            updates = self._updates_needed(brightnesses, transitions)
        self._execute_dimmer_commands(updates)

    def set_channel_subset(
            self,
            lights: list[int],
            brightness: int,
            transition: float,
    ) -> None:
        """Set lights (indexes) / dimmer channels 
           to brightness with transition.
           Adjust for brightness_factor."""
        brightness = int(brightness * self._brightness_factor)
        self._execute_dimmer_commands([
            (   self.dimmer_channels[light], 
                brightness, 
                transition,
            )
            for light in lights
        ])

    def _execute_channel_commands(
            self,
            updates: list[tuple[LightChannel, int, float]],
    ) -> None:
        """Set each dimmer channel to brightness at transition rate."""
        commands = [
            c.make_set_command(
                brightness=b,
                transition=t,
            )
            for c, b, t in updates
        ]
        self.controller.execute_commands(commands)
        for command in commands:
            command.channel.brightness = command.params['brightness']

    @property
    def relay_pattern(self) -> str:
        """Return the active light pattern."""
        return self._relay_pattern
    
    @relay_pattern.setter
    def relay_pattern(self, value) -> None:
        """Update the active light pattern."""
        self._relay_pattern = value

    def click(self) -> None:
        """Click the specified otherwise unused light relays."""
        extra = ''.join(
            ('0' if e == '1' else '1')
            if i + self.light_count in self.click_relays else e
            for i, e in enumerate(self.extra_pattern)
        )
        self.set_relays(
            light_pattern=self.relay_pattern, 
            extra_pattern=extra,
        )

