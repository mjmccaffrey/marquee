"""Marquee Lighted Sign Project - playerinterface"""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Callable

from button_misc import ButtonSet
from instruments import BellSet, DrumSet
from lightset import LightSet
from modes.modeconstructor import ModeConstructor
from specialparams import SpecialParams


@dataclass
class PlayerInterface(ABC):
    modes: dict[int, ModeConstructor]
    mode_ids: dict[str, int]
    bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    speed_factor: float
    current_mode: int | None = field(init=False)
    remembered_mode: int | None = field(init=False)
    pace: float = field(init=False)
    bg_mode_instances: dict = field(init=False)
    event_queue: object = field(init=False)

    @abstractmethod
    def close(self) -> None:
        """Clean up."""

    @abstractmethod
    def add_event(self, time: float, func: Callable):
        """Add event to queue; func will be called at time."""

    @abstractmethod
    def replace_kwarg_values(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Replace variables with current runtime values."""

    @abstractmethod
    def execute(self, starting_mode_index: int) -> None:
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
        ) -> None:
        """Execute sequence count times, with pace seconds in between.
           If stop is specified, end the sequence 
           just before the nth pattern.
           Pause for post_delay seconds before exiting."""

    @abstractmethod
    def wait(
        self, 
        seconds: tuple[float, ...] | float | None, elapsed: float = 0,
    ) -> None:
        """Wait seconds after adjusting for
           speed_factor and time already elapsed."""

    @abstractmethod
    def click(self) -> None:
        """Generate a small click sound by flipping
           an otherwise unused relay."""

