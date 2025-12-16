"""Marquee Lighted Sign Project - playerinterface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import NoReturn

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
    # top: LightSet
    speed_factor: float
    pace: float = field(init=False)
    fg_mode_history: list[int] = field(init=False)
    bg_mode_instances: dict = field(init=False)
    event_queue: PriorityQueue = field(init=False)

    @abstractmethod
    def close(self) -> None:
        """Clean up."""

    @abstractmethod
    def change_mode(self, mode_index: int) -> NoReturn:
        """Change active mode to mode_index."""
        raise  # Pylance work-around

    @abstractmethod
    def delete_mode_instance(
        self, 
        bg_index: int | None = None,
        fg_instance: object | None = None,
    ) -> None:
        """Delete foreground or background mode instance and scheduled events."""

    @abstractmethod
    def execute(self, starting_mode_index: int) -> None:
        """Play the specified mode and all subsequently selected modes."""

    # @abstractmethod
    # def wait(
    #     self, 
    #     seconds: float | None, 
    #     elapsed: float = 0.0,
    # ) -> None | NoReturn:
    #     """Wait seconds, after adjusting for
    #        speed_factor and time already elapsed.
    #        If seconds is None, wait indefinitely.
    #        During this time, trigger any events that come due; 
    #        any button press will terminate waiting."""
        
