"""Marquee Lighted Sign Project - lightset"""

from collections.abc import Sequence
from dataclasses import dataclass, field, InitVar
from enum import IntEnum
import logging
import time
from typing import Any, cast, TYPE_CHECKING
from typing_extensions import override

from devices import rgbxy

from devices.color import Color, Colors, ColorSets, RGB
from devices.bulb import SmartBulb
from devices.lightcontroller import ChannelUpdate, LightChannel, LightController
from devices.relaymodule import RelayClient
from devices.device_schemas import DeviceName
from devices.specialparams import ChannelParams, MirrorParams, SpecialParams
from .lightsetinterface import SavedState
from .instruments_abstract import RelayInstrument

log = logging.getLogger('marquee.' + __name__)


@dataclass
class LightSet(RelayInstrument):
    """Supports all of the light-related devices."""
    count: int
    relays: RelayClient | None
    mirror: RelayClient | None
    controller_type: type[LightController]
    controller_kwargs: dict
    brightness_factor_init: InitVar[float]
    channel_enum: InitVar[type[IntEnum]]
    speed_factor: float
    device: DeviceName = DeviceName.LIGHTS

    if TYPE_CHECKING:
        def __getattr__(self, name: str) -> IntEnum: ...

    def __post_init__(
        self, 
        brightness_factor_init: float,
        channel_enum: type[IntEnum],
    ) -> None:
        """Initialize."""
        self._brightness_factor = brightness_factor_init
        for channel in channel_enum:
            setattr(self, channel.name, channel.value)
        self.smart_bulbs = issubclass(
            self.controller_type.bulb_comp, 
            SmartBulb,
        )
        indices = (
            i for o in range(2) for i in range(self.count) if (i + o) % 2
        )
        self.update_order = {
            index: i for i, index in enumerate(indices)
        }
        self.color_sets = ColorSets()
        self._init_relays()
        self._init_controller()

    def _init_relays(self):
        """Initialize relays, if they exist."""
        if self.relays is None: 
            return
        assert self.relays.count == self.count
        self.relay_pattern = self.relays.get_state_of_devices()
        print(f"{self.relay_pattern}")
        if self.smart_bulbs:
            if all(r == '1' for r in self.relay_pattern):
                log.info("***** Smart bulbs in use - light relays already ON. *****")
            else:
                log.info("***** Smart bulbs in use - setting light relays ON. *****")
                self.set_relays(True, smart_bulb_override=True)
                time.sleep(3.0)  # Enough time for controller to see all bulbs.

    def _init_controller(self):
        """Initialize controller."""
        self.controller = self.controller_type(**self.controller_kwargs)
        self.gamut = self.controller.bulb_model.gamut
        RGB.adjust_incomplete_colors(self.gamut or rgbxy.GamutC)
        self.colors = Colors(self.gamut or rgbxy.GamutC)
        assert len(self.controller.channels) == self.count
        self.channels = self.controller.channels
        self.trans_min = self.controller.trans_min
        self.bulb_adjustments = self.controller.bulb_model.adjustments

    @override
    def play(self) -> None:
        """Should never be called."""
        raise NotImplementedError

    def calibrate(self):
        """Calibrate lights, if supported by controller.
           If not supported, exception will bubble up
           to executor."""
        log.info("Calibrating channels")
        self.set_relays(True)
        self.set_channels(brightness=100, force=True)
        self.controller.calibrate()

    def set_channels(
        self, 
        *,
        brightness: Sequence[int | None] | str | int | None = None,
        color: Sequence[Color | None] | Color | None = None,
        on: Sequence[int | bool | str | None] | bool | int | None = None,
        transition: Sequence[float | None] | float | None = None,
        index: Sequence[int] | int = (),
        group: str = "",
        force: bool = False,
    ) -> None:
        """Set the channels per the supplied brightnesses
           (adjusted by brightness_factor), 
           colors, and "on"s, with transition times.
           Specify a subset of channels via index.
           Force all specified channels to update 
           (ignore tracked state) with force.
           Specifying group forces that channel group 
           to be used, ignoring index."""           
        
        _index = self._convert_index(index)
        _group = self._determine_group(
            brightness, transition, color, on, group, _index
        )
        updates = self._channel_updates(
            brightness, transition, color, on, 
            [self.channels[i] for i in _index],
        )
        if _group is not None:
            self.controller.update_channel_group(updates, _group, force)
        else:
            self.controller.update_channels(updates, force)

    def _channel_updates(
        self, brightness, transition, color, on,
        channels: Sequence[LightChannel],
    ) -> list[ChannelUpdate]:
        """Return ChannelUpdate for each specified channel."""
        length = len(channels)
        _brightness = self._convert_brightness(brightness, length)
        _transition = self._convert_transition(transition, length)
        _color = self._convert_color(color, length)
        _on = self._convert_on(on, length)
        updates = [
            ChannelUpdate(ch, br, tr, co, on)
            for ch, br, tr, co, on in 
            zip(channels, _brightness, _transition, _color, _on)
        ]
        updates.sort(key=lambda u: self.update_order[u.channel.index])
        return updates

    def _determine_group(
        self, brightness, transition, color, on, group, index,
    ) -> str:
        """Return specified group, group that matches
            the specified indices, or None."""
        # print()
        # print(f"! {time.time()} {brightness=} {transition=} {color=} {on=} {group=} {index=}")
        if group:
            print("SPECIFIED GROUP: ", group)
            return group
        derived = self.controller.indices_in_group.get(frozenset(index))
        if (
            derived is not None and
            not isinstance(brightness, Sequence) and
            not isinstance(transition, Sequence) and
            not isinstance(color, Sequence) and
            not isinstance(on, Sequence)
        ):
            # print(index)
            # print(self.controller.indices_in_group)
            # print("DERIVED GROUP: ", derived)
            return derived
        else:
            return ""

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
        print('RELAY PATTERN', lights)

        if isinstance(special, MirrorParams):
            assert self.mirror is not None
            # self.mirror.set_state_of_devices(lights)

        if isinstance(special, ChannelParams):
            self._set_channels_instead_of_relays(lights, special)
        else:
            assert self.relays is not None
            self.relays.set_state_of_devices(lights)
            self.relay_pattern = lights

    def update_channels(self, updates: Sequence['ChannelUpdate']):
        """Effect channel updates."""
        self.controller.update_channels(updates)

    def simplify_parameter(self, p: Any) -> Any:
        """"""
        if all(e == p[0] for e in p):
            return p[0]
        return p

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
            force=True,
            brightness=self.simplify_parameter(
                tuple(brightness_values[p] for p in light_pattern)
            ),
            transition=self.simplify_parameter(
                tuple(trans_values[p] for p in light_pattern)
            ),
            color=self.simplify_parameter(
                tuple(color_values[p] for p in light_pattern)
            ),
            on=self.simplify_parameter(
                tuple(on_values[p] for p in light_pattern)
            ),
        )
            
    def brightnesses(self) -> list[int]:
        """Return each channel's brightness state."""
        return [
            int(channel.brightness)
            for channel in self.channels
        ]

    def current_state(self) -> 'SavedState':
        """Return state of lights."""
        return (
            tuple(int(c.brightness) for c in self.channels),
            tuple(c.color for c in self.channels),
            tuple(c.on for c in self.channels),
        )

    def restore_state(self, state: 'SavedState', transition: float) -> None:
        """"""
        br, co, on = state
        self.set_channels(
            brightness=br,
            color=co,
            on=on,
            transition=transition,
        )

    @property
    def brightness_factor(self) -> float:
        """Return brightness_factor."""
        return self._brightness_factor
    
    @brightness_factor.setter
    def brightness_factor(self, value) -> None:
        """Set brightness_factor. Lights not adjusted."""
        assert 0 <= value <= 1.0
        self._brightness_factor = value
        log.info(f"Brightness factor is now {self._brightness_factor}")

    def _convert_index(
        self,
        index: Sequence[int] | int,
    ) -> list[int]:
        """Return normalized index list.  If index is None, 
           return complete index list in scattered order."""
        print(index)
        print(type(index))
        match index:
            case tuple() if not index:
                result = list(range(self.count))
            case Sequence():
                result = list(index)
            case None:
                result = list(range(self.count))
            case int():
                result = [index]
            case _:
                raise ValueError(index)
        assert all(i in range(self.count) for i in result)
        return result
    
    def _convert_brightness(
        self,
        brightness: Sequence[int | None] | str | int | None,
        length: int,
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
                result = [brightness] * length
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
        length: int,
    ) -> list[float | None]:
        """"""
        match transition:
            case Sequence():
                result = list(transition)
            case _:
                result = [transition] * length
        return cast(list, result)
    
    def _convert_color(
        self,
        color: Sequence[Color | None] | Color | None,
        length: int,
    ) -> list[Color | None]:
        """"""
        match color:
            case Sequence():
                result = list(color)
            case _:
                result = [color] * length
        return result
    
    def _convert_on(
        self,
        on: Sequence[int | bool | str | None] | bool | int | None,
        length: int,
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
                ] * length
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

