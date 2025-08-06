"""Marquee Lighted Sign Project - basemode"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from itertools import cycle
import time
from typing import Any, ClassVar

from button_interface import ButtonInterface
from definitions import AutoModeEntry

@dataclass
class BaseMode(ABC):
    """Base class for all modes."""
    player: Any
    name: str

    @abstractmethod
    def button_action(self, button: ButtonInterface):
        """Respond to button being pressed."""

    @abstractmethod
    def execute(self):
        """Play the mode."""

@dataclass
class AutoMode(BaseMode):
    """Supports time-based automatic mode change."""
    default_duration: ClassVar[float]
    mode_lookup: ClassVar[dict[str, int]]
    modes: list[AutoModeEntry]
    mode_iter: Iterator[AutoModeEntry] = field(init=False)
    trigger_time: float = field(init=False)

    def __post_init__(self):
        """Initialize."""
        self.mode_iter = cycle(self.modes)

    @classmethod
    def init(
        cls, 
        default_duration: float,
        mode_lookup: dict[str, int],
    ):
        """Prepare for classmethod add to be called."""
        cls.default_duration = default_duration
        cls.mode_lookup = mode_lookup

    @classmethod
    def add(cls, name: str, duration: float | None = None):
        """Add mode with name."""
        try:
            index = cls.mode_lookup[name]
        except LookupError:
            raise ValueError(f"Mode {name} not defined.")
        return AutoModeEntry(
            index=index, 
            name=name,
            duration=duration or cls.default_duration,
        )
    
    def button_action(self, button: ButtonInterface):
        """Respond to button being pressed."""

    def execute(self):
        """Return next mode in sequence."""
        return self.next_mode()

    def next_mode(self):
        """Set up next mode in sequence."""
        mode = next(self.mode_iter)
        self.trigger_time = (
            time.time() + mode.duration
        )
        print(f"Next auto mode is {mode.name} "
              f"for {mode.duration} seconds.")
        return(mode.index)
