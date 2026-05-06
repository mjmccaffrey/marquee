"""Marquee Lighted Sign Project - basemode"""

from abc import ABC
from dataclasses import dataclass, astuple
import logging

from devices.deviceset import DeviceSet
from devices.specialparams import SpecialParams
from .basemode import BaseMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ForegroundMode(BaseMode, ABC):
    """Base for all Playing and Select modes."""
    devices: DeviceSet
    speed_factor: float
    special: SpecialParams | None = None

    def __post_init__(self):
        """"""
        (   self.buttons, self.drums, self.lights, self.aux,
            self.clicker, self.ringer, self.joystick,
        ) = self.devices.astuple()

