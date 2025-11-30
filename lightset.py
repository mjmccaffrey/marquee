"""Marquee Lighted Sign Project - lightset"""

# THIS SHOULD BE THE SOLE INTERFACE FOR THE APPLICATION,
# PARTICULARLY FOR METHODS

from collections.abc import Sequence
from dataclasses import dataclass, InitVar

from bulb import SmartBulb
from color import Color
from lightcontroller import (
    ChannelUpdate, LightController, LightChannel,
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
        self.trans_min = self.controller.trans_min
        self.trans_max = self.controller.trans_max
        self.bulb_adjustents = self.controller.bulb_model.adjustments

        assert len(self.channels) == self.light_count
        full_pattern = self.relays.get_state_of_devices()
        self.relay_pattern = full_pattern[:self.light_count]
        self.extra_pattern = full_pattern[self.light_count:]
        self.brightness_factor = brightness_factor_init

        if isinstance(self.controller.bulb_comp, SmartBulb):
            self.set_relays(light_pattern=True, smart_bulb_override=True)
            print("***** Smart bulbs in use - light relays preset to ON. *****")
        else:
            print("***** Standard bulbs in use. *****")  

    @property
    def brightness_factor(self) -> float:
        return self._brightness_factor
    
    @brightness_factor.setter
    def brightness_factor(self, value) -> None:
        self._brightness_factor = value
        print("Brightness factor is ", self._brightness_factor)

    def brightnesses(self) -> list[int | float]:
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
        _brightness = tuple(
            bright_values[p]
            for p in light_pattern
        )
        _transitions = tuple(
            trans_values[p]
            for p in light_pattern
        )
        _colors = tuple(
            color_values[p]
            for p in light_pattern
        )
        self.set_channels(
            brightness=_brightness, 
            transition=_transitions,
            color=_colors,
            on=True,
        )
            
    def set_relays(
            self, 
            light_pattern: str | Sequence[int | bool] | bool | int,
            extra_pattern: str | Sequence[int | bool] | bool | int | None = None,
            special: SpecialParams | None = None,
            smart_bulb_override: bool = False,
        ) -> None:
        """Set all lights and extra relays per supplied patterns and special.
           Set light_pattern property, always as string
           rather than list."""
        _light = self.convert_relay(light_pattern)
        _extra = self.convert_relay(extra_pattern)
        if _extra is None:
            _extra = self.extra_pattern
        assert isinstance(_light, str)  # I do not understand
        assert isinstance(_extra, str)  # why these are necessary.
        if isinstance(special, ChannelParams):
            self._set_channels_instead_of_relays(_light, special)
            return
        _full = _light + _extra
        if (
            _light != self.relay_pattern and
            isinstance(self.controller.bulb_comp, SmartBulb) and 
            not smart_bulb_override
        ):
            raise TypeError(
                "Light relay change request refused - smart bulbs in use."
            )
        self.relays.set_state_of_devices(_full)
        if isinstance(special, MirrorParams):
            special.func(_full)
        self.extra_pattern = _extra
        self.relay_pattern = _light

    def set_channels(
            self, 
            brightness: Sequence[int | None] | str | int | None = None,
            transition: Sequence[float | None] | float | None = None,
            color: Sequence[Color | None] | Color | None = None,
            on: Sequence[int | bool | str | None] | bool | int | None = None,
            channel_indexes: Sequence[int] | None = None,
            force: bool = False,
        ) -> None:
        """Set the channels per the supplied brightness, 
           trans times and colors.  
           Specify a subset of channels via channel_indexes.
           Force all specified channels to update with force.
           Adjust for brightness_factor."""
        
        _channel_indexes = (
            [i for i in range(self.light_count)]
                if channel_indexes is None else
            channel_indexes
        )
        _channels = [self.channels[i] for i in _channel_indexes]
        _brightnesses = self.convert_brightness(brightness)
        _transitions = self.convert_transition(transition)
        _colors = self.convert_color(color)
        _on = self.convert_on(on)
        updates = [
            ChannelUpdate(
                channel=ch,
                brightness=br,
                trans=tr,
                color=co,
                on=on,
            )
            for ch, br, tr, co, on in zip(
                _channels, _brightnesses, _transitions, _colors, _on,
            )
        ]
        self.controller.update_channels(updates, force)

    def set_channel(
        self,
        channel: LightChannel,
        brightness: int | None = None,
        transition: float | None = None,
        color: Color | None = None,
        on: bool | None = None,
    ) -> None:
        """"""
        channel._set(brightness, transition, color, on)

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

    def convert_brightness(
        self,
        brightness: Sequence[int | None] | str | int | None,
    ) -> list[int | None]:
        """"""
        match brightness:
            case str():
                result = [
                    self.controller.bulb_model.adjustments[b]
                    for b in brightness
                ]
            case Sequence():
                result = list(brightness)
            case _:
                result = [brightness] * self.light_count

        result = [
            int(b * self._brightness_factor)
            if b is not None else None
            for b in result
        ]
        return result  # type: ignore
    
    def convert_transition(
        self,
        transition: Sequence[float | None] | float | None,
    ) -> list[float | None]:
        """"""
        match transition:
            case Sequence():
                result = list(transition)
            case _:
                result = [transition] * self.light_count
        return result  # type: ignore
    
    def convert_color(
        self,
        color: Sequence[Color | None] | Color | None,
    ) -> list[Color | None]:
        """"""
        match color:
            case Sequence():
                result = list(color)
            case _:
                result = [color] * self.light_count
        return result
    
    def convert_on(
        self,
        on: Sequence[int | bool | str | None] | bool | int | None,
    ) -> list[bool | None]:
        """"""
        match on:
            case str():
                result = [
                    False if o == "0" else True
                    for o in on
                ]
            case Sequence():
                result = [
                    bool(o) if o is not None else None
                    for o in on
                ]
            case _:
                result = [
                    bool(on) if on is not None else None
                ] * self.light_count
        return result  # type: ignore
    
    def convert_relay(
        self, 
        pattern: str | Sequence[int | bool] | int | bool | None,
    ) -> str | None:
        """"""
        match pattern:
            case str():
                result = pattern
            case Sequence():
                result = ''.join("1" if e else "0" for e in pattern)
            case None:
                result = None
            case _:
                result = ("1" if pattern else "0") * self.light_count
        return result
    
