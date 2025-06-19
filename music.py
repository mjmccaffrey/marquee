"""Marquee Lighted Sign Project - music"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field, replace
import itertools
import time
from typing import Any, ClassVar

from definitions import SpecialParams
from instruments import Instrument, ActionInstrument, BellSet, DrumSet, Piano, RestInstrument
from player_interface import PlayerInterface

def set_player(the_player: PlayerInterface):
    """Set the Player object used throughout this module."""
    global player
    player = the_player

@dataclass(frozen=True)
class Element(ABC):
    """Base for all musical items."""
    
@dataclass(frozen=True)
class BaseNote(Element):
    """Base for all musical notes."""
    instrument: ClassVar[type[Instrument]]
    duration: float

    @abstractmethod
    def play(self):
        """Play single BaseNote (abstract)."""

@dataclass(frozen=True)
class Rest(BaseNote):
    """Musical rest."""
    instrument: ClassVar[type[Instrument]] = RestInstrument

    def play(self):
        """Play single rest (do nothing)."""

@dataclass(frozen=True)
class ActionNote(BaseNote):
    """Note to execute arbitrary actions."""
    instrument: ClassVar[type[Instrument]] = ActionInstrument
    actions: tuple[Callable, ...]

    def play(self):
        """Play single ActionNote."""
        for action in self.actions:
            action()

@dataclass(frozen=True)
class BellNote(BaseNote):
    """Note to strike 1 or more bells."""
    instrument: ClassVar[type[Instrument]] = BellSet
    pitches: str

    def play(self):
        """Play single BellNote."""
        # player.bells.play(self.pitches)

@dataclass(frozen=True)
class DrumNote(BaseNote):
    """Note to click & clack relays."""
    instrument: ClassVar[type[Instrument]] = DrumSet
    accent: str

    def play(self):
        """Play single DrumNote."""
        player.drums.play(self.accent)

@dataclass(frozen=True)
class SustainedNote(BaseNote):
    """ """
    release: bool

@dataclass(frozen=True)
class PianoNote(SustainedNote):
    """Note for MIDI piano."""
    instrument: ClassVar[type[Instrument]] = Piano
    pitches: str

    def play(self):
        """Strike or release single PianoNote."""
        if self.release:
            player.piano.release(self.pitches)
        else:
            player.piano.play(self.pitches, self.duration, player.pace)

@dataclass(frozen=True)
class NoteGroup(Element):
    """Contains notes to play concurrently."""
    notes: tuple[BaseNote, ...]
    duration: float = 0.0

    def play(self):
        """Play all notes in group."""
        for note in self.notes:
            note.play()

@dataclass(frozen=True)
class Measure(Element):
    """Musical measure containing notes."""
    elements: tuple[Element, ...]
    beats: int

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

    def __post_init__(self):
        """Create iterator."""
        object.__setattr__(self, 'patterns', itertools.cycle(self.sequence(**self.kwargs)))

@dataclass(frozen=True)
class Sequence(Element):
    """Defines a sequence of light patterns."""
    sequence: Callable
    special: SpecialParams | None
    measures: int
    kwargs: dict[str, Any]
    iter: Iterator = field(init=False)

    def __post_init__(self):
        """Create iterator."""
        object.__setattr__(self, 'iter', itertools.cycle(self.sequence(**self.kwargs)))

@dataclass(frozen=True)
class Part(Element):
    """Musical part containing measures."""
    measures: tuple[Measure, ...]
    default_accent: str = ''
    # ??? elements: tuple[Element] = field(init=False)

    def __post_init__(self):
        """Process measures."""
        if self.default_accent:
            self._apply_accent(self.default_accent, self.measures)

    @staticmethod
    def _apply_accent(accent, measures: tuple[Measure, ...]):
        """Apply default accent (drums only)."""
        for measure in measures:
            elements = tuple(
                replace(element, accent=accent)
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
    measures: tuple[Measure, ...] = field(init=False)

    def __post_init__(self):
        """Process parts so they are ready to play."""
        if self.beats is not None:
            self._apply_beats(self.beats, self.parts)
        object.__setattr__(self, 'measures', self._prepare_parts(self.parts))

    def play(self):
        """Play already-generated measures comprising Section."""
        play(*self.measures, tempo=self.tempo)

    @staticmethod
    def _apply_beats(beats: int, parts: tuple[Part, ...]):
        """Apply default # of beats to all measures in the Section."""
        for part in parts:
            measures = tuple(
                replace(measure, beats=beats)
                for measure in part.measures
            )
            object.__setattr__(part, 'measures', measures)

    @staticmethod
    def _prepare_parts(
            parts: tuple[Part, ...], 
    ) -> tuple[Measure, ...]:
        """ Expand SequenceMeasures.
            Make all parts the same length.
            Merge parts into single sequence of Measures."""
        for part in parts:
            _expand_sequence_measures(part.measures)
            _convert_sustained_notes(part.measures)
        _make_parts_equal_length(parts)
        concurrent_measures = zip(*(part.measures for part in parts))
        return tuple(
            Section._merge_concurrent_measures(measure_set)
            for measure_set in concurrent_measures
        )

    @staticmethod
    def _merge_concurrent_measures(measures: tuple[Measure, ...]) -> Measure:
        """Convert measure from each part into single measure
        of (non-rest) notes with 0 duration, padded with rests."""

        def get_concurrent_notes(beat: float) -> list[BaseNote]:
            """Return all notes occuring on beat."""
            result = []
            for i, _ in enumerate(measures):
                if beat_next[i] == beat:
                    element = next(elements_in[i], None)
                    if element is None:
                        beat_next[i] = None
                    else:
                        assert isinstance(element, BaseNote)
                        beat_next[i] = beat + element.duration
                        if not isinstance(element, Rest):
                            result.append(replace(element, duration=0))
            return result

        def concurrent_note_output(concurrent: list[BaseNote]) -> Element | None:
            """Return concurrent notes as single object."""
            if len(concurrent) > 1:
                result = NoteGroup(tuple(concurrent))
            elif len(concurrent) == 1:
                result = concurrent[0]
            else:
                result = None
            return result

        beats = measures[0].beats
        assert all(m.beats == beats for m in measures)
        elements_in: list[Iterator] = [iter(m.elements) for m in measures]
        elements_out: list[Element] = []
        beat_next: list[float | None] = [0.0 for _ in measures]
        beat, rest_accumulated = 0.0, 0.0
        while any(bn is not None for bn in beat_next):
            concurrent = get_concurrent_notes(beat)
            out = concurrent_note_output(concurrent)
            if out is not None:
                if rest_accumulated:
                    elements_out.append(Rest(rest_accumulated))
                    rest_accumulated = 0.0
                elements_out.append(out)
            next_beat = min(
                (bn for bn in beat_next if bn is not None),
                default=beats
            )
            rest_accumulated += next_beat - beat
            beat = next_beat
        if rest_accumulated:
            elements_out.append(Rest(rest_accumulated))
        return Measure(tuple(elements_out), beats=beats)

