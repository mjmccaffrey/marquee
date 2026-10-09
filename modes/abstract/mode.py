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

    @override
    def close(self) -> None:
        """Stop any sounds and music. Assumption is that 
           no other mode instance is making sound or music."""
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        super().close()

    @override
    def command_action(self, command: APICommand) -> bool:
        """Respond to command."""
        match command:
            case APICommand.NEXT_ENTRY:
                return self.next_entry()
            case APICommand.PREVIOUS_ENTRY:
                return self.previous_entry()
            case APICommand.NEXT_MODE:
                return self.next_mode()
            case APICommand.PREVIOUS_MODE:
                return self.previous_mode()
            case _:
                raise ValueError(it)

    def next_entry(self) -> bool:
        """Change to the next entry."""
        print("NEXT ENTRY")
        return False

    def previous_entry(self) -> bool:
        """Change to the previous entry."""
        print("PREVIOUS ENTRY")
        return False
        
    def next_mode(self) -> bool:
        """Change to the next mode."""
        print("NEXT MODE")
        return False
        
    def previous_mode(self) -> bool:
        """Change to the previous mode."""
        print("PREVIOUS MODE")
        return False

