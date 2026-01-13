"""Marquee Lighted Sign Project - musicmode"""

from abc import ABC
from dataclasses import dataclass

from .performancemode import PerformanceMode
from music import Measure, play, Section
from music.music_interface import set_player

@dataclass
class MusicMode(PerformanceMode, ABC):
    """Mode for playing music."""

    def __post_init__(self):
        """Initialize."""
        set_player(self.player)

    def execute(self, *elements: Measure | Section, tempo: int) -> None:
        """"""
        tempo = int(tempo * self.player.speed_factor)
        if isinstance(elements[0], Measure):
            assert all(isinstance(e, Measure) for e in elements)
            play(*elements, tempo=tempo)  # type: ignore
        else:
            for element in elements:
                assert isinstance(element, Section)
                element.play(tempo=tempo)

