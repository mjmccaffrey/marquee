"""Marquee Lighted Sign Project - musicmode"""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
import logging
from typing import cast, override

from .performancemode import PerformanceMode
from music import Measure, play, Section
from music.music_interface import set_mode

log = logging.getLogger('marquee.' + __name__)


@dataclass
class MusicMode(PerformanceMode, ABC):
    """Mode for playing music."""

    def __post_init__(self):
        """Initialize."""
        set_mode(self)

    @override
    def execute(self, *elements: Measure | Section, tempo: int) -> None:
        """"""
        tempo = int(tempo * self.speed_factor)
        if isinstance(elements[0], Measure):
            assert all(isinstance(e, Measure) for e in elements)
            play(*cast(Sequence[Measure], elements), tempo=tempo)
        else:
            for element in elements:
                assert isinstance(element, Section)
                element.play(tempo=tempo)

