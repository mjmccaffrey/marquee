"""Marquee Lighted Sign Project - music_collections"""

from collections.abc import Callable
from dataclasses import dataclass, field, replace
import logging
from typing import Any, Protocol

from .music_elements import (
    Element, Note, DrumNote,
    AccentedNote, PitchedNote, ScheduledNote,
)

log = logging.getLogger('marquee.' + __name__)


@dataclass(frozen=True)
class NoteGroup(Element):
    """Contains notes to play concurrently."""
    notes: tuple[Note, ...]
    duration: float = 0.0

    def play(self, bps: float) -> None:
        """Play all notes in group, not quite concurrently."""
        for note in self.notes:
            note.play(bps)


@dataclass(frozen=True)
class Measure(Element):
    """Musical measure containing notes and / or implicit rests."""
    elements: tuple[Element, ...]
    beats: int


@dataclass(frozen=True)
class Part(Element):
    """Musical part containing measures.
       All measures have the same number of beats."""
    measures: tuple[Measure, ...]
    default_accent: int = 0

    def __post_init__(self) -> None:
        """Validate and process measures."""
        if self.default_accent:
            self._apply_accent()

    def _apply_accent(self) -> None:
        """Apply default accent."""
        for measure in self.measures:
            elements = tuple(
                replace(e, accent=self.default_accent)
                if isinstance(e, AccentedNote) and e.accent else
                e
                for e in measure.elements
            )
            object.__setattr__(measure, 'elements', elements)


@dataclass(frozen=True)
class Section(Element):
    """Musical section containing parts and meta info.
       All measures have the same number of beats."""
    parts: tuple[Part, ...]
    beats: int
    tempo: int = 0

    def __post_init__(self) -> None:
        """"""
        if self.beats is not None:
            self._apply_beats()

    def _apply_beats(self) -> None:
        """Apply default # of beats to all measures in the Section."""
        for part in self.parts:
            measures = tuple(
                replace(measure, beats=self.beats)
                for measure in part.measures
            )
            object.__setattr__(part, 'measures', measures)


@dataclass(frozen=True)
class Piece(Element):
    """Series of Sections and Parts. 
       Number of beats across sections and parts may vary."""
    groups: tuple[Section | Part, ...]
    tempo: int = 0


# class PlayMeasures(Protocol):
#     """Signature for playing a sequence of measures."""
#     def __call__(
#         self,
#         measures: tuple[Measure, ...], 
#         delay: float, 
#         tempo: int,
#     ) -> float:
#         ...


