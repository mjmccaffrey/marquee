"""Marquee Lighted Sign Project - performancemode"""

from abc import ABC
from dataclasses import dataclass
import logging
from typing_extensions import override

from devices.device_schemas import ControlName
from .mode import Mode
from ..structural.mode_schemas import ModeIndex

log = logging.getLogger('marquee.' + __name__)


@dataclass
class PerformanceMode(Mode, ABC):
    """Base for performance modes."""

    @override
    def control_action(self, control: ControlName) -> int | None:
        """Respond to button being pressed.
           Return index of new mode, if any."""
        new_mode = None
        b = ControlName
        match control:
            case b.BODY_BACK:
                new_mode = ModeIndex.MODE_SELECT
            # case b.REMOTE_C:
            #     self.clicker.click()
            #     new_mode = ModeIndex.BRIGHTNESS_SELECT
            # case b.REMOTE_B:
            #     self.clicker.click()
            #     new_mode = self.wrap_mode_index(-1)
            # case b.REMOTE_D:
            #     self.clicker.click()
            #     new_mode = self.wrap_mode_index(+1)
            case _:
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

