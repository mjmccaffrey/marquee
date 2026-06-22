"""Marquee Lighted Sign Project - alarm"""

from dataclasses import dataclass
import logging
import pygame
from typing_extensions import override

from devices.color import Colors
from devices.devices_misc import ButtonName
from .abstract.backgroundmode import BackgroundMode
from . import ModeDefinition
from .abstract.interruptionmode import InterruptionMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class AlarmBackground(BackgroundMode):
    """"""
    bell: bool
    
    @override
    def button_action(self, button: ButtonName) -> int | None:
        """"""
        if button == ButtonName.CORDED_C:
            self.schedule(action=self.execute_alarm)
        else:
            return super().button_action(button)

    @override
    def execute(self) -> None:
        """"""

    def execute_alarm(self) -> None:
        """"""
        self.create_mode_instance(
            mode_definition=ModeDefinition(
                name='alarm_foreground',
                cls=AlarmBell if self.bell else AlarmDive,
            ),
            parent=self,
        ).execute()
    

@dataclass(kw_only=True)
class AlarmBell(InterruptionMode):
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
        print("***RING***")
        # self.ringer.play()
        self.lights.set_channels(
            brightness=100, 
            color=Colors.RED, 
            on=True,
            transition=self.activity_time,
        )

    def quell_alarm(self):
        """Stop ringing."""
        self.ringer.rest()


@dataclass(kw_only=True)
class AlarmDive(InterruptionMode):
    """"""
    activity_time: float = 0.5
    restore_time: float = 4.0
    total_time: float = activity_time + restore_time

    @override
    def execute_activity(self):
        """"""
        self.lights.set_channels(
            brightness=100, 
            color=Colors.RED, 
            on=True,
            transition=0.0,
        )
        dive = pygame.mixer.Sound('modes/alarm.ogg')
        dive.play()

