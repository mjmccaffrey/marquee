"""Marquee Lighted Sign Project - performancemode"""

from abc import ABC
from dataclasses import dataclass

from .foregroundmode import ForegroundMode
from button import Button
from .mode_misc import ModeIndex
from player import Player


@dataclass
class PerformanceMode(ForegroundMode, ABC):
    """Base for performance modes."""

    def __post_init__(self) -> None:
        """Initialize."""
        self.direction = +1

    def button_action(self, button: Button) -> int | None:
        """Respond to button being pressed.
           Return index of new mode, if any."""
        new_mode = None
        b = self.buttons
        match button:
            case b.remote_a | b.body_back:
                new_mode = ModeIndex.SELECT_MODE
            case b.remote_c:
                self.lights.click()
                new_mode = ModeIndex.SELECT_BRIGHTNESS
            case b.remote_b:
                self.lights.click()
                new_mode = self.mode_index(self.index, -1)
            case b.remote_d:
                self.lights.click()
                new_mode = self.mode_index(self.index, +1)
            case _:
                raise ValueError("Unrecognized button.")
        return new_mode

