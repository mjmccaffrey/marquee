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
    dimmer: Callable[[str], Callable]
    light: Callable[[Any, SpecialParams | None], Callable]
    wait: Callable[[float, float], None]

def set_environment(env: Environment):
    """Called once to link to Player and Sign resources."""
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
        """Play single BaseNote (abstract)."""

@dataclass
class Rest(BaseNote):
    """Musical rest."""
    instrument_class: ClassVar[type[Instrument]] = RestInstrument

    def play(self):
        """Play single rest (do nothing)."""

@dataclass
class ActionNote(BaseNote):
    """Note to execute arbitrary actions."""
    instrument_class: ClassVar[type[Instrument]] = ActionInstrument
    actions: tuple[Callable, ...]

    def play(self):
        """Play single ActionNote."""
        for action in self.actions:
            action()

@dataclass
class BellNote(BaseNote):
    """Note to strike 1 or more bells."""
    instrument_class: ClassVar[type[Instrument]] = BellSet
    pitches: str

    def play(self):
        """Play single BellNote."""
        environment.bell_set.play(self.pitches)

@dataclass
class DrumNote(BaseNote):
    """Note to click & clack relays."""
    instrument_class: ClassVar[type[Instrument]] = DrumSet
    accent: str

    def play(self):
        """Play single DrumNote."""
        environment.drum_set.play(self.accent)

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
    """Defines a measure with a sequence of light events."""
    sequence: Callable
    kwargs: dict[str, Any]
    step_duration: float
    count: int
    special: SpecialParams | None
    beats: int

    def __post_init__(self):
        """Create Sequence component."""
        self.sequence_obj = Sequence(self.sequence, self.kwargs)

@dataclass
class Sequence(Element):
    """Defines a sequence of light patterns."""
    sequence: Callable
    kwargs: dict[str, Any]

    def __post_init__(self):
        """Create Sequence iterator."""
        self.iter = itertools.cycle(self.sequence(**self.kwargs))

@dataclass
class Part(Element):
    """Musical part containing measures."""
    measures: tuple[Measure, ...]
    default_accent: str = ''

    def __post_init__(self):
        """Process measures."""
        if self.default_accent:
            self._apply_accent(self.default_accent, self.measures)

    @staticmethod
    def _apply_accent(accent, measures: tuple[Measure, ...]):
        """Apply default accent (drums only)."""
        for measure in measures:
            for element in measure.elements:
                if isinstance(element, DrumNote) and not element.accent:
                    element.accent = accent

@dataclass
class Section(Element):
    """Musical section containing parts and meta info."""
    parts: tuple[Part, ...]
    beats: int
    tempo: int

    def __post_init__(self):
        """Process parts so they are ready to play."""
        if self.beats is not None:
            self._apply_beats(self.beats, self.parts)
        self._measures = self._prepare_parts(self.parts)

    def play(self):
        """Play already-generated measures comprising Section."""
        play(*self._measures, tempo=self.tempo)

    @staticmethod
    def _apply_beats(beats, parts):
        """Apply default # of beats to all measures in the Section."""
        for part in parts:
            for measure in part.measures:
                measure.beats = beats

    @staticmethod
    def _prepare_parts(
            parts: tuple[Part, ...], 
    ) -> list[Measure]:
        """ Expand SequenceMeasures.
            Make all parts the same length.
            Merge parts into single sequence of Measures."""
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
        beat, next_beat, rest_dur = 0.0, 0.0, 0.0
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
                out.append(Rest(rest_dur))
                rest_dur = 0.0
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
            rest_dur += next_beat - beat
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
            elements_out.append(Rest(rest_dur))
        # print(f"FINAL elements_out: {elements_out}")
        return Measure(tuple(elements_out), beats=beats)

def interpret_symbols(symbols: str) -> tuple[float, str, str, bool]:
    """Return duration, pitch, accent, and is_rest
       from a single set of symbols. """
    symbols = symbols.replace(' ', '')
    if not symbols:
        raise ValueError("Invalid (empty) symbol.")
    elif symbols.startswith('3'):
        duration, pitch, accent, is_rest = interpret_symbols(symbols[1:])
        duration *= 2/3
    elif symbols[-1] in accent_symbols:
        duration, pitch, accent, is_rest = interpret_symbols(symbols[:-1])
        accent = symbols[-1]
    elif symbols[-1] in pitch_symbols:
        duration, pitch, accent, is_rest = interpret_symbols(symbols[:-1])
        pitch += symbols[-1]
    else:
        if any(
            s not in symbol_duration 
            for s in symbols
        ):
            raise ValueError(f"Invalid symbol in '{symbols}'.")
        if any(
            s1 in rest_duration and s2 in note_duration 
            for s1 in symbols for s2 in symbols
        ):
            raise ValueError("Cannot mix note and rest symbols.")
        is_rest: bool = symbols[0] in rest_duration
        duration = sum(
            (rest_duration if is_rest else note_duration)[s]
            for s in symbols
        )
        pitch, accent = "", ""
        #print(symbols, duration, pitch, accent, is_rest)
    return duration, pitch, accent, is_rest

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
                        next(measure.sequence_obj.iter),
                        measure.special,
                    ),
                )
            )
            for _ in range(measure.count)
        )

