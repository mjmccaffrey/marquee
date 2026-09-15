"""Marquee Lighted Sign Project - performancemode"""

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing_extensions import override

from .mode import Mode
from schemas import APICommand, DeviceName, ModeIndex


log = logging.getLogger('marquee.' + __name__)


@dataclass
class PerformanceMode(Mode, ABC):
    """Base for performance modes."""

    @override
    def control_action(self, control: DeviceName) -> None:
        """Respond to button being pressed.
           Return index of new mode, if any."""
        new_mode = None
        b = DeviceName
        match control:
            case b.BUTTON_REAR:
                new_mode = ModeIndex.MODE_SELECT
            # case b.REMOTE_C:
            #     self.clicker.click()
            #     new_mode = ModeIndex.BRIGHTNESS_SELECT
            case DeviceName.BUTTON_CORDED_A:
                self.clicker.play()
                new_mode = self._wrap_mode_index(-1)
            case DeviceName.BUTTON_CORDED_B:
                self.clicker.play()
                new_mode = self._wrap_mode_index(+1)
            case _:
                pass
        if new_mode is not None:
            self.change_mode(new_mode)

    def _wrap_mode_index(self, delta: int) -> int:
        """"""
        return self.wrap_value(
            lower=1, 
            upper=max(self.player.modes), 
            current=self.index,
            delta=delta,
        )

