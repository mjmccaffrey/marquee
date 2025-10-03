"""Marquee Lighted Sign Project - playerinterface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from button_misc import ButtonSet
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
    event_queue: object = field(init=False)

    @abstractmethod
    def close(self) -> None:
        """Clean up."""

    @abstractmethod
    def add_event(self, time_due: float, owner: object, action: Callable) -> None:
        """Add event to queue."""

    @abstractmethod
    def execute(self, starting_mode_index: int) -> None:
        """Play the specified mode and all subsequently selected modes."""

