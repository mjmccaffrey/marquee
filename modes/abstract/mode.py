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
from schemas import APICommand, DeviceName


log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class Mode(BaseMode, ABC):
    """Base for all Playing and Select modes."""
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

    def change_brightness(self, factor: float) -> None:
        """"""
        original = [
            int(self.lights.brightness_factor / channel.brightness)
            for channel in self.lights.channels
        ]
        print(original)
        self.lights.brightness_factor = factor
        self.lights.set_channels(brightness=original)

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
    #     if control == DeviceName.ROTARY_A:
    #         self.change_brightness(self.controls.rotary_a.steps)
    #         self.lights.brightness_factor = 0

    @override
    def command_action(self, command: APICommand) -> None:
        """Respond to command."""
        match command:
            case APICommand.NEXT_ENTRY:
                self.next_entry()
            case APICommand.PREVIOUS_ENTRY:
                self.previous_entry()
            case APICommand.NEXT_MODE:
                self.next_mode()
            case APICommand.PREVIOUS_MODE:
                self.previous_mode()
            case _:
                raise ValueError(it)

    def next_entry(self) -> None:
        """Change to the next entry."""
        print("NEXT ENTRY")

    def previous_entry(self) -> None:
        """Change to the previous entry."""
        print("PREVIOUS ENTRY")
        
    def next_mode(self) -> None:
        """Change to the next mode."""
        print("NEXT MODE")
        
    def previous_mode(self) -> None:
        """Change to the previous mode."""
        print("PREVIOUS MODE")

