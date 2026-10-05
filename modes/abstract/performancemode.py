"""Marquee Lighted Sign Project - performancemode"""

from abc import ABC
from dataclasses import dataclass
import logging
from typing_extensions import override

from .mode import Mode
from schemas import ControlName, DeviceName, ModeIndex


log = logging.getLogger('marquee.' + __name__)


@dataclass
class PerformanceMode(Mode, ABC):
    """Base for performance modes."""

    @override
    def control_action(self, control: ControlName) -> bool:
        """Respond to control action and return True."""
        b = DeviceName
        match control:
            case b.BUTTON_REAR:
                self.change_mode(ModeIndex.MODE_SELECT)
                return True
            # case b.REMOTE_C:
            #     self.clicker.click()
            #     new_mode = ModeIndex.BRIGHTNESS_SELECT
            case ControlName.BUTTON_CORDED_A:
                self.clicker.play()
                self.previous_mode()
                return True
            case ControlName.BUTTON_CORDED_B:
                self.clicker.play()
                self.next_mode()
                return True
            case _:
                return False

    @override
    def next_mode(self) -> bool:
        self.change_mode(self._wrap_mode_index(+1))
        return True
    
    @override
    def previous_mode(self) -> bool:
        self.change_mode(self._wrap_mode_index(-1))
        return True

