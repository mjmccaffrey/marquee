"""Marquee Lighted Sign Project - musicmode"""

from abc import ABC
from dataclasses import dataclass
import logging

from .performancemode import PerformanceMode
from music import (
    Piece, Section, Part, Measure,
    play_measures, prepare_parts, prepare_measures,
)

log = logging.getLogger('marquee.' + __name__)


@dataclass
class MusicMode(PerformanceMode, ABC):
    """Mode for playing music."""

    def play(
        self, 
        *groups: Piece | Section | Part | Measure,
        delay = 0.0,
        tempo = 0,
    ):
        """Play provided musical notation.
           tempo is used if no tempo is specified elsewhere."""
        delay = 0
        for group in groups:
            tempo = tempo or getattr(group, 'tempo', 0)
            if not tempo:
                raise ValueError('A tempo is required.')
            match group:
                case Piece():
                    delay += self.play(
                        *group.groups, delay=delay, tempo=tempo,
                    )
                    measures = ()
                case Section():
                    measures = prepare_parts(
                        group.parts, self.devices, self.tasks,
                    )
                case Part():
                    measures = prepare_measures(
                        group.measures, self.devices, self.tasks,
                    )
                case Measure():
                    measures = prepare_measures(
                        (group,), self.devices, self.tasks,
                    )
            delay += play_measures(
                measures=measures, 
                delay=delay,
                tempo=tempo,
                schedule=self.tasks,
                owner=self,
            )
        return delay

