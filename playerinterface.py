"""Marquee Lighted Sign Project - playerinterface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, NoReturn

from button_misc import ButtonSet
from event import PriorityQueue
from instruments import BellSet, DrumSet
from lightset import LightSet
from modes.mode_misc import ModeConstructor


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
    event_queue: PriorityQueue = field(init=False)

    @abstractmethod
    def close(self) -> None:
        """Clean up."""

    @abstractmethod
    def execute(self, starting_mode_index: int) -> None:
        """Play the specified mode and all subsequently selected modes."""

    @abstractmethod
    def wait(
        self, 
        seconds: float | None, 
        elapsed: float = 0.0,
    ) -> None | NoReturn:
        """Wait seconds, after adjusting for
           speed_factor and time already elapsed.
           If seconds is None, wait indefinitely.
           During this time, trigger any events that come due; 
           any button press will terminate waiting."""
        
