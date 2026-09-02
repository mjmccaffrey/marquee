"""Marquee Lighted Sign Project - mode"""

from abc import ABC
from dataclasses import dataclass
import logging
import pygame
from typing import cast
from typing_extensions import override

from devices.controlset import ControlSet
from devices.device_schemas import ControlName, DeviceSet, DeviceName
from devices.joystick import Joystick
from devices.specialparams import SpecialParams
from .basemode import BaseMode
from instruments import (
    Buzzer, BellSet, Clicker, DrumSet, 
    LightSet, Ringer,
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
        self.controls = cast(ControlSet, self.devices[DeviceName.CONTROLS])
        self.lights = cast(LightSet, self.devices[DeviceName.LIGHTS])
        self.clicker = cast(Clicker, self.devices[DeviceName.CLICKER])
        self.bells: BellSet
        self.drums = cast(DrumSet, self.devices[DeviceName.DRUMS])
        self.buzzer = cast(Buzzer, self.devices[DeviceName.BUZZER])
        # self.joystick = cast(Joystick, self.devices[DeviceName.JOYSTICK])
        self.ringer = cast(Ringer, self.devices[DeviceName.RINGER])

    @override
    def close(self) -> None:
        """Stop any sounds and music. Assumption is that 
           no other mode instance is making sound or music."""
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        super().close()

    # @override
    # def control_action(self, control: ControlName) -> int | None:
    #     """"""
    #     if control == ControlName.ROTARY_A:
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

