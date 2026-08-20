"""Marquee Lighted Sign Project - mode"""

from abc import ABC
from dataclasses import dataclass
import logging
import pygame

from devices.devices_misc import DeviceSet, Device
from devices.joystick import Joystick
from devices.specialparams import SpecialParams
from .basemode import BaseMode
from instruments import (
    Buzzer, BellSet, ClickSet, DrumSet, 
    LightSet, LightSetInterface, Ringer,
)

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class Mode(BaseMode, ABC):
    """Base for all Playing and Select modes."""
    background: bool = False
    devices: DeviceSet
    speed_factor: float
    special: SpecialParams | None = None

    def __post_init__(self):
        """"""
        pygame.mixer.init()
        # Assign critical devices
        self.buttons = self.devices[Device.CONTROLS]
        self.lights: LightSet = self.devices[Device.LIGHTS]
        self.extra: LightSet = self.devices[Device.EXTRA]
        self.combined: LightSet = self.devices[Device.COMBINED]
        self.clicker: ClickSet = self.devices[Device.CLICKER]
        # Not assigned: bells, drums, ringer, buzzer, joystick, tilts
        self.bells: BellSet
        self.drums: DrumSet
        self.buzzer: Buzzer
        self.joystick: Joystick
        self.ringer: Ringer

