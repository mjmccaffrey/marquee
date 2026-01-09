"""Marquee Lighted Sign Project - lightset"""

# THIS SHOULD BE THE SOLE INTERFACE FOR THE APPLICATION,
# PARTICULARLY FOR METHODS

from collections.abc import Sequence
from dataclasses import dataclass, InitVar
import time

import rgbxy

from bulb import SmartBulb
from color import Color, Colors
from lightcontroller import ChannelUpdate, LightController, LightChannel
from relays import RelayModule
from specialparams import EmulateParams, ChannelParams, MirrorParams, SpecialParams


@dataclass
class LightSet:
    """Supports all of the light-related devices."""
    relays: RelayModule
    light_relays: set[int]
    click_relays: set[int]
    controller_type: type[LightController]
    controller_kwargs: dict
    brightness_factor_init: InitVar[float]
    speed_factor: float

    def __post_init__(self, brightness_factor_init: float) -> None:
        """Initialize."""
        self._brightness_factor = brightness_factor_init
        self.count = len(self.light_relays)
        full_pattern = self.relays.get_state_of_devices()
        self.relay_pattern = full_pattern[:self.count]
        self.extra_pattern = full_pattern[self.count:]
        self.smart_bulbs = issubclass(
            self.controller_type.bulb_comp, 
            SmartBulb,
        )

        if self.smart_bulbs:
            print("***** Smart bulbs in use - setting light relays ON. *****")
            self.set_relays(light_pattern=True, smart_bulb_override=True)
            time.sleep(5.0)  # Enough time for controller to see all bulbs.

        self.controller = self.controller_type(**self.controller_kwargs)
        self.gamut = self.controller.bulb_model.gamut
        self.colors = Colors(self.gamut or rgbxy.GamutC)
        assert len(self.controller.channels) == self.count
        self.channels = self.controller.channels
        self.trans_min = self.controller.trans_min
        self.trans_max = self.controller.trans_max
        self.bulb_adjustents = self.controller.bulb_model.adjustments

    @property
    def brightness_factor(self) -> float:
        return self._brightness_factor
    
    @brightness_factor.setter
    def brightness_factor(self, value) -> None:
        self._brightness_factor = value
        print("Brightness factor is ", self._brightness_factor)

    def brightnesses(self) -> list[int]:
        """Return each channel's brightness state."""
        return [
            int(channel.brightness)
            for channel in self.channels
        ]

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
        assert isinstance(_light, str)
        _extra = self.convert_relay(extra_pattern)
        if _extra is None:
            _extra = self.extra_pattern

            
        if self.smart_bulbs and not smart_bulb_override:
            special = special or EmulateParams()
            
        if isinstance(special, ChannelParams):
            self._set_channels_instead_of_relays(_light, special)
            return

        # if (
        #     self.smart_bulbs and 
        #     not smart_bulb_override and 
        #     _light != self.relay_pattern
        # ):
        #     raise TypeError("Light relay change request refused.")
        
        self.relays.set_state_of_devices(_light + _extra)
        if isinstance(special, MirrorParams):
            special.func(_light + _extra)
        self.relay_pattern = _light
        self.extra_pattern = _extra

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
            [i for i in range(self.count)]
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
        """Build and send command via requests.
           Does not check current state."""
        channel._set(brightness, transition, color, on)

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
                   special.trans_off * self.speed_factor), 
            1: max(self.trans_min, 
                   special.trans_on * self.speed_factor),
        }
        color_values: dict[int, Color | None] = {
            0: special.color_off,
            1: special.color_on,
        }
        light_pattern = [int(p) for p in light_pattern]
        self.set_channels(
            brightness=tuple(bright_values[p] for p in light_pattern), 
            transition=tuple(trans_values[p] for p in light_pattern),
            color=tuple(color_values[p] for p in light_pattern),
            on=True,
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
            if i + self.count in self.click_relays else e
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
                result = [brightness] * self.count

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
                result = [transition] * self.count
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
                result = [color] * self.count
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
                ] * self.count
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
                result = ("1" if pattern else "0") * self.count
        return result
    
