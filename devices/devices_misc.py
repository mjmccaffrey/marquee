"""Marquee Lighted Sign Project - devices_misc"""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ButtonPressed(Exception):
    """Button pressed base exception."""
    button: 'ButtonInterface'
    held: bool

class ButtonPhysicallyPressed(ButtonPressed):
    """Physical button pressed exception."""

class ButtonVirtuallyPressed(ButtonPressed):
    """Virtual button pressed (IPC signal received) exception."""


class ButtonInterface(Protocol):
    """Button interface."""

    def button_physically_pressed(self, held: bool = False) -> None:
        """Callback for button press."""
        ...

    def button_virtually_pressed(self, signal_number, stack_frame) -> None:
        """Callback for virtual button press."""
        ...

    def close(self) -> None:
        """Clean up."""
        ...


class ButtonInSetPressed(Protocol):
    """"""
    def __call__(
        self,
        button: ButtonInterface, 
        held: bool,
    ) -> None:
        ...

