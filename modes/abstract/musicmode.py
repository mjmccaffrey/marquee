"""Marquee Lighted Sign Project - musicmode"""

from abc import ABC
from dataclasses import dataclass
import logging

from .performancemode import PerformanceMode
from music import Piece, Section, Part, Measure, MusicTask, play_measures
from schemas import EpochTime
from task import Task

log = logging.getLogger('marquee.' + __name__)


@dataclass
class MusicMode(PerformanceMode, ABC):
    """Mode for playing music."""

    def play(
        self, 
        *groups: Piece | Section | Part | Measure,
        tempo=0,
    ) -> float:
        """Play provided musical notation.
           Tempo is used if no tempo is specified elsewhere.
           Return the duration of the music in seconds."""
        duration = 0.0
        for group in groups:
            print("musicmode.play")
            duration += self._play_group(group, duration, tempo)
            # print(
            #     len(self.player.tasks), 
            #     self.player.tasks._schedule[0].action,
            #     self.player.tasks._schedule[0].due,
            # )
        return duration

    def _play_group(
        self, 
        group: Piece | Section | Part | Measure,
        delay: float,
        tempo: int,
    ):
        """Play provided musical notation after initial delay.
           Tempo is used if no tempo is specified elsewhere.
           Return the duration of the music in seconds."""
        tempo = tempo or getattr(group, 'tempo', 0)
        if not tempo:
            raise ValueError('A tempo is required.')
        duration = 0.0
        match group:
            case Piece():
                for _group in group.groups:
                    duration += self._play_group(_group, delay + duration, tempo)
                    print("Section " + _group.name if isinstance(_group, Section) else "group in piece", delay)
                measures = ()
            case Section() | Part():
                measures = group.measures
            case Measure():
                measures = (group,)
        if measures:
            duration += play_measures(
                measures=measures, 
                delay=delay + duration,
                tempo=tempo,
                devices=self.devices,
                schedule=self._schedule_task,
            )
            print(f"{duration=}")
        return duration

    def _schedule_task(self, task: MusicTask) -> None:
        """"""
        self.player.tasks.push(
            Task(
                action=task.action,
                due=task.due,
                owner=self,
            )
        )

