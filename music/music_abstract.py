"""Marquee Lighted Sign Project - music_abstract"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
import logging
from typing_extensions import override

from devices.device_schemas import DeviceName
from instruments import Instrument, LightSet, ReleaseableInstrument

log = logging.getLogger('marquee.' + __name__)


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
    duration_original: float = field(init=False)

    def __post_init__(self) -> None:
        """"""
        object.__setattr__(self, 'duration_original', self.duration)

    @abstractmethod
    def play(self, bps: float) -> None:
        """Play single Note."""
        self.instrument.play()


@dataclass(frozen=True, kw_only=True)
class Accented(ABC):
    accent: int


@dataclass(frozen=True, kw_only=True)
class Pitched(ABC):
    pitches: set[int]


@dataclass(frozen=True, kw_only=True)
class Scheduled(ABC):
    schedule: Callable[[Callable[[], None], float], None]


@dataclass(frozen=True, kw_only=True)
class ReleasableNote(Note, ABC):
    """Note that involves releasing after playing."""


@dataclass(frozen=True, kw_only=True)
class PlayableReleasableNote(ReleasableNote, PlayableNote, Scheduled, ABC):
    """Note that involves releasing after playing."""
    instrument: ReleaseableInstrument

    def release(self) -> None:
        """Release note."""
        self.instrument.release()

    def schedule_release(self, release_time: float) -> None:
        """Schedule release of played note."""
        self.schedule(self.release, release_time)


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
class DinNote(ReleasableNote, ABC):
    """Note to play and rest a buzzer, ringer, etc."""
    device: DeviceName = field(init=False)


@dataclass(frozen=True, kw_only=True)
class PlayableDinNote(DinNote, PlayableReleasableNote, ABC):
    """Note to play and rest a buzzer, ringer, etc."""

    @override
    def play(self, bps: float) -> None:
        """Play note."""
        super().play(bps)
        self.schedule_release(self.duration_original / bps)

