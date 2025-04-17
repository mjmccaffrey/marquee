"""Marquee Lighted Sign Project - music"""

from abc import ABC, abstractmethod
from collections.abc import Callable
import itertools

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

class Element(ABC):
    """Base for all musical items."""
    @abstractmethod
    def __init__(self):
        super().__init__()
    def __str__(self):
        return f"Element"
    def __repr__(self):
        return f"<{self}>"
    def __eq__(self, other):
        return (
            isinstance(other, type(self)) and
            str(self) == str(other)
        )
    
class BaseNote(Element):
    """Base for all musical notes."""
    @abstractmethod
    def __init__(
        self, 
        instrument_class: type[Instrument],
        duration: float,
    ):
        super().__init__()
        self.instrument_class = instrument_class
        self.duration = duration
    def __str__(self):
        return f"BaseNote {self.instrument_class} {self.duration}"
    @abstractmethod
    def execute(self):
        """"""

class Rest(BaseNote):
    """Musical rest."""
    def __init__(
        self, 
        duration: float,
    ):
        super().__init__(RestInstrument, duration)
    def __str__(self):
        return f"Rest {self.duration}"
    def execute(self):
        """"""

class ActionNote(BaseNote):
    """Note to execute arbitrary actions."""
    def __init__(
        self, 
        duration: float,
        actions: tuple[Callable, ...],
    ):
        super().__init__(ActionInstrument, duration)
        assert actions, "Note must have at least 1 action."
        self.actions = actions
    def __str__(self):
        return f"ActionNote {self.duration} {self.actions}"
    def execute(self):
        for action in self.actions:
            action()

class BellNote(BaseNote):
    """Note to strike 1 or more bells."""
    def __init__(
        self, 
        duration: float,
        #
        pitches: str,
    ):
        super().__init__(BellSet, duration)
        self.pitches = pitches
    def __str__(self):
        return f"BellNote {self.duration} {self.pitches}"
    def execute(self):
        raise NotImplementedError

class DrumNote(BaseNote):
    """Note to click relays."""
    def __init__(
        self, 
        duration: float,
        #
        accent: str,
    ):
        super().__init__(DrumSet, duration)
        self.accent = accent
    def __str__(self):
        return f"DrumNote {self.duration} {self.accent}"
    def execute(self):
        raise NotImplementedError

class NoteGroup(Element):
    """Contains notes to play concurrently."""
    def __init__(
        self, 
        notes: tuple[BaseNote, ...],
    ):
        """"""
        super().__init__()
        self.notes = notes
    def __str__(self):
        return f"NoteGroup {self.notes}"
    
class Measure(Element):
    """Musical measure containing notes."""
    def __init__(
        self, 
        elements: tuple[Element, ...],
        beats: int,
    ):
        """"""
        super().__init__()
        self.elements = elements
        self.beats = beats
    def __str__(self):
        return f"Measure {self.elements} {self.beats}"
    
class SequenceMeasure(Measure):
    """Will be expended to a Measure with notes."""
    def __init__(
        self,
        sequence: Callable,
        step_duration: float, 
        count: int,
        special: SpecialParams | None,
        beats: int,
        **kwargs,
    ):
        super().__init__((), beats)
        self.seq = Sequence(sequence, **kwargs)
        self.step_duration = step_duration
        self.count = count
        self.special = special
    def __str__(self):
        return f"SequenceMeasure {self.beats}"

class Part(Element):
    """Musical part containing measures."""
    def __init__(
        self, 
        measures: tuple[Measure, ...],
    ):
        super().__init__()
        self.measures = measures
    def __str__(self):
        return f"Part {self.measures}"

class Sequence(Element):
    """"""
    def __init__(
        self,
        sequence: Callable,
        **kwargs,
    ):
        super().__init__()
        self.sequence = sequence
        self.kwargs = kwargs
        self.iter = itertools.cycle(sequence(**kwargs))

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
                    #print(f"part: {i} OUT OF ELEMENTS")
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
        if beat >= beats:
            raise ValueError("Too many actual beats in measure.")
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
