"""Marquee Lighted Sign Project - tiltsensors"""

from dataclasses import dataclass
import logging

from device_defs import LIGHT_COUNT, LIGHTS_BY_COLUMN
from devices.devices_misc import ButtonInterface
from devices.color import Colors
from .performancemode import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class TiltSensors(PerformanceMode):
    """"""

    def __post_init__(self) -> None:
        self.position = 1
        self.lights.set_channels(on=False)
        self.lights.set_channels(color=Colors.WHITE)
    
    def button_action(self, button: ButtonInterface) -> int | None:
        """"""
        if button == self.buttons.corded_a:
            self.entry_index = self.wrap_position(+1)
            self.execute()
        elif button == self.buttons.corded_b:
            self.entry_index = self.wrap_position(-1)
            self.execute()
        else:
            return super().button_action(button)

    def lights_on(self) -> tuple[bool, ...]:
        """"""
        on = set(i for c in LIGHTS_BY_COLUMN[:self.position] for i in c)
        return tuple(i in on for i in range(LIGHT_COUNT))

    def execute(self):
        """"""
        print(self.lights_on())
        self.lights.set_channels(on=self.lights_on())

    def wrap_position(self, delta: int):
        """"""
        return self.wrap_value(
            lower=0, 
            upper=len(LIGHTS_BY_COLUMN),
            current=self.position,
            delta=delta,
        )

