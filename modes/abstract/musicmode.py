"""Marquee Lighted Sign Project - musicmode"""

from abc import ABC
from dataclasses import dataclass
import logging

from .performancemode import PerformanceMode
from music import Piece, Section, Part, Measure, play

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
                delay += self._play_group(
                    *group.groups, delay=delay, tempo=tempo,
                )
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
            schedule=self.player.tasks,
            owner=self,
        )

    def play(
        self, 
        *groups: Piece | Section | Part | Measure,
        tempo = 0,
    ) -> float:
        """Play provided musical notation.
           Tempo is used if no tempo is specified elsewhere.
           Return seconds until music stops playing."""
        delay = 0.0
        for group in groups:
            delay += self._play_group(group, delay, tempo)
        return delay

