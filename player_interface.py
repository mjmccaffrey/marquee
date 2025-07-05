"""Marquee Lighted Sign Project - player interface"""

from abc import ABC, abstractmethod
from buttonsets import ButtonSet
from collections.abc import Iterable
from dataclasses import dataclass
from instruments import BellSet, DrumSet
from lights import LightSet
from mode_interface import ModeConstructor
from specialparams import SpecialParams
from typing import Any

@dataclass
class PlayerInterface:
    modes: dict[int, ModeConstructor]
    bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    speed_factor: float

    @abstractmethod
    def close(self):
        """Clean up."""

    @abstractmethod
    def replace_kwarg_values(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Replace variables with current runtime values."""

    @abstractmethod
    def execute(self, starting_mode_index: int):
        """Play the specified mode and all subsequently selected modes."""

    @abstractmethod
    def next_auto_mode(self):
        """Effect change to next auto mode in sequence."""

    @abstractmethod
    def play_sequence(
            self, 
            sequence: Iterable, 
            count: int = 1, 
            pace: tuple[float, ...] | float | None = None,
            stop: int | None = None, 
            post_delay: float = 0, 
            special: SpecialParams | None = None,
        ):
        """Execute sequence count times, with pace seconds in between.
           If stop is specified, end the sequence 
           just before the nth pattern.
           Pause for post_delay seconds before exiting."""

    @abstractmethod
    def wait(self, seconds: float | None, elapsed: float = 0):
        """"""
