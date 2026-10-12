"""Marquee Lighted Sign Project - music_abstract"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
import logging
import time
from typing import Protocol
from typing_extensions import override

from instruments import Instrument, LightSet, ReleaseableInstrument
from schemas import DeviceName, EpochTime


log = logging.getLogger('marquee.' + __name__)


@dataclass(frozen=True, kw_only=True)
class MusicTask:
    """"""
    action: Callable
    due: EpochTime


@dataclass(frozen=True, kw_only=True)
class Element(ABC):
    """Base for all musical items."""


@dataclass(frozen=True, kw_only=True)
class Note(Element, ABC):
    """Base for all musical notes."""
    device: DeviceName
    duration: float = 0.0


@dataclass(frozen=True, kw_only=True)
class PlayableNote(Note, ABC):
    """Note that has necessary resources assigned."""
    instrument: Instrument

    @abstractmethod
    def play(self) -> None:
        """Play single Note."""
        self.instrument.play()


@dataclass(frozen=True, kw_only=True)
class Accented(ABC):
    accent: int


@dataclass(frozen=True, kw_only=True)
class Pitched(ABC):
    pitches: set[int]


@dataclass(frozen=True, kw_only=True)
class ReleasedNote(Note, ABC):
    """Note that involves releasing after playing."""


@dataclass(frozen=True, kw_only=True)
class PlayableReleasedNote(ReleasedNote, PlayableNote, ABC):
    """Note that involves releasing after playing."""
    instrument: ReleaseableInstrument

    def release(self) -> None:
        """Release note."""
        self.instrument.release()

    @abstractmethod
    def release_time(cls, bps: float, play_start: float) -> float:
        """"""


@dataclass(frozen=True, kw_only=True)
class LightNote(Note, ABC):
    """Base for Channel and Relay notes."""
    device: DeviceName = DeviceName.LIGHTS
    kwargs: dict


@dataclass(frozen=True, kw_only=True)
class PlayableLightNote(LightNote, PlayableNote, ABC):
    """Base for Channel and Relay notes."""
    instrument: LightSet


@dataclass(frozen=True, kw_only=True)
class DinNote(ReleasedNote, ABC):
    """Note to play and rest a buzzer, ringer, etc."""
    device: DeviceName = field(init=False)


@dataclass(frozen=True, kw_only=True)
class PlayableDinNote(DinNote, PlayableReleasedNote, ABC):
    """Note to play and rest a buzzer, ringer, etc."""

    @override
    def play(self) -> None:
        """Play note."""
        super().play()

    @override
    def release_time(self, bps: float, play_start: float) -> float:
        """"""
        return play_start + self.duration / bps


class ScheduleTask(Protocol):
    """Call signature to schedule a task."""
    def __call__(
        self,
        task: MusicTask,
    ) -> None:
        ...

