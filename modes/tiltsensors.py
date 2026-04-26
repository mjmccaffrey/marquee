"""Marquee Lighted Sign Project - tiltsensors"""

from dataclasses import dataclass
import logging
from typing import override

from light_defs import LIGHT_COUNT, LIGHTS_BY_COLUMN
from devices.devices_misc import ButtonName
from devices.color import Colors
from .performancemode import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class TiltSensors(PerformanceMode):
    """"""

    def __post_init__(self) -> None:
        self.shift = 1
        self.lights.set_channels(on=False)
        self.lights.set_channels(color=Colors.WHITE)
    
    @override
    def button_action(self, button: ButtonName) -> int | None:
        """"""
        direction_buttons = {
            ButtonName.CORDED_A: +1,
            ButtonName.CORDED_B: -1,
        }
        if button in direction_buttons:
            shift = self.shift + direction_buttons[button]
            if -5 >= shift >= 5:
                self.shift = shift
                self.execute()
        else:
            return super().button_action(button)

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

    @override
    def execute(self):
        """"""
        self.lights.set_channels(on=self.on_parameter(self.shift))

