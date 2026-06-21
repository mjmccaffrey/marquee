"""Marquee Lighted Sign Project - alarm"""

from dataclasses import dataclass
import logging
from typing_extensions import override

from devices.color import Colors
from devices.devices_misc import ButtonName
from .abstract.backgroundmode import BackgroundMode
from .modes_misc import ModeDefinition
from .abstract.interruptionmode import InterruptionMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class AlarmBackground(BackgroundMode):
    """"""
    
    @override
    def execute(self) -> None:
        return
    
    @override
    def button_action(self, button: ButtonName) -> int | None:
        """"""
        if button == ButtonName.GAME_START:
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
class AlarmForeground(InterruptionMode):
    """"""
    activity_time: float = 0.5
    restore_time: float = 5.0
    total_time: float = activity_time + restore_time

    @override
    def execute_activity(self):
        """"""
        self.schedule(action=self.raise_alarm)
        self.schedule(action=self.quell_alarm, due=self.activity_time)

    def raise_alarm(self):
        """Start ringing. Set lights."""
        self.ringer.play()
        self.lights.set_channels(
            brightness=100, 
            color=Colors.RED, 
            transition=self.activity_time,
        )

    def quell_alarm(self):
        """Stop ringing."""
        self.ringer.rest()

