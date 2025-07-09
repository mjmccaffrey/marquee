""""""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from definitions import AutoModeEntry
from itertools import cycle
import time
from typing import Any

from button_interface import ButtonInterface
from player_interface import PlayerInterface

@dataclass
class BaseMode(ABC):
    """Base class for all modes."""
    player: PlayerInterface
    name: str

    @abstractmethod
    def button_action(self, button: ButtonInterface):
        """"""        

    @abstractmethod
    def execute(self):
        """Play the mode."""

@dataclass
class AutoMode(BaseMode):
    """Supports time-based automatic mode change."""
    mode_sequence: list[AutoModeEntry]
    pace: float = 1.0
    mode_iter: Iterator[AutoModeEntry] = field(init=False)
    trigger_time: float = field(init=False)

    def __post_init__(self):
        """Initialize."""
        self.mode_iter = cycle(self.mode_sequence)

    def button_action(self, button: ButtonInterface):
        """"""        

    def execute(self):
        """Return next mode in sequence."""
        return self.next_mode()

    def next_mode(self):
        """Set up next mode in sequence."""
        next_mode = next(self.mode_iter)
        self.trigger_time = (
            time.time() + next_mode.duration_seconds
        )
        print(f"Next auto mode is {next_mode.mode_index} "
              f"for {next_mode.duration_seconds} seconds.")
        return(next_mode.mode_index)
