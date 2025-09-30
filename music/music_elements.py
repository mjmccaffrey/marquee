"""Marquee Lighted Sign Project - music_elements"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
import itertools
import time
from typing import Any, ClassVar

from instruments import (
    Instrument, ActionInstrument, BellSet, DrumSet, 
    ReleaseableInstrument, RestInstrument,
)
from .music_implementation import (
    apply_accent, apply_beats, play_measures, prepare_parts
)
from playerinterface import PlayerInterface
from specialparams import SpecialParams


@dataclass(frozen=True)
class Element(ABC):
    """Base for all musical items."""


@dataclass(frozen=True)
class BaseNote(Element, ABC):
    """Base for all musical notes."""
    instrument: ClassVar[type[Instrument]]
    duration: float

    @abstractmethod
    def play(self, player: PlayerInterface) -> None:
        """Play single BaseNote (abstract)."""


@dataclass(frozen=True)
class Rest(BaseNote):
    """Musical rest."""
    instrument: ClassVar[type[Instrument]] = RestInstrument

    def play(self, player: PlayerInterface) -> None:
        """Play single rest (do nothing)."""


@dataclass(frozen=True)
class ActionNote(BaseNote):
    """Note to execute arbitrary actions."""
    instrument: ClassVar[type[Instrument]] = ActionInstrument
    actions: tuple[Callable, ...]

    def __post_init__(self) -> None:
        """Validate."""
        assert self.actions

    def play(self, player: PlayerInterface) -> None:
        """Play single ActionNote."""
        for action in self.actions:
            action()


@dataclass(frozen=True)
class ReleasableNote(BaseNote, ABC):
    """Note that requires releasing after playing."""

    def add_to_release_queue(self, player: PlayerInterface) -> None:
        """Add note to release queue immediately after 
           concrete class plays it."""
        assert isinstance(self.instrument, ReleaseableInstrument)
        player.release_queue.append(
            (time.time() + self.instrument.release_time, self)
        )


@dataclass(frozen=True)
class BellNote(ReleasableNote):
    """Note to strike or release 1 or more bells."""
    instrument: ClassVar[type[ReleaseableInstrument]] = BellSet
    pitches: set[int]

    def __post_init__(self) -> None:
        """Validate."""
        assert self.pitches

    def play(self, player: PlayerInterface) -> None:
        """Play single BellNote."""
        player.bells.play(self.pitches)
        self.add_to_release_queue(player)

    def release(self, player: PlayerInterface) -> None:
        """Release all BellNotes."""
        player.bells.release(self.pitches)


@dataclass(frozen=True)
class DrumNote(BaseNote):
    """Note to sound relays."""
    instrument: ClassVar[type[Instrument]] = DrumSet
    accent: int
    pitches: set
    
    def __post_init__(self) -> None:
        """Validate."""
        assert self.pitches

    def play(self, player: PlayerInterface) -> None:
        """Play single DrumNote."""
        player.drums.play(self.accent, self.pitches)


@dataclass(frozen=True)
class NoteGroup(Element):
    """Contains notes to play concurrently."""
    notes: tuple[BaseNote, ...]
    duration: float = 0.0

    def __post_init__(self) -> None:
        """Validate."""
        assert self.notes
        assert all(n.duration == 0.0 for n in self.notes)

    def play(self, player: PlayerInterface) -> None:
        """Play all notes in group."""
        for note in self.notes:
            note.play(player)


@dataclass(frozen=True)
class Measure(Element):
    """Musical measure containing notes."""
    elements: tuple[Element, ...]
    beats: int

    def __post_init__(self) -> None:
        """Validate."""
        assert self.elements


@dataclass(frozen=True)
class SequenceMeasure(Measure):
    """Defines a measure with a sequence of light events."""
    sequence: Callable
    kwargs: dict[str, Any]
    step_duration: float
    count: int
    special: SpecialParams | None
    beats: int
    patterns: Iterator = field(init=False)

    def __post_init__(self) -> None:
        """Create iterator."""
        object.__setattr__(
            self, 
            'patterns', 
            itertools.cycle(self.sequence(**self.kwargs)),
        )


@dataclass(frozen=True)
class Sequence(Element):
    """Defines a sequence of light patterns."""
    sequence: Callable
    special: SpecialParams | None
    measures: int
    kwargs: dict[str, Any]
    iter: Iterator = field(init=False)

    def __post_init__(self) -> None:
        """Create iterator."""
        object.__setattr__(
            self, 
            'iter', 
            itertools.cycle(self.sequence(**self.kwargs)),
        )


@dataclass(frozen=True)
class Part(Element):
    """Musical part containing measures."""
    measures: tuple[Measure, ...]
    default_accent: int = 0

    def __post_init__(self) -> None:
        """Validate and process measures."""
        assert self.measures
        if self.default_accent:
            apply_accent(self.default_accent, self.measures)


@dataclass(frozen=True)
class Section(Element):
    """Musical section containing parts and meta info."""
    parts: tuple[Part, ...]
    beats: int
    tempo: int
    measures: tuple[Measure, ...] = field(init=False)

    def __post_init__(self) -> None:
        """Validate and process parts so they are ready to play."""
        assert self.parts
        if self.beats is not None:
            apply_beats(self.beats, self.parts)
        object.__setattr__(
            self, 
            'measures', 
            prepare_parts(self.parts),
        )

    def play(self, tempo: int = 0) -> None:
        """Play already-generated measures comprising Section."""
        play_measures(self.measures, tempo = tempo or self.tempo)

