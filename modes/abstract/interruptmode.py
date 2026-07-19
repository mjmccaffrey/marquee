"""Marquee Lighted Sign Project - alarm"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import pygame

from .performancemode import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class InterruptMode(PerformanceMode, ABC):
    """"""
    activity_time: float  # Length of activity.
    restore_time: float  # Length of state restoration.

    @abstractmethod
    def execute_activity(self) -> None:
        """"""

    def execute_interrupt(self):
        """"""
        self.save_and_pause()
        self.schedule(self.execute_activity)
        self.schedule(self.restore_and_resume, self.activity_time)

    def save_and_pause(self):
        """"""
        self.tasks.delay_all(self.activity_time + self.restore_time)
        pygame.mixer.music.pause()
        self.state = self.lights.current_state()

    def restore_and_resume(self):
        """"""
        self.lights.restore_state(self.state, self.restore_time)
        pygame.mixer.music.unpause()

