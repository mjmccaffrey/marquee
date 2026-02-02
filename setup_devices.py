"""Marquee Lighted Sign Project - setup_devices"""

from typing import Protocol

from button_misc import ButtonSet
from instruments import BellSet, DrumSet
from lightset import ClickSet, LightSet


class SetupDevices(Protocol):
    """"""
    def __call__(
        self,
        brightness_factor: float,
        speed_factor: float,
     ) -> tuple[BellSet, ButtonSet, DrumSet, LightSet, LightSet, ClickSet]:
        ...