def play(
        *measures: Measure,
        tempo: int,
):
    """Play a series of measures."""
    expand_sequences(measures)
    pace = 60 / tempo
    for measure in measures:
        beat = 0
        start = time.time()
        for element in measure.elements:
            if isinstance(element, NoteGroup):
                for note in element.notes:
                    note.play()
                duration = 0
            else:
                assert isinstance(element, BaseNote)
                element.play()
                duration = element.duration
                if duration:
                    wait_dur = (duration) * pace
                    environment.wait(wait_dur, time.time() - start)
                    start = time.time()
            beat += duration
            if beat > measure.beats:
                raise ValueError("Too many actual beats in measure.")
        # Play implied rests at end of measure
        wait_dur = (measure.beats - beat) * pace 
        #print(f"wait_dur: {wait_dur}")
        environment.wait(wait_dur, time.time() - start)

def rest(symbols: str) -> Rest:
    """Validate symbols and return Rest."""
    duration, pitch, accent, is_rest = interpret_symbols(symbols)
    if pitch or accent:
        raise ValueError("Rest cannot have pitch or accent.")
    return Rest(duration)

def act(symbols: str, *actions: Callable, pre_call_actions: bool = False) -> ActionNote | Rest:
    """Validate symbols and return ActionNote or Rest."""
    duration, pitch, accent, is_rest = interpret_symbols(symbols)
    if is_rest:
        return rest(symbols)
    if pitch or accent:
        # raise ValueError("Action note cannot have pitch or accent.")
        pass
    if pre_call_actions:
        actions = tuple(action() for action in actions)
    return ActionNote(duration, actions)

def act_part(
        notation: str, 
        *actions: Callable,
        beats=4,
) -> Part:
    """"""
    def func(symbols: str):
        return act(symbols, lambda: next(acts), pre_call_actions=True)
    acts = iter(actions)
    return part(
        *interpret_notation(func, notation, beats)
    )

def sequence_part(
        *segments: tuple[Callable[[str], ActionNote | Rest], str],
        beats=4
) -> Part:
    """Produce sequence part from notation."""
    return part(
        *tuple(
            measure
            for create_note, notation in segments
            for measure in interpret_notation(create_note, notation, beats)
        )
    )

def bell(symbols: str) -> BellNote | Rest:
    """Validate symbols and return BellNote or Rest."""
    duration, pitch, accent, is_rest = interpret_symbols(symbols)
    if is_rest:
        return rest(symbols)
    if accent:
        raise ValueError("Bell note cannot have accent.")
    return BellNote(duration, pitch)

def bell_part(notation: str, beats=4) -> Part:
    """Produce bell part from notation."""
    return part(
        *interpret_notation(bell, notation, beats)
    )

def drum(symbols: str) -> DrumNote | Rest:
    """Validate symbols and return DrumNote or Rest."""
    duration, pitch, accent, is_rest = interpret_symbols(symbols)
    if is_rest:
        return rest(symbols)
    if pitch:
        raise ValueError("Drum note cannot have pitch.")
    return DrumNote(duration, accent)

def drum_part(notation: str, accent: str = '', beats=4) -> "Part":
    """Produce drum part from notation."""
    return part(
        *interpret_notation(drum, notation, beats),
        accent=accent,
    )

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
    return Section(
        parts, 
        beats=beats,
        tempo=tempo,
    )

def sequence(
    seq: Callable,
    special: SpecialParams | None = None,
    **kwargs,
) -> Callable[[str], ActionNote | Rest]:
    """Return callable to effect each step in sequence."""
    sequence_obj = Sequence(seq, kwargs)
    def func(s: str):
        return act(
            s, lambda: environment.light(next(sequence_obj.iter), special),
            pre_call_actions=True,
        )
    return func

def sequence_measure(
    symbols: str,
    count: int,
    sequence: Callable,
    special: SpecialParams | None = None,
    beats: int = 4,
    **kwargs,
) -> SequenceMeasure:
    """Produce a SequenceMeasure."""
    step_duration, _, _, _ = interpret_symbols(symbols)
    return SequenceMeasure(
        elements=(),
        beats=beats,
        sequence=sequence, 
        kwargs=kwargs,
        step_duration=step_duration, 
        count=count, 
        special=special,
    )

def dimmer(pattern: str) -> Callable:
    """"""
    return environment.dimmer(pattern)

def light(
    pattern: Any,
    special: SpecialParams | None = None,
) -> Callable:
    """"""
    return environment.light(pattern, special)
