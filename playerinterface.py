"""Marquee Lighted Sign Project - playerinterface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import NoReturn

from button_misc import ButtonSet
from event import PriorityQueue
from instruments import BellSet, DrumSet
from lightset import LightSet
from modes.mode_misc import ModeConstructor


class ChangeMode(Exception):
    """Change mode exception."""

@dataclass
class PlayerInterface(ABC):
    modes: dict[int, ModeConstructor]
    mode_ids: dict[str, int]
    bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    # top: LightSet
    speed_factor: float
    pace: float = field(init=False)
    fg_mode_history: list[int] = field(init=False)
    bg_mode_instances: dict = field(init=False)
    event_queue: PriorityQueue = field(init=False)

    @abstractmethod
    def close(self) -> None:
        """Clean up."""

    # @abstractmethod
    # def change_mode(self, mode_index: int) -> NoReturn:
    #     """Change active mode to mode_index."""
    #     raise  # Pylance work-around

    @abstractmethod
    def execute(self, starting_mode_index: int) -> None:
        """Play the specified starting mode and all subsequent modes."""

