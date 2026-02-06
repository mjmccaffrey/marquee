"""Marquee Lighted Sign Project - devices_misc"""

from dataclasses import dataclass
from typing import Protocol

from instruments import BellSet, DrumSet
from lightset import ClickSet, LightSet


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

    def button_pressed(self, held: bool = False) -> None:
        """Callback for button press."""
        ...

    def virtual_button_pressed(self, signal_number, stack_frame) -> None:
        """Callback for virtual button press."""
        ...


@dataclass
class ButtonSet:
    """Every button."""
    body_back: ButtonInterface
    remote_a: ButtonInterface
    remote_b: ButtonInterface
    remote_c: ButtonInterface
    remote_d: ButtonInterface


class SetupDevices(Protocol):
    """"""
    def __call__(
        self,
        brightness_factor: float,
        speed_factor: float,
     ) -> tuple[BellSet, ButtonSet, DrumSet, LightSet, LightSet, ClickSet]:
        ...

