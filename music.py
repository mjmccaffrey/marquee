"""Marquee Lighted Sign Project - music"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import itertools
import time
from typing import Any, ClassVar

from definitions import SpecialParams
from instruments import Instrument, ActionInstrument, BellSet, DrumSet, RestInstrument

accent_symbols = '->^'
pitch_symbols = 'DEGAabcde'
note_duration: dict[str, float] = {
    '𝅝': 4,     '𝅗𝅥': 2,      '♩': 1,
    '♪': 0.5,   '𝅘𝅥𝅯': 0.25,  '𝅘𝅥𝅰': 0.125,
}
rest_duration: dict[str, float] = {
    '𝄻': 4,    '𝄼': 2,      '𝄽': 1,
    '𝄾': 0.5,   '𝄿': 0.25,  '𝅀': 0.125,
}
symbol_duration = note_duration | rest_duration

@dataclass
class Environment:
    bell_set: BellSet
    drum_set: DrumSet
    light: Callable[[Any, SpecialParams | None], Callable]
    wait: Callable[[float, float], None]

def set_environment(env: Environment):
    """"""
    global environment
    environment = env

@dataclass
class Element(ABC):
    """Base for all musical items."""
    
@dataclass
class BaseNote(Element):
    """Base for all musical notes."""
    instrument_class: ClassVar[type[Instrument]]
    duration: float

    @abstractmethod
    def play(self):
        """"""

@dataclass
class Rest(BaseNote):
    """Musical rest."""
    instrument_class: ClassVar[type[Instrument]] = RestInstrument

    def play(self):
        """"""

@dataclass
class ActionNote(BaseNote):
    """Note to execute arbitrary actions."""
    instrument_class: ClassVar[type[Instrument]] = ActionInstrument
    actions: tuple[Callable, ...]

    def play(self):
        for action in self.actions:
            action()

@dataclass
class BellNote(BaseNote):
    """Note to strike 1 or more bells."""
    instrument_class: ClassVar[type[Instrument]] = BellSet
    pitches: str

    def play(self):
        environment.bell_set.play(self.pitches)

@dataclass
class DrumNote(BaseNote):
    """Note to click & clack relays."""
    instrument_class: ClassVar[type[Instrument]] = DrumSet
    accent: str

    def play(self):
        environment.bell_set.play(self.accent)

@dataclass
class NoteGroup(Element):
    """Contains notes to play concurrently."""
    notes: tuple[BaseNote, ...]
    
@dataclass
class Measure(Element):
    """Musical measure containing notes."""
    elements: tuple[Element, ...]
    beats: int
    
@dataclass
class SequenceMeasure(Measure):
    """Will be expanded to a Measure with notes."""
    sequence: Callable
    kwargs: dict[str, Any]
    step_duration: float
    count: int
    special: SpecialParams | None
    beats: int

    def __post_init__(self):
        self.seq = Sequence(self.sequence, **self.kwargs)

@dataclass
class Sequence(Element):
    """"""
    sequence: Callable
    kwargs: dict[str, Any]

    def __post_init__(self):
        self.iter = itertools.cycle(self.sequence(**self.kwargs))

@dataclass
class Part(Element):
    """Musical part containing measures."""
    measures: tuple[Measure, ...]
    default_accent: str = ''

    def __post_init__(self):
        if self.default_accent:
            self._apply_accent(self.default_accent, self.measures)

    @staticmethod
    def _apply_accent(accent, measures: tuple[Measure, ...]):
        """"""
        for measure in measures:
            for element in measure.elements:
                assert isinstance(element, DrumNote)
                if not element.accent:
                    element.accent = accent

@dataclass
class Section(Element):
    """Musical section containing parts and meta info."""
    parts: tuple[Part, ...]
    pace: float
    beats: int
    tempo: int

    def __post_init__(self):
        """"""
        if self.beats is not None:
            self._apply_beats(self.beats, self.parts)
        self._measures = self._prepare_parts(self.parts)

    def play(self):
        """"""
        play(
            *self._measures,
            pace=self.pace,
        )

    @staticmethod
    def _apply_beats(beats, parts):
        """"""
        for part in parts:
            for measure in part.measures:
                measure.beats = beats


    #     self.player.sign.drum_set.accent = symbol

    #         
    # NEED THIS FOR Sections and raw measures:
    # if beat > measure.beats:
    #             raise ValueError("Too many actual beats in measure.")

    @staticmethod
    def _prepare_parts(
            parts: tuple[Part, ...], 
    ) -> list[Measure]:
        #
        for part in parts:
            expand_sequences(part.measures)
        # Make all parts have the same # of measures
        longest = max(len(p.measures) for p in parts)
        for p in parts:
            if len(p.measures) < longest:
                pad = Measure(elements=(), beats=p.measures[-1].beats)
                p.measures = tuple(
                    p.measures[i] if i < len(p.measures) else pad
                    for i in range(longest)
                )
        #
        concurrent_measures = zip(*(p.measures for p in parts))
        return [
            Section.merge_concurrent_measures(measure_set)
            for measure_set in concurrent_measures
        ]

    @staticmethod
    def merge_concurrent_measures(measures: tuple[Measure, ...]) -> Measure:
        """Convert measure from each part into single measure
        of notes with 0 duration, padded with rests."""
        beats = measures[0].beats
        assert all(m.beats == beats for m in measures)
        elements_in = [iter(m.elements) for m in measures]
        elements_out: list[Element] = []
        beat_next: list[float | None] = [0 for m in measures]
        beat, next_beat, rest = 0.0, 0.0, 0.0
        while any(bn is not None for bn in beat_next):
            # Get concurrent notes
            beat = next_beat
            out: list[Element] = []
            concurrent_notes: list[BaseNote] = []
            for i, _ in enumerate(measures):
                if beat_next[i] == beat:
                    element = next(elements_in[i], None)
                    if element is None:
                        beat_next[i] = None
                    else:
                        assert isinstance(element, BaseNote)
                        beat_next[i] = beat + element.duration
                        if not isinstance(element, Rest):
                            element.duration = 0
                            concurrent_notes.append(element)
            if concurrent_notes and rest:
                out.append(Rest(rest))
                rest = 0.0
            # Group notes if necessary
            if len(concurrent_notes) > 1:
                out.append(NoteGroup(tuple(concurrent_notes)))
            elif len(concurrent_notes) == 1:
                out.append(concurrent_notes[0])
            # Calculate next_beat
            next_beat = min(
                (bn for bn in beat_next if bn is not None),
                default=beats
            )
            # Add a rest
            rest += next_beat - beat
            # Add to output
            elements_out.extend(out)
            # print(f"concurrent notes: {concurrent_notes}")
            # print(f"beat: {beat}")
            # print(f"out: {out}")
            # print(f"next beat: {next_beat}")
            # print(f"beats next: {beat_next}")
            # print(f"elements_out: {elements_out}")
            # print(f"rest: {rest}")
        if rest:
            elements_out.append(Rest(rest))
        # print(f"FINAL elements_out: {elements_out}")
        return Measure(tuple(elements_out), beats=beats)

def interpret_symbols(symbols: str) -> tuple[float, str, str, bool]:
    """Return duration, pitch, accent, and rest
       from a single set of symbols. """
    if not symbols:
        raise ValueError("Invalid (empty) symbol.")
    elif symbols.startswith('3'):
        duration, pitch, accent, rest = interpret_symbols(symbols[1:])
        duration *= 2/3
    elif symbols[-1] in accent_symbols:
        duration, pitch, accent, rest = interpret_symbols(symbols[:-1])
        accent = symbols[-1]
    elif symbols[-1] in pitch_symbols:
        duration, pitch, accent, rest = interpret_symbols(symbols[:-1])
        pitch += symbols[-1]
    else:
        if any(
            s not in symbol_duration 
            for s in symbols
        ):
            raise ValueError("Invalid symbol.")
        if any(
            s1 in rest_duration and s2 in note_duration 
            for s1 in symbols for s2 in symbols
        ):
            raise ValueError("Cannot mix note and rest symbols.")
        rest: bool = symbols[0] in rest_duration
        duration = sum(
            (rest_duration if rest else note_duration)[s]
            for s in symbols
        )
        pitch, accent = "", ""
        #print(symbols, duration, pitch, accent, rest)
    return duration, pitch, accent, rest

def interpret_notation(
    create_note: Callable[[str], BaseNote],
    notation: str, 
    beats: int = 4,
) -> tuple[Measure, ...]:
    """Return measures from notation using create_note."""
    def create_measure(measure):
        return Measure(
            tuple(
                create_note(symbols)
                for symbols in measure.split()
            ),
            beats = beats,
        )
    return tuple(
        create_measure(measure)
        for measure in notation.split('|')
    )

def expand_sequences(
        measures: tuple[Measure, ...],
):
    """Populate SequenceMeasures with ActionNotes."""
    for measure in measures:
        if not isinstance(measure, SequenceMeasure):
            continue
        assert isinstance(measure, SequenceMeasure)
        measure.elements = tuple(
            ActionNote(
                duration=measure.step_duration,
                actions=(
                    environment.light(
                        next(measure.seq.iter),
                        measure.special,
                    ),
                )
            )
            for _ in range(measure.count)
        )

def play(
        *measures: Measure,
        pace: float,
    ):
    """Play a series of measures."""
    expand_sequences(measures)
    for measure in measures:
        beat = 0
        for element in measure.elements:
            start = time.time()
            if isinstance(element, NoteGroup):
                for note in element.notes:
                    note.play()
                duration = 0
            else:
                assert isinstance(element, BaseNote)
                note.play()
                duration = element.duration
            wait_dur = (duration) * pace
            environment.wait(wait_dur, time.time() - start)
            beat += duration
            print(beat, duration, measure.beats)
        wait_dur = max(0, measure.beats - beat) * pace
        environment.wait(wait_dur, 0)
