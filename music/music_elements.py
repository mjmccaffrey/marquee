"""Marquee Lighted Sign Project - music_elements"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field, replace
from functools import partial
import itertools
import time
from typing import Any, ClassVar

from event import Event
from instruments import (
    Instrument, ActionInstrument, BellSet, DrumSet, 
    ReleaseableInstrument, RestInstrument,
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

    @abstractmethod
    def release(self, player: PlayerInterface) -> None:
        """Release BellNote."""

    def schedule_release(self, player: PlayerInterface) -> None:
        """Schedule release of played note."""
        assert issubclass(self.instrument, ReleaseableInstrument)
        player.event_queue.push(
            Event(
                action = partial(self.release, player),
                due = time.time() + self.instrument.release_time,
                owner = self,
            )
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
        """Play BellNote."""
        player.bells.play(self.pitches)
        self.schedule_release(player)

    def release(self, player: PlayerInterface) -> None:
        """Release BellNote."""
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
            self.apply_accent()

    def apply_accent(self) -> None:
        """Apply default accent (drums only)."""
        for measure in self.measures:
            elements = tuple(
                replace(element, accent=self.default_accent)
                    if (        isinstance(element, DrumNote) 
                        and not element.accent) else
                element
                for element in measure.elements
            )
            object.__setattr__(measure, 'elements', elements)


@dataclass(frozen=True)
class Section(Element):
    """Musical section containing parts and meta info."""
    parts: tuple[Part, ...]
    beats: int
    tempo: int
    prepare_parts: Callable[[tuple[Part, ...]], tuple[Measure, ...]]
    play_measures: Callable[[tuple[Measure, ...], int], None]
    measures: tuple[Measure, ...] = field(init=False)

    def __post_init__(self) -> None:
        """Validate and process parts so they are ready to play."""
        assert self.parts
        if self.beats is not None:
            self.apply_beats()
        object.__setattr__(
            self, 
            'measures', 
            self.prepare_parts(self.parts),
        )

    def apply_beats(self) -> None:
        """Apply default # of beats to all measures in the Section."""
        for part in self.parts:
            measures = tuple(
                replace(measure, beats=self.beats)
                for measure in part.measures
            )
            object.__setattr__(part, 'measures', measures)

    def play(self, tempo: int = 0) -> None:
        """Play already-generated measures comprising Section."""
        print("SECTION.PLAY")
        self.play_measures(self.measures, tempo or self.tempo)