def _convert_note_if_sustained(element: Element):
    """"""
    if isinstance(element, SustainedNote):
        result = [element, replace(element, duration=0, release=True)]
    else:
        result = [element]
    return result

def _convert_sustained_notes(measures: tuple[Measure, ...]):
    """Add release 'notes' for all notes played
       by an instrument that supports sustaining."""
    for measure in measures:
        elements = tuple(
            e
            for element in measure.elements
            for e in _convert_note_if_sustained(element)
        )
        object.__setattr__(measure, 'elements', elements)

def _expand_sequence_measures(measures: tuple[Measure, ...]):
    """Populate SequenceMeasures with ActionNotes."""
    for measure in measures:
        if not isinstance(measure, SequenceMeasure):
            continue
        assert isinstance(measure, SequenceMeasure)
        elements = tuple(
            ActionNote(
                duration=measure.step_duration,
                actions=(
                    light(
                        next(measure.patterns),
                        measure.special,
                    ),
                )
            )
            for _ in range(measure.count)
        )
        object.__setattr__(measure, 'elements', elements)

@staticmethod
def _make_parts_equal_length(parts: tuple[Part, ...]):
    # Make all parts have the same # of measures
    longest = max(len(part.measures) for part in parts)
    for part in parts:
        if len(part.measures) < longest:
            pad = Measure(elements=(), beats=part.measures[-1].beats)
            measures = tuple(
                part.measures[i] if i < len(part.measures) else pad
                for i in range(longest)
            )
            object.__setattr__(part, 'measures', measures)

def _play_measure(measure: Measure):
    """Play all notes in measure."""
    start = time.time()
    beat = 0
    for element in measure.elements:
        assert isinstance(element, (BaseNote, NoteGroup))
        element.play()
        if element.duration:
            wait_dur = (element.duration) * player.pace
            player.wait(wait_dur, time.time() - start)
            start = time.time()
        beat += element.duration
        if beat > measure.beats:
            raise ValueError("Too many actual beats in measure.")
    # Play implied rests at end of measure
    wait_dur = (measure.beats - beat) * player.pace 
    player.wait(wait_dur, time.time() - start)

def play(*measures: Measure, tempo: int):
    """Play a series of measures."""
    _expand_sequence_measures(measures)
    player.pace = 60 / tempo
    for measure in measures:
        _play_measure(measure)

def measure(*elements: Element, beats: int = 4) -> Measure:
    """Produce Measure."""
    return Measure(elements, beats=beats)

def part(*measures: Measure, accent: str = '') -> Part:
    """Produce Part."""
    return Part(measures, accent)

def section(
    *parts: Part,
    beats: int = 4,
    tempo: int = 60,
):
    """Produce Section."""
    return Section(
        parts, 
        beats=beats,
        tempo=tempo,
    )

def sequence(
    seq: Callable,
    measures: int = 1,
    special: SpecialParams | None = None,
    **kwargs,
) -> Sequence:
    """Return callable to effect each step in sequence."""
    sequence_obj = Sequence(seq, special, measures, kwargs)
    return sequence_obj

def dimmer(pattern: str) -> Callable:
    """Return callable to effect dimmer pattern."""
    return lambda: player.lights.set_dimmers(pattern)

def dimmer_sequence(brightness: int, transition: float) -> Callable:
    """Return callable to effect state of specified dimmers."""
    def func(lights: list[int]):
        player.lights.execute_dimmer_commands([
            (   player.lights.dimmer_channels[l], 
                brightness, 
                transition,
            )
            for l in lights
        ])
    return func

def light(
    pattern: Any,
    special: SpecialParams | None = None,
) -> Callable:
    """Callable to effect light pattern."""
    return lambda: player.lights.set_relays(pattern, special=special)
