"""Marquee Lighted Sign Project - mode"""

from abc import ABC
from dataclasses import dataclass
import logging
import pygame
from typing import cast
from typing_extensions import override

from devices.deviceset import DeviceSet
from devices.specialparams import SpecialParams
from .basemode import BaseMode
from schemas import DeviceName


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
        self.lights = self.devices[DeviceName.LIGHTS.value]
        self.clicker = self.devices[DeviceName.CLICKER.value]
        # self.bells: BellSet
        self.drums = self.devices[DeviceName.DRUMS.value]
        self.buzzer = self.devices[DeviceName.BUZZER.value]
        self.ringer = self.devices[DeviceName.RINGER.value]

    @override
    def close(self) -> None:
        """Stop any sounds and music. Assumption is that 
           no other mode instance is making sound or music."""
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        super().close()

    # @override
    # def control_action(self, control: DeviceName) -> int | None:
    #     """"""
    #     if control == DeviceName.ROTARY_A:
    #         self.change_brightness(self.controls.rotary_a.steps)
    #         self.lights.brightness_factor = 0

    def change_brightness(self, factor: float) -> None:
        """"""
        original = [
            int(self.lights.brightness_factor / channel.brightness)
            for channel in self.lights.channels
        ]
        print(original)
        self.lights.brightness_factor = factor
        self.lights.set_channels(brightness=original)

