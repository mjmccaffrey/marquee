"""Marquee Lighted Sign Project - alarm"""

from dataclasses import dataclass
import logging
from typing_extensions import override

from devices.color import Colors
from devices.devices_misc import ButtonName
from .backgroundmode import BackgroundMode
from .modes_misc import ModeDefinition
from .performancemode import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class AlarmBackground(BackgroundMode):
    """"""
    
    @override
    def execute(self) -> None:
        """"""
        # Nothing to do.

    @override
    def button_action(self, button: ButtonName) -> int | None:
        """"""
        if button == ButtonName.CORDED_A:
            self.create_mode_instance(
                mode_definition=ModeDefinition(
                    name='alarm_foreground',
                    cls=AlarmForeground,
                ),
                parent=self,
            ).execute()
        else:
            return super().button_action(button)


@dataclass(kw_only=True)
class AlarmForeground(PerformanceMode):
    """"""
    alarm_time = 0.5
    restore_time = 5.0
    total_time = alarm_time + restore_time

    @override
    def execute(self):
        """"""
        self.tasks.delay_all(self.total_time)
        self.state = self.lights.current_state()
        self.schedule(due=0.0, action=self.raise_alarm)
        self.schedule(due=self.alarm_time, action=self.restore_order)

    def raise_alarm(self):
        """Start ringing. Set lights."""
        self.ringer.play()
        self.lights.set_channels(
            brightness=100, 
            color=Colors.RED, 
            transition=self.alarm_time,
        )

    def restore_order(self):
        """Stop ringing. Restore lights."""
        self.ringer.rest()
        self.lights.restore_state(self.state, self.restore_time)

