"""Marquee Lighted Sign Project - background_modes"""

from abc import ABC, abstractmethod
from calendar import timegm
from collections.abc import Iterator
from dataclasses import dataclass, field
from itertools import cycle
from time import gmtime, time
from typing import Callable, ClassVar, NoReturn

from button_misc import ButtonInterface
from .basemode import BaseMode
from .mode_misc import ChangeMode, ModeConstructor, ModeIndex


@dataclass
class ModeEntry:
    name: str
    seconds: float
    index: int = -1


@dataclass
class BackgroundMode(BaseMode, ABC):
    """Base for all background modes.
       Background modes should not play anything directly."""
    modes: ClassVar[dict[int, ModeConstructor]]
    mode_ids: ClassVar[dict[str, int]]

    def button_action(self, button: ButtonInterface) -> None:
        """Respond to button being pressed."""
        raise ValueError(f"Button {button} action in background mode.")

    @abstractmethod
    def execute(self) -> int:
        """Return index of next mode."""


@dataclass
class SequenceBGMode(BackgroundMode):
    """Play sequence of foreground modes."""
    mode_sequence: list[ModeEntry]
    mode_iter: Iterator[ModeEntry] = field(init=False)
    mode_on_deck: ModeEntry = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        self.mode_iter = cycle(self.mode_sequence)
        self.mode_on_deck = next(self.mode_iter)
        self.validate_mode_sequence()

    def validate_mode_sequence(self) -> None:
        """Validate each ModeIndex in sequence."""
        for entry in self.mode_sequence:
            try:
                entry.index = self.mode_ids[entry.name]
            except LookupError:
                raise ValueError(f"Mode {entry.name} not defined.")

    def execute(self) -> int:
        """Return index of next mode in sequence. Schedule next next mode."""
        print(
            f"Next mode in sequence is "
            f"{self.modes[self.mode_on_deck.index]} "
            f"for {self.mode_on_deck.seconds} seconds."
        )
        self.schedule(
            action=self.execute,
            due=time() + self.mode_on_deck.seconds,
            name="SequenceBGMode execute", 
        )
        new_mode = self.mode_on_deck.index
        self.mode_on_deck = next(self.mode_iter)
        return new_mode
    
def on_the_hour():
    """Trigger every hour, on the hour."""
    now = gmtime()
    hour = now.tm_hour + 1
    target = timegm(now.__replace__(tm_hour=hour, tm_min=0, tm_sec=0))
    return target


@dataclass
class TimeBGMode(BackgroundMode, ABC):
    """Play a foreground mode upon a time trigger."""
    mode_name: str
    next_trigger_time: Callable[[], float]

    def __post_init__(self):
        """Schedule first event."""
        try:
            self.mode_index = self.mode_ids[self.mode_name]
        except LookupError:
            raise ValueError(f"Mode {self.mode_name} not defined.")
        self.schedule_next_event()

    def event_execute(self) -> NoReturn:
        """Schedule next event, raise event with foreground mode index."""
        raise ChangeMode(self.execute(), False)

    def execute(self, is_initial_mode: bool = True) -> int:
        """Return index of desired mode.
           If mode was specified on command line, return default mode."""
        self.schedule_next_event()
        return ModeIndex.DEFAULT if is_initial_mode else self.mode_index

    @abstractmethod
    def schedule_next_event(self):
        """Schedule next (future) event for this background mode."""
        self.schedule(
            action=self.event_execute,
            due=self.next_trigger_time(), 
            name="TimeBGMode event_execute",
        )

