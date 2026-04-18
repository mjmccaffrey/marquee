"""Marquee Lighted Sign Project - lightset"""

from collections.abc import Sequence
from dataclasses import dataclass, InitVar
import logging
import time
from typing import cast

from devices import rgbxy

from devices.color import Color, Colors, RGB
from devices.bulb import SmartBulb
from devices.lightcontroller import ChannelUpdate, LightController
from devices.relays import RelayClient
from devices.specialparams import ChannelParams, MirrorParams, SpecialParams

log = logging.getLogger('marquee.' + __name__)


@dataclass
class LightSet:
    """Supports all of the light-related devices."""
    count: int
    relays: RelayClient | None
    mirror: RelayClient | None
    controller_type: type[LightController]
    controller_kwargs: dict
    brightness_factor_init: InitVar[float]
    speed_factor: float

    def __post_init__(self, brightness_factor_init: float) -> None:
        """Initialize."""
        self._brightness_factor = brightness_factor_init
        self.smart_bulbs = issubclass(
            self.controller_type.bulb_comp, 
            SmartBulb,
        )
        self._init_relays()
        self._init_controller()

    def _init_relays(self):
        """Initialize relays, if they exist."""
        if self.relays is None: 
            return
        assert self.relays.count == self.count
        self.relay_pattern = self.relays.get_state_of_devices()
        if self.smart_bulbs:
            if all(r == '1' for r in self.relay_pattern):
                log.info("***** Smart bulbs in use - light relays already ON. *****")
            else:
                log.info("***** Smart bulbs in use - setting light relays ON. *****")
                self.set_relays(True, smart_bulb_override=True)
                time.sleep(5.0)  # Enough time for controller to see all bulbs.

    def _init_controller(self):
        """Initialize controller."""
        self.controller = self.controller_type(**self.controller_kwargs)
        self.gamut = self.controller.bulb_model.gamut
        RGB.adjust_incomplete_colors(self.gamut or rgbxy.GamutC)
        self.colors = Colors(self.gamut or rgbxy.GamutC)
        assert len(self.controller.channels) == self.count
        self.update_sequence = [i for i in range(self.count)]
        # log.info(self.update_sequence)
        self.channels = self.controller.channels
        self.trans_min = self.controller.trans_min
        self.bulb_adjustments = self.controller.bulb_model.adjustments

    def calibrate(self):
        """Calibrate lights, if supported by controller.
           If not supported, exception will bubble up
           to executor."""
        log.info("Calibrating channels")
        self.set_relays(True)
        self.set_channels(brightness=100, force=True)
        self.controller.calibrate()

    def brightnesses(self) -> list[int]:
        """Return each channel's brightness state."""
        return [
            int(channel.brightness)
            for channel in self.channels
        ]

    def set_relays(
            self, 
            light_pattern: str | Sequence[int | bool] | bool | int | None,
            special: SpecialParams | None = None,
            smart_bulb_override: bool = False,
        ) -> None:
        """Set all light relays, or channels,
           per supplied patterns and special."""
        
        if light_pattern is None:
            return  # No pattern given; nothing to do.
        if (
            self.smart_bulbs and 
            not smart_bulb_override and 
            special is None
        ):  # Ignore relay command unless special circumstances.
            return
        
        lights = self._convert_relay_pattern(light_pattern)

        if isinstance(special, MirrorParams):
            assert self.mirror is not None
            self.mirror.set_state_of_devices(lights)

        if isinstance(special, ChannelParams):
            self._set_channels_instead_of_relays(lights, special)
        else:
            assert self.relays is not None
            self.relays.set_state_of_devices(lights)
            self.relay_pattern = lights

    def set_channels(
            self, 
            brightness: Sequence[int | None] | str | int | None = None,
            transition: Sequence[float | None] | float | None = None,
            color: Sequence[Color | None] | Color | None = None,
            on: Sequence[int | bool | str | None] | bool | int | None = None,
            channel_indexes: set[int] | None = None,
            force: bool = False,
        ) -> None:
        """Set the channels per the supplied brightness, 
           transition times and colors. 
           Specify a subset of channels via channel_indexes.
           Force all specified channels to update with force.
           Adjust for brightness_factor."""
        
        def all_at_once_possible() -> bool:
            """Can the update be performed more-or-less all at once,
               rather than on each channel individually."""
            return (
                self.controller.all_at_once_supported and 
                (   channel_indexes is None or 
                    len(channel_indexes) == self.count
                ) and
                not isinstance(brightness, Sequence) and
                not isinstance(transition, Sequence) and
                not isinstance(color, Sequence) and
                not isinstance(on, Sequence)
            )
        
        if all_at_once_possible():
            self.controller.execute_update_all_at_once(
                ChannelUpdate(
                    channel=self.controller.channels[0],  # Dummy
                    brightness=self._convert_brightness(brightness)[0],
                    transition=self._convert_transition(transition)[0],
                    color=self._convert_color(color)[0],
                    on=self._convert_on(on)[0],
                )
            )
            return

        # Update each channel individually
        _channel_indexes = (
            self.update_sequence
                if channel_indexes is None else
            channel_indexes
        )
        _channels = [self.channels[i] for i in _channel_indexes]
        _brightnesses = self._convert_brightness(brightness)
        _transitions = self._convert_transition(transition)
        _colors = self._convert_color(color)
        _on = self._convert_on(on)
        updates = [
            ChannelUpdate(
                channel=ch,
                brightness=br,
                transition=tr,
                color=co,
                on=on,
            )
            for ch, br, tr, co, on in zip(
                _channels, _brightnesses, _transitions, _colors, _on,
            )
        ]
        self.controller.update_channels(updates, force)

    def update_channels(self, updates: Sequence['ChannelUpdate']):
        """Effect channel updates."""
        self.controller.update_channels(updates)

    def _set_channels_instead_of_relays(
            self,
            light_pattern: list | str, 
            special: ChannelParams,
    ) -> None:
        """Set channels per the specified pattern and special.
           Adjust for brightness_factor."""
        brightness_values: dict[int, int | None] = {
            0: (int(special.brightness_off * self._brightness_factor)
                if special.brightness_off is not None else None),
            1: (int(special.brightness_on * self._brightness_factor)
                if special.brightness_on is not None else None),
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
        on_values: dict[int, bool | None] = {
            0: special.on_off,
            1: special.on_on,
        }
        light_pattern = [int(p) for p in light_pattern]
        self.set_channels(
            brightness=tuple(brightness_values[p] for p in light_pattern), 
            transition=tuple(trans_values[p] for p in light_pattern),
            color=tuple(color_values[p] for p in light_pattern),
            on=tuple(on_values[p] for p in light_pattern),
        )
            
    @property
    def brightness_factor(self) -> float:
        return self._brightness_factor
    
    @brightness_factor.setter
    def brightness_factor(self, value) -> None:
        self._brightness_factor = value
        log.info(f"Brightness factor is now {self._brightness_factor}")

    @property
    def relay_pattern(self) -> str:
        """Return the active light pattern."""
        return self._relay_pattern
    
    @relay_pattern.setter
    def relay_pattern(self, value) -> None:
        """Update the active light pattern."""
        self._relay_pattern = value

    def _convert_brightness(
        self,
        brightness: Sequence[int | None] | str | int | None,
    ) -> list[int | None]:
        """Return normalized brightness pattern, 
           adjusted by brightness_factor."""
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
        # log.info(f"{result=} {self._brightness_factor=}")
        result = [
            int(b * self._brightness_factor)
            if b is not None else None
            for b in result
        ]
        return result
    
    def _convert_transition(
        self,
        transition: Sequence[float | None] | float | None,
    ) -> list[float | None]:
        """"""
        match transition:
            case Sequence():
                result = list(transition)
            case _:
                result = [transition] * self.count
        return cast(list, result)
    
    def _convert_color(
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
    
    def _convert_on(
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
        return cast(list, result)
    
    def _convert_relay_pattern(
        self, 
        pattern: str | Sequence[int | bool] | int | bool,
    ) -> str:
        """"""
        match pattern:
            case str():
                result = pattern
            case Sequence():
                result = ''.join("1" if e else "0" for e in pattern)
            # case None:
            #     result = None
            case _:
                result = ("1" if pattern else "0") * self.count
        return result


@dataclass
class ClickSet:
    """"""
    relays: RelayClient

    def click(self) -> None:
        """Click the otherwise unused light relays."""
        pattern = "".join(
            "1" if p == "0" else "0" for p in self.relays.device_pattern
        )
        self.relays.set_state_of_devices(pattern)

