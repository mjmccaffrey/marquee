"""Marquee Lighted Sign Project - music_elements"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
import logging
from typing_extensions import override

from devices.devices_misc import Device
from instruments import (
    Instrument, BellSet, DrumSet, LightSet, ReleaseableInstrument,
)

log = logging.getLogger('marquee.' + __name__)


@dataclass(frozen=True)
class Element(ABC):
    """Base for all musical items."""


@dataclass(frozen=True)
class Note(Element, ABC):
    """Base for all musical notes."""
    device: Device
    duration: float = 0.0
    instrument: Instrument = field(init=False)
    duration_original: float = field(init=False)

    def __post_init__(self) -> None:
        """"""
        object.__setattr__(self, 'duration_original', self.duration)

    @abstractmethod
    def play(self, bps: float) -> None:
        """Play single Note."""
        self.instrument.play()


@dataclass(frozen=True, kw_only=True)
class ActionNote(Note):
    """Note to execute arbitrary actions."""
    device: None = field(init=False)
    instrument: None = field(init=False)
    action: Callable[[], None]

    @override
    def play(self, bps: float) -> None:
        """Play single ActionNote."""
        self.action()


@dataclass(frozen=True)
class Rest(Note):
    """Musical rest."""
    device: None = field(init=False)
    instrument: None = field(init=False)

    @override
    def play(self, bps: float) -> None:
        """Play single rest (do nothing)."""
        raise RuntimeError("PLAYING REST")


@dataclass(frozen=True, kw_only=True)
class AccentedNote(ABC):
    accent: int


@dataclass(frozen=True, kw_only=True)
class PitchedNote(ABC):
    pitches: set[int]


@dataclass(frozen=True, kw_only=True)
class ScheduledNote(ABC):
    schedule: Callable[[Callable[[], None], float], None] = field(init=False)


@dataclass(frozen=True, kw_only=True)
class ReleasableNote(Note, ScheduledNote, ABC):
    """Note that involves releasing after playing."""
    instrument: ReleaseableInstrument = field(init=False)

    def release(self) -> None:
        """Release note."""
        self.instrument.release()

    def schedule_release(self, release_time: float) -> None:
        """Schedule release of played note."""
        self.schedule(self.release, release_time)


@dataclass(frozen=True, kw_only=True)
class BellNote(ReleasableNote, PitchedNote):
    """Note to strike and release 1 or more bells."""
    instrument: BellSet = field(init=False)

    @override
    def play(self, bps: float) -> None:
        """Play BellNote."""
        self.instrument.play(self.pitches)
        self.schedule_release(self.instrument.release_time)

    @override
    def release(self) -> None:
        """Release BellNote."""
        self.instrument.release(self.pitches)


@dataclass(frozen=True)
class DrumNote(Note, AccentedNote, PitchedNote):
    """Note to sound relays."""
    device: Device = field(init=False, default=Device.DRUMS)
    instrument: DrumSet = field(init=False)


    @override
    def play(self, bps: float) -> None:
        """Play DrumNote."""
        self.instrument.play(self.accent, self.pitches)


@dataclass(frozen=True, kw_only=True)
class LightNote(Note, ABC):
    """Base for Channel and Relay notes."""
    device: Device = field(init=False, default=Device.LIGHTS)
    instrument: LightSet = field(init=False)
    kwargs: dict


@dataclass(frozen=True)
class LightRelayNote(LightNote):
    """Note to execute light relay actions."""

    @override
    def play(self, bps: float) -> None:
        """Play single LightRelayNote."""
        if self.kwargs:
            self.instrument.set_relays(**self.kwargs)


@dataclass(frozen=True)
class LightChannelNote(LightNote):
    """Note to execute light channel actions."""

    @override
    def play(self, bps: float) -> None:
        """Play single LightChannelNote."""
        if self.kwargs:
            self.instrument.set_channels(**self.kwargs)


@dataclass(frozen=True)
class DinNote(ReleasableNote):
    """Note to play and rest a buzzer, ringer, etc."""
    device: Device = field(init=False)

    @override
    def play(self, bps: float) -> None:
        """Play note."""
        super().play(bps)
        self.schedule_release(self.duration_original / bps)


@dataclass(frozen=True)
class BuzzerNote(DinNote):
    """"""
    device: Device = field(init=False, default=Device.BUZZER)


@dataclass(frozen=True)
class RingerNote(DinNote):
    """"""
    device: Device = field(init=False, default=Device.RINGER)

