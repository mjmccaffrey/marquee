"""Marquee Lighted Sign Project - alarm"""

from dataclasses import dataclass
import logging
import pygame
from typing_extensions import override

from devices.color import Colors
from devices.devices_misc import Control
from .abstract.interruptmode import InterruptMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class AlarmBell(InterruptMode):
    """"""
    background: bool = True
    activity_time: float = 0.5
    restore_time: float = 5.0
    total_time: float = activity_time + restore_time

    @override
    def control_action(self, control: Control) -> int | None:
        """"""
        if control == Control.CORDED_B:
            self.schedule()
        else:
            return super().control_action(control)

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
            force=True,
        )

    def quell_alarm(self):
        """Stop ringing."""
        self.ringer.rest()


@dataclass(kw_only=True)
class AlarmDive(InterruptMode):
    """"""
    background: bool = True
    activity_time: float = 3.0
    restore_time: float = 4.0

    @override
    def control_action(self, control: Control) -> int | None:
        """"""
        if control == Control.CORDED_B:
            self.schedule(self.execute_interrupt)
        else:
            return super().control_action(control)

    @override
    def execute_activity(self):
        """"""
        self.lights.set_channels(
            brightness=100, 
            color=Colors.RED, 
            on=True,
            transition=0.0,
            force=True,
        )
        dive = pygame.mixer.Sound('modes/alarm.ogg')
        dive.play()

