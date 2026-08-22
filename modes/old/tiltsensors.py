"""Marquee Lighted Sign Project - tiltsensors"""

from dataclasses import dataclass
import logging
from typing_extensions import override

from light_defs import LIGHT_COUNT, LIGHTS_BY_COLUMN
from devices.devices_misc import Control
from devices.color import Colors
from . import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class TiltSensors(PerformanceMode):
    """"""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.shift = 1
        self.lights.set_channels(on=False)
        self.lights.set_channels(color=Colors.WHITE)
    
    def control_action(self, control: Control) -> int | None:
        """"""
        direction_buttons = {
            Control.CORDED_A: +1,
            Control.CORDED_B: -1,
        }
        if control in direction_buttons:
            shift = self.shift + direction_buttons[control]
            if -5 <= shift <= 5:
                self.shift = shift
                self.schedule(action=self.execute)
        else:
            return super().control_action(control)

    @staticmethod
    def on_parameter(shift: int) -> tuple[bool, ...]:
        """"""
        cols_on = (
            slice(shift, 5) 
                if shift >= 0 else 
            slice(0, 5 + shift)
        )
        lights_on = set(i for c in LIGHTS_BY_COLUMN[cols_on] for i in c)
        return tuple(i in lights_on for i in range(LIGHT_COUNT))

    def execute(self):
        """"""
        self.lights.set_channels(on=self.on_parameter(self.shift))

