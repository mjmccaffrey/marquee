"""Marquee Lighted Sign Project - performancemode"""

from abc import ABC
from dataclasses import dataclass
import logging
from typing import override

from devices.devices_misc import ButtonName
from .foregroundmode import ForegroundMode
from .modes_misc import ModeIndex

log = logging.getLogger('marquee.' + __name__)


@dataclass
class PerformanceMode(ForegroundMode, ABC):
    """Base for performance modes."""

    @override
    def button_action(self, button: ButtonName) -> int | None:
        """Respond to button being pressed.
           Return index of new mode, if any."""
        new_mode = None
        b = ButtonName
        match button:
            case b.REMOTE_A | b.BODY_BACK:
                new_mode = ModeIndex.MODE_SELECT
            case b.REMOTE_C:
                self.clicker.click()
                new_mode = ModeIndex.BRIGHTNESS_SELECT
            case b.REMOTE_B:
                self.clicker.click()
                new_mode = self.wrap_mode_index(-1)
            case b.REMOTE_D:
                self.clicker.click()
                new_mode = self.wrap_mode_index(+1)
            case b.CORDED_A | b.CORDED_B | b.GAME_START:
                pass
        return new_mode

    def wrap_mode_index(self, delta: int) -> int:
        """"""
        return self.wrap_value(
            lower=1, 
            upper=max(self.modes), 
            current=self.index,
            delta=delta,
        )

