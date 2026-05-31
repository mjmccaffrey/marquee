"""Marquee Lighted Sign Project - lightsetinterface"""

from collections.abc import Sequence
from typing import Protocol

from devices.color import Color
from devices.lightcontroller import ChannelUpdate
from devices.specialparams import SpecialParams


class LightSetInterface(Protocol):
    """"""
    count: int
    speed_factor: float

    def calibrate(self): ...

    def set_channels(
        self, 
        brightness: Sequence[int | None] | str | int | None = None,
        transition: Sequence[float | None] | float | None = None,
        color: Sequence[Color | None] | Color | None = None,
        on: Sequence[int | bool | str | None] | bool | int | None = None,
        indices: set[int] | None = None,
        force: bool = False,
    ) -> None: ...

    def set_relays(
        self, 
        light_pattern: str | Sequence[int | bool] | bool | int | None,
        special: SpecialParams | None = None,
        smart_bulb_override: bool = False,
    ) -> None: ...

    def update_channels(self, updates: Sequence['ChannelUpdate']): ...

    def brightnesses(self) -> list[int]: ...

    def current_state(self) -> 'SavedState': ...

    def restore_state(self, state: 'SavedState', transition: float) -> None: ...

    @property
    def brightness_factor(self) -> float: ...
    
    @brightness_factor.setter
    def brightness_factor(self, value) -> None: ...


SavedState = tuple[tuple[int, ...], tuple[Color | None, ...], tuple[bool, ...]]

