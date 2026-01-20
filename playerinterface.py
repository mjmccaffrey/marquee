"""Marquee Lighted Sign Project - playerinterface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import NoReturn

from button_misc import ButtonSet
from event import PriorityQueue
from instruments import BellSet, DrumSet
from lightset import LightSet
from modes.mode_misc import ModeDefinition


class ChangeMode(Exception):
    """Change mode exception."""

@dataclass
class PlayerInterface(ABC):
    modes: dict[int, ModeDefinition]
    mode_ids: dict[str, int]
    bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    # top: LightSet
    speed_factor: float
    pace: float = field(init=False)
    active_mode_history: list[int] = field(init=False)
    bg_mode_instances: dict = field(init=False)
    event_queue: PriorityQueue = field(init=False)

    @abstractmethod
    def close(self) -> None:
        """Clean up."""

    @abstractmethod
    def execute(self, starting_mode_index: int) -> None:
        """Play the specified starting mode and all subsequent modes."""

