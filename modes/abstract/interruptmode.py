"""Marquee Lighted Sign Project - alarm"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import pygame
from typing_extensions import override

from .performancemode import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class InterruptMode(PerformanceMode, ABC):
    """"""
    activity_time: float
    restore_time: float
    total_time: float

    @abstractmethod
    def execute_activity(self) -> None:
        """"""

    def execute_interrupt(self):
        """"""
        self.tasks.delay_all(self.total_time)
        pygame.mixer.music.pause()
        self.state = self.lights.current_state()
        self.execute_activity()
        self.lights.restore_state(self.state, self.restore_time)
        pygame.mixer.music.unpause()

