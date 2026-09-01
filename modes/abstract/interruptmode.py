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

    def __post_init__(self):
        self.total_time = self.activity_time + self.restore_time
        super().__post_init__()
    
    @abstractmethod
    def execute_activity(self) -> None:
        """"""

    def execute_interrupt(self):
        """"""
        self.save_and_pause()
        self.schedule(self.execute_activity)
        self.schedule(self.restore, self.activity_time)
        self.schedule(self.resume, self.total_time)

    def save_and_pause(self):
        """"""
        self.player.tasks.delay_all(self.total_time)
        pygame.mixer.music.pause()
        self.state = self.lights.current_state()

    def restore(self):
        """"""
        self.lights.restore_state(self.state, self.restore_time)

    def resume(self):
        """"""
        pygame.mixer.music.unpause()

