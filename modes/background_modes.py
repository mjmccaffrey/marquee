"""Marquee Lighted Sign Project - background_modes"""

from abc import ABC, abstractmethod
from calendar import timegm
from collections.abc import Iterator
from dataclasses import dataclass, field
from itertools import cycle
from time import gmtime, time
from typing import Callable, ClassVar, NoReturn

from configuration import ModeIndex
from button_misc import ButtonProtocol
from .modeconstructor import ModeConstructor
from .modeinterface import ModeInterface
from playerinterface import PlayerInterface


@dataclass
class ModeEntry:
    index: int
    time: float


class BackgroundModeDue(Exception):
    """Background mode run due exception."""


@dataclass
class BackgroundMode(ModeInterface, ABC):
    """"""
    player: PlayerInterface
    execute_count: int = field(init=False)
    modes: ClassVar[dict[int, ModeConstructor]]
    mode_ids: ClassVar[dict[str, int]]
    trigger_time: float = field(init=False)

    @classmethod
    def init(
        cls, 
        modes: dict[int, ModeConstructor],
        mode_ids: dict[str, int],
    ) -> None:
        """Prepare for classmethod add to be called."""
        cls.modes = modes
        cls.mode_ids = mode_ids

    def button_action(self, button: ButtonProtocol) -> None:
        """Respond to button being pressed."""
        raise ValueError(f"Button {button} action in background mode.")

    @abstractmethod
    def execute(self) -> int:
        """Return index of next mode."""


@dataclass
class SequenceBGMode(BackgroundMode):
    """Play sequence of foreground modes."""
    default_duration: ClassVar[float]
    mode_sequence: list[ModeEntry]
    mode_iter: Iterator[ModeEntry] = field(init=False)
    mode_on_deck: ModeEntry = field(init=False)

    @classmethod
    def init(
        cls, 
        default_duration: float,
        modes: dict[int, ModeConstructor],
        mode_ids: dict[str, int],
    ) -> None:
        """Prepare for classmethod add to be called."""
        super().init(modes, mode_ids)
        cls.default_duration = default_duration

    @classmethod
    def add(cls, name: str, duration: float | None = None) -> ModeEntry:
        """Add mode with name to place in the sequence."""
        try:
            index = cls.mode_ids[name]
        except LookupError:
            raise ValueError(f"Mode {name} not defined.")
        return ModeEntry(index, time = duration or cls.default_duration)

    def __post_init__(self) -> None:
        """Initialize."""
        self.mode_iter = cycle(self.mode_sequence)
        self.mode_on_deck = next(self.mode_iter)

    def execute(self) -> int:
        """Return index of next mode in sequence. Schedule next next mode."""
        print(
            f"Next mode in sequence is "
            f"{self.modes[self.mode_on_deck.index]} "
            f"for {self.mode_on_deck.time} seconds."
        )
        self.player.add_event(
            time() + self.mode_on_deck.time, 
            self.execute,
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
        raise BackgroundModeDue(self.execute(), False)

    def execute(self, is_initial_mode: bool = True) -> int:
        """Return index of desired mode.
           If mode was specified on command line, return default mode."""
        self.schedule_next_event()
        return ModeIndex.DEFAULT if is_initial_mode else self.mode_index

    @abstractmethod
    def schedule_next_event(self):
        """"""
        self.player.add_event(self.next_trigger_time(), self.event_execute)

