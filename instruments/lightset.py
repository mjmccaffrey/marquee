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
from devices.relaymodule import RelayClient
from devices.specialparams import ChannelParams, MirrorParams, SpecialParams
from .lightsetinterface import SavedState

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
        indices = (
            i for o in range(2) for i in range(12) if (i + o) % 2
        )
        self.update_order = {
            index: i for i, index in enumerate(indices)
        }
        # print(self.update_order)
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
        brightness: Sequence[int | None] | str | int | None = None,
        transition: Sequence[float | None] | float | None = None,
        color: Sequence[Color | None] | Color | None = None,
        on: Sequence[int | bool | str | None] | bool | int | None = None,
        index: Sequence[int] | int | None = None,
        force: bool = False,
    ) -> None:
        """Set the channels per the supplied brightnesses
           (adjusted by brightness_factor), 
           colors, and 'on's, with transition times.
           Specify a subset of channels via indices.
           If subset of channels specified, other parameters
           must each be a single value.
           Force all specified channels to update with force."""
        
        def channel_updates() -> list[ChannelUpdate]:
            """"""
            _channels = [self.channels[i] for i in _index]
            _brightness = self._convert_brightness(brightness, _index)
            _transition = self._convert_transition(transition, _index)
            _color = self._convert_color(color, _index)
            _on = self._convert_on(on, _index)
            assert (
                len(_channels) == 
                len(_brightness) ==
                len(_transition) ==
                len(_color) ==
                len(_on)
            )
            updates = [
                ChannelUpdate(ch, br, tr, co, on)
                for ch, br, tr, co, on in 
                zip(_channels, _brightness, _transition, _color, _on)
            ]
            updates.sort(key=lambda u: self.update_order[u.channel.index])
            print(' '.join(str(u.channel.index) for u in updates))
            return updates

        def no_params_are_sequences():
            """"""
            return (
                not isinstance(brightness, Sequence) and
                not isinstance(transition, Sequence) and
                not isinstance(color, Sequence) and
                not isinstance(on, Sequence)
            )

        # index is None => all lights, no other implications
        # no parameter sequences => group update possible

        _index = self._convert_index(index)
        updates = channel_updates()
        group = self.controller.groups.get(frozenset(_index))
        if group is not None and no_params_are_sequences():
            self.controller.update_channel_group(updates[0], group)
        else:
            self.controller.update_channels(updates, force)

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
        index: Sequence[int] | int | None,
    ) -> list[int]:
        """Return normalized index list.  If index is None, 
           return complete index list in scattered order."""
        match index:
            case Sequence():
                result = list(index)
            case None:
                result = list(range(self.count))
            case int():
                result = [index]
        return result
    
    def _convert_brightness(
        self,
        brightness: Sequence[int | None] | str | int | None,
        index: Sequence[int],
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
                result = [brightness] * len(index)
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
        index: Sequence[int],
    ) -> list[float | None]:
        """"""
        match transition:
            case Sequence():
                result = list(transition)
            case _:
                result = [transition] * len(index)
        return cast(list, result)
    
    def _convert_color(
        self,
        color: Sequence[Color | None] | Color | None,
        index: Sequence[int],
    ) -> list[Color | None]:
        """"""
        match color:
            case Sequence():
                result = list(color)
            case _:
                result = [color] * len(index)
        return result
    
    def _convert_on(
        self,
        on: Sequence[int | bool | str | None] | bool | int | None,
        index: Sequence[int],
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
                ] * len(index)
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
            "1" if p == "0" else "0" 
            for p in self.relays.device_pattern
        )
        self.relays.set_state_of_devices(pattern)

