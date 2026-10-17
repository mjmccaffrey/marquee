"""Marquee Lighted Sign Project - musicmode"""

from abc import ABC
from dataclasses import dataclass
import logging

from .performancemode import PerformanceMode
from music.music_interface import set_mode

log = logging.getLogger('marquee.' + __name__)


@dataclass
class MusicMode(PerformanceMode, ABC):
    """Mode for playing music."""

    def __post_init__(self):
        """Initialize."""
        super().__post_init__()
        set_mode(self)

