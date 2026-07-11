"""Marquee Lighted Sign Project - mode"""

from abc import ABC
from dataclasses import dataclass
import logging
import pygame

from devices.deviceset import DeviceSet
from devices.specialparams import SpecialParams
from .basemode import BaseMode
from instruments.combinedlightset import CombinedLightSet
from instruments.lightsetinterface import LightSetInterface

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
        (   self.buttons, self.drums, self.lights, self.extra,
            self.clicker, self.ringer, self.joystick,
        ) = self.devices.astuple()
        self.combined: LightSetInterface
        if self.extra is not None:
            self.primary = self.lights
            self.secondary = self.extra
            self.combined = CombinedLightSet(self.lights, self.extra)

