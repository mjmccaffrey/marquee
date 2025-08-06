"""Marquee Lighted Sign Project - player_interface"""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from basemode import AutoMode
from buttonsets import ButtonSet
from definitions import SpecialParams, ModeConstructor
from instruments import BellSet, DrumSet
from lightsets import LightSet

@dataclass
class PlayerInterface(ABC):
    modes: dict[int, ModeConstructor]
    mode_ids: dict[str, int]
    bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    speed_factor: float
    auto_mode: AutoMode | None = field(init=False)
    current_mode: int = field(init=False)
    pace: float = field(init=False)
    release_queue: list[tuple[float, Any]] = field(init=False)

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
    def play_sequence(
            self, 
            sequence: Iterable, 
            count: int = 1, 
            pace: tuple[float, ...] | float | None = None,
            stop: int | None = None, 
            post_delay: float | None = 0.0, 
            special: SpecialParams | None = None,
        ):
        """Execute sequence count times, with pace seconds in between.
           If stop is specified, end the sequence 
           just before the nth pattern.
           Pause for post_delay seconds before exiting."""

    @abstractmethod
    def wait(
        self, 
        seconds: tuple[float, ...] | float | None, elapsed: float = 0,
    ):
        """Wait seconds after adjusting for
           speed_factor and time already elapsed."""

    @abstractmethod
    def click(self):
        """Generate a small click sound by flipping
           an otherwise unused relay."""
