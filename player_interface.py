"""Marquee Lighted Sign Project - player interface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from instruments import BellSet, DrumSet
from lights import LightSet

@dataclass
class PlayerInterface:
    bells: BellSet
    drums: DrumSet
    lights: LightSet
    pace: float = 0.0

    @abstractmethod
    def wait(self, seconds: float | None, elapsed: float = 0):
        """"""
