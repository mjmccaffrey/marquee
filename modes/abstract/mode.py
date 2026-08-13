"""Marquee Lighted Sign Project - mode"""

from abc import ABC
from dataclasses import dataclass
import logging
import pygame
from typing_extensions import override

from devices.devices_misc import ControlName
from devices.deviceset import DeviceSet
from devices.specialparams import SpecialParams
from .basemode import BaseMode

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
        (   self.controls, self.drums, 
            self.lights, self.extra, self.combined,
            self.clicker, self.ringer, self.buzzer, 
            self.joystick,
        ) = self.devices.astuple()
        self.combined.channels = [
            channel
            for lightset in (self.lights, self.extra)
            for channel in lightset.channels
          ]  # Kludge.

    @override
    def close(self) -> None:
        """Stop any sounds and music. Assumption is that 
           no other mode instance is making sound or music."""
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        super().close()

    @override
    def control_action(self, control: ControlName) -> int | None:
        """"""
        if control == ControlName.ROTARY_A:
            self.change_brightness(self.controls.rotary_a.steps)
            self.lights.brightness_factor = 0
        return super().control_action(control)

    def change_brightness(self, factor: float) -> None:
        """"""
        original = [
            int(self.lights.brightness_factor / channel.brightness)
            for channel in self.lights.channels
        ]
        print(original)
        self.lights.brightness_factor = factor
        self.lights.set_channels(brightness=original)

