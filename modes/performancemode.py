"""Marquee Lighted Sign Project - performancemode"""

from abc import ABC
from dataclasses import dataclass
import logging

from devices.devices_misc import ButtonInterface
from .foregroundmode import ForegroundMode
from .modes_misc import ModeIndex

log = logging.getLogger('marquee.' + __name__)


@dataclass
class PerformanceMode(ForegroundMode, ABC):
    """Base for performance modes."""

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        self.direction = +1

    def button_action(self, button: ButtonInterface) -> int | None:
        """Respond to button being pressed.
           Return index of new mode, if any."""
        new_mode = None
        b = self.buttons
        match button:
            case b.remote_a | b.body_back:
                new_mode = ModeIndex.MODE_SELECT
            case b.remote_c:
                self.clicker.click()
                new_mode = ModeIndex.BRIGHTNESS_SELECT
            case b.remote_b:
                self.clicker.click()
                new_mode = self.wrap_mode_index(-1)
            case b.remote_d:
                self.clicker.click()
                new_mode = self.wrap_mode_index(+1)
            case _:
                raise ValueError("Unrecognized button.")
        return new_mode

    def wrap_mode_index(self, delta: int) -> int:
        """"""
        return self.wrap_value(
            lower=1, 
            upper=max(self.modes), 
            current=self.index,
            delta=delta,
        )

