"""Marquee Lighted Sign Project - mode_interfaces."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field

from button_interface import ButtonInterface
from definitions import AutoModeEntry
from player_interface import PlayerInterface

@dataclass
class ModeInterface(ABC):
    """Mode abstract base."""
    player: PlayerInterface
    name: str

    @abstractmethod
    def button_action(self, button: ButtonInterface):
        """"""        

    @abstractmethod
    def execute(self):
        """"""

@dataclass
class AutoModeInterface(ModeInterface, ABC):
    """Supports time-based automatic mode change."""
    mode_sequence: list[AutoModeEntry]
    mode_iter: Iterator[AutoModeEntry] = field(init=False)
    trigger_time: float = field(init=False)

    @abstractmethod
    def exit(self):
        """Stop auto mode."""

    @abstractmethod
    def next_mode(self):
        """Set up next mode in sequence."""
