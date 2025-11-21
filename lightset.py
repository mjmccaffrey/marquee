"""Marquee Lighted Sign Project - lightset"""

# THIS SHOULD BE THE SOLE INTERFACE FOR THE APPLICATION,
# PARTICULARLY FOR METHODS

from collections.abc import Sequence
from dataclasses import dataclass, InitVar
from typing import Any

from bulb import SmartBulb
from lightcontroller import (
    ChannelUpdate, Color, LightController, LightChannel,
)
from relays import RelayModule
from specialparams import ChannelParams, MirrorParams, SpecialParams


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
        self.channels = self.controller.channels
        self.trans_def = self.controller.trans_def
        self.trans_min = self.controller.trans_min
        self.trans_max = self.controller.trans_max
        self.bulb_adjustents = self.controller.bulb_model.adjustments

        assert len(self.channels) == self.light_count
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

    def brightnesses(self) -> list[int]:
        """Return each channel's brightness."""
        return [
            channel.brightness
            for channel in self.channels
        ]


    def _set_channels_instead_of_relays(
            self,
            light_pattern: list | str, 
            special: ChannelParams,
    ) -> None:
        """Set channels per the specified pattern and special.
           Adjust for brightness_factor."""
        bright_values: dict[int, int] = {
            0: int(special.brightness_off * self._brightness_factor), 
            1: int(special.brightness_on * self._brightness_factor),
        }
        trans_values: dict[int, float] = {
            0: max(self.trans_min, 
                   special.trans_off * special.speed_factor), 
            1: max(self.trans_min, 
                   special.trans_on * special.speed_factor),
        }
        color_values: dict[int, Color | None] = {
            0: special.color_off,
            1: special.color_on,
        }
        light_pattern = [int(p) for p in light_pattern]
        brightnesses = tuple(
            bright_values[p]
            for p in light_pattern
        )
        trans = tuple(
            trans_values[p]
            for p in light_pattern
        )
        colors = tuple(
            color_values[p]
            for p in light_pattern
        )
        self.set_channels(
            brightnesses=brightnesses, 
            transitions=trans,
            colors=colors,
            on=True,
        )
            
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
        if isinstance(special, ChannelParams):
            self._set_channels_instead_of_relays(light_pattern, special)
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

    def set_channels_from_pattern(
            self, 
            pattern: str,
    ):
        """Set the channels per the supplied pattern and trans times.
           Apply bulb_adjustments.  Adjust for brightness_factor."""
        assert len(pattern) == self.light_count
        updates = [
            ChannelUpdate(
                channel=c,
                brightness=self.controller.bulb_model.adjustments[p],
                trans=None,
                color=None,
                on=True,
            )
            for c, p in zip(self.channels, pattern)
        ]

    def set_channels(
            self, 
            brightnesses: Sequence[int | None] | int | None = None,
            transitions: Sequence[float | None] | float | None = None,
            colors: Sequence[Color | None] | Color | None = None,
            on: Sequence[bool | None] | bool | None = None,
            channel_indexes: Sequence[int] | None = None,
            force_update: bool = False,
        ) -> None:
        """Set the channels per the supplied brightnesses, 
           trans times and colors.  
           Specify a subset of channels via channel_indexes.
           Force all specified channels to update with force_update.
           Adjust for brightness_factor."""
        
        def normalize(param: Any) -> list[Any]:
            """"""
            match param:
                case list():
                    assert len(param) == self.light_count
                    _param = param
                case _:
                    _param = [param] * self.light_count
            return _param
        
        _channel_indexes = (
            [i for i in range(self.light_count)]
                if channel_indexes is None else
            channel_indexes
        )
        _channels = [self.channels[i] for i in _channel_indexes]
        _brightnesses = normalize(brightnesses)
        if _brightnesses[0] is not None:
            _brightnesses = [
                int(b * self._brightness_factor)
                for b in _brightnesses
            ]
        _transitions = normalize(transitions)
        _colors = normalize(colors)
        _ons = normalize(on)
        updates = [
            ChannelUpdate(
                channel=ch,
                brightness=br,
                trans=tr,
                color=co,
                on=on,
            )
            for ch, br, tr, co, on in zip(
                _channels, _brightnesses, _transitions, _colors, _ons,
            )
        ]
        self.controller.update_channels(updates, force_update)

    def set_channel(
        self,
        channel: LightChannel,
        brightness: int | None = None,
        transition: float | None = None,
        color: Color | None = None,
        on: bool | None = None,
    ) -> None:
        """"""
        self.controller.set_channel(
            channel, brightness, transition, color, on,
        )

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

