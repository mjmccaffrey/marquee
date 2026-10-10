"""Marquee Lighted Sign Project - musicmode"""

from abc import ABC
from dataclasses import dataclass
import logging

from .performancemode import PerformanceMode
from music import Piece, Section, Part, Measure, MusicTask, play
from task import Task

log = logging.getLogger('marquee.' + __name__)


@dataclass
class MusicMode(PerformanceMode, ABC):
    """Mode for playing music."""

    def _play_group(
        self, 
        group: Piece | Section | Part | Measure,
        delay: float,
        tempo: int,
    ):
        """Play provided musical notation.
           Tempo is used if no tempo is specified elsewhere."""
        tempo = tempo or getattr(group, 'tempo', 0)
        if not tempo:
            raise ValueError('A tempo is required.')
        match group:
            case Piece():
                for _group in group.groups:
                    delay += self._play_group(_group, delay, tempo)
                measures = ()
            case Section() | Part():
                measures = group.measures
            case Measure():
                measures = (group,)
        return delay + play(
            measures=measures, 
            delay=delay,
            tempo=tempo,
            devices=self.devices,
            schedule=self._schedule_task,
        )

    def _schedule_task(self, task: MusicTask) -> None:
        """"""
        self.player.tasks.push(
            Task(
                action=task.action,
                due=task.due,
                owner=self,
            )
        )

    def play(
        self, 
        *groups: Piece | Section | Part | Measure,
        tempo=0,
    ) -> float:
        """Play provided musical notation.
           Tempo is used if no tempo is specified elsewhere.
           Return seconds until music stops playing."""
        delay = 0.0
        for group in groups:
            delay += self._play_group(group, delay, tempo)
            print(
                len(self.player.tasks), 
                self.player.tasks._schedule[0].action,
                self.player.tasks._schedule[0].due,
            )
        return delay

