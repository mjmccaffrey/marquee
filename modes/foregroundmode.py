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
        self.buttons = self.devices.buttons
        self.drums = self.devices.drums
        self.lights = self.devices.lights
        self.aux = self.devices.aux
        self.clicker = self.devices.clicker
        self.ringer = self.devices.ringer
        self.joystick = self.devices.joystick

