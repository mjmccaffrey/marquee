"""Marquee Lighted Sign Project - player_interface"""

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Any

from buttonsets import ButtonSet
from definitions import SpecialParams, ModeConstructor
from instruments import BellSet, DrumSet
from lightsets import LightSet
from automode_interface import AutoModeInterface

@dataclass
class PlayerInterface(ABC):
    modes: dict[int, ModeConstructor]
    bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    speed_factor: float
    auto_mode: AutoModeInterface | None = field(init=False)
    current_mode: int = field(init=False)
    pace: float = field(init=False)

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

    @abstractmethod
    def click(self):
        """Generate a small click sound by flipping
           an otherwise unused relay."""
