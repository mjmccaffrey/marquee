"""Marquee Lighted Sign Project - automode"""

from collections.abc import Iterator
from dataclasses import dataclass, field
from itertools import cycle
import time
from typing import ClassVar

from button_misc import ButtonProtocol
from .modeinterface import ModeInterface

@dataclass
class AutoModeEntry:
    index: int
    name: str
    duration: float

@dataclass
class AutoMode(ModeInterface):
    """Supports time-based automatic mode change."""
    default_duration: ClassVar[float]
    mode_lookup: ClassVar[dict[str, int]]
    modes: list[AutoModeEntry]
    mode_iter: Iterator[AutoModeEntry] = field(init=False)
    trigger_time: float = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        self.mode_iter = cycle(self.modes)

    @classmethod
    def init(
        cls, 
        default_duration: float,
        mode_lookup: dict[str, int],
    ) -> None:
        """Prepare for classmethod add to be called."""
        cls.default_duration = default_duration
        cls.mode_lookup = mode_lookup

    @classmethod
    def add(cls, name: str, duration: float | None = None) -> AutoModeEntry:
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
    
    def button_action(self, button: ButtonProtocol) -> None:
        """Respond to button being pressed."""

    def execute(self) -> int:
        """Return index of next mode in sequence."""
        return self.next_mode()

    def next_mode(self) -> int:
        """Set up next mode in sequence. Return mode index."""
        mode = next(self.mode_iter)
        self.trigger_time = (
            time.time() + mode.duration
        )
        print(f"Next auto mode is {mode.name} "
              f"for {mode.duration} seconds.")
        return(mode.index)

    def exit(self) -> None:
        """Exit auto mode."""
        print("Exiting auto mode.")
        self.player.auto_mode = None
