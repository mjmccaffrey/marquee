"""Marquee Lighted Sign Project - automode_interface."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field

from definitions import AutoModeEntry
from mode_interface import ModeInterface

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
