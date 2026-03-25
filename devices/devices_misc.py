"""Marquee Lighted Sign Project - devices_misc"""

from dataclasses import dataclass
from typing import Protocol

from instruments import BellSet, DrumSet
from lightset import ClickSet, LightSet


@dataclass
class ButtonPressed(Exception):
    """Button pressed base exception."""
    button: 'ButtonInterface'
    held: bool

class PhysicalButtonPressed(ButtonPressed):
    """Physical button pressed exception."""

class ButtonVirtuallyPressed(ButtonPressed):
    """Virtual button pressed (IPC signal received) exception."""


class ButtonInterface(Protocol):
    """Button interface."""

    @classmethod
    def reset(cls) -> None:
        """Prepare for a button press."""
        ...

    @classmethod
    def wait(cls, seconds: float | None) -> None:
        """Wait until seconds have elapsed or any button is pressed."""
        ...
    
    def close(self) -> None:
        """Clean up."""
        ...

    def button_physically_pressed(self, held: bool = False) -> None:
        """Callback for button press."""
        ...

    def button_virtually_pressed(self, signal_number, stack_frame) -> None:
        """Callback for virtual button press."""
        ...


class SetupDevices(Protocol):
    """"""
    def __call__(
        self,
        brightness_factor: float,
        speed_factor: float,
     ) -> tuple[BellSet, ButtonSet, DrumSet, LightSet, LightSet, ClickSet]:
        ...

