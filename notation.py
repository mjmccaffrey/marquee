"""Marquee Lighted Sign Project - notation"""

from collections.abc import Callable, Iterator
from music import (
    ActionNote, BaseNote, BellNote, DrumNote,
    Measure, Part, Rest,
    Sequence, SequenceMeasure, SpecialParams,
    light, part,
)
from instruments import BellSet, DrumSet

note_duration: dict[str, float] = {
    '𝅝': 4,     '𝅗𝅥': 2,      '♩': 1,
    '♪': 0.5,   '𝅘𝅥𝅯': 0.25,  '𝅘𝅥𝅰': 0.125,
}
rest_duration: dict[str, float] = {
    '𝄻': 4,    '𝄼': 2,      '𝄽': 1,
    '𝄾': 0.5,   '𝄿': 0.25,  '𝅀': 0.125,
}
symbol_duration = note_duration | rest_duration
drum_accent_map = {
    '': 0, '-': 1, '>': 2, '^': 3,
}

def _interpret_symbols(
    symbols: str, 
    accent_map: dict = {},
    pitch_map: dict = {},
) -> tuple[float, set, int, bool]:
    """Return duration, pitches, accent, and is_rest
       from a single set of symbols. """
    def interpret(symbols: str):
        print(symbols)
        symbols = symbols.replace(' ', '')
        if not symbols:
            raise ValueError("Invalid (empty) symbol.")
        elif symbols[0] == '3':
            duration, pitches, accent, is_rest = interpret(symbols[1:])
            duration *= 2/3
        elif symbols[-1] in accent_map:
            duration, pitches, accent, is_rest = interpret(symbols[:-1])
            accent = accent_map[symbols[-1]]
        elif symbols[0] in pitch_map:
            duration, pitches, accent, is_rest = interpret(symbols[1:])
            pitches = {pitch_map[symbols[0]]} | pitches
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
            pitches, accent = set(), 0
            #print(symbols, duration, pitches, accent, is_rest)
        return duration, pitches, accent, is_rest
    return interpret(symbols)

def _each_notation_measure(notation: str) -> Iterator[str]:
    """Yield non-empty measures of notation."""
    for measure in notation.split('|'):
        if measure.replace(' ', ''):
            yield measure

def _interpret_notation(
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
        for measure in _each_notation_measure(notation)
    )

def rest(symbols: str) -> Rest:
    """Validate symbols and return Rest."""
    duration, pitches, accent, is_rest = _interpret_symbols(symbols)
    if pitches or accent:
        raise ValueError("Rest cannot have pitch or accent.")
    return Rest(duration)

def act(
        symbols: str, 
        *actions: Callable, 
        pre_call_actions: bool = False,
    ) -> ActionNote | Rest:
    """Validate symbols and return ActionNote or Rest."""
    duration, pitches, accent, is_rest = _interpret_symbols(symbols)
    if is_rest:
        return rest(symbols)
    if pitches or accent:
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
    """Produce act part from notation."""
    def func(symbols: str):
        return act(symbols, lambda: next(acts), pre_call_actions=True)
    acts = iter(actions)
    return part(
        *_interpret_notation(func, notation, beats)
    )

def bell(symbols: str) -> BellNote | Rest:
    """Validate symbols and return BellNote or Rest."""
    duration, pitches, accent, is_rest = _interpret_symbols(
        symbols,
        pitch_map={
            '-': 1, '>': 2, '^': 3,
        }
    )
    if is_rest:
        return rest(symbols)
    if accent:
        raise ValueError("Bell note cannot have accent.")
    if not pitches:
        raise ValueError("Bell note must have at least one pitch.")
    return BellNote(duration, pitches)

def bell_part(notation: str, beats=4) -> Part:
    """Produce bell part from notation."""
    return part(
        *_interpret_notation(bell, notation, beats)
    )

def drum(symbols: str) -> DrumNote | Rest:
    """Validate symbols and return DrumNote or Rest."""
    duration, pitches, accent, is_rest = _interpret_symbols(
        symbols, 
        accent_map=drum_accent_map,
        pitch_map={
            'h': 0, 'l': 1,
        }
    )
    if is_rest:
        return rest(symbols)
    if not pitches:
        raise ValueError("Drum note must have at least one pitch.")
    return DrumNote(duration, accent, pitches)

def drum_part(notation: str, accent: str = '', beats=4) -> "Part":
    """Produce drum part from notation."""
    return part(
        *_interpret_notation(drum, notation, beats),
        accent=drum_accent_map[accent],
    )

def sequence_measure(
    symbols: str,
    count: int,
    sequence: Callable,
    special: SpecialParams | None = None,
    beats: int = 4,
    **kwargs,
    ) -> SequenceMeasure:
    """Produce a SequenceMeasure."""
    step_duration, _, _, _ = _interpret_symbols(symbols)
    return SequenceMeasure(
        elements=(),
        beats=beats,
        sequence=sequence, 
        kwargs=kwargs,
        step_duration=step_duration, 
        count=count, 
        special=special,
    )

def sequence_part(
        notation: str, 
        *sequences: Sequence,
        beats=4,
    ) -> Part:
    """Produce sequence part from notation."""

    def sequence_gen():
        """Return each sequence in order."""
        for sequence in sequences:
            for _ in range(sequence.measures):
                yield sequence
        while True:
            yield sequence

    def func(s: str) -> ActionNote | Rest:
        """Return a callable that returns an ActionNote."""
        return act(
            s, 
            lambda: light(
                next(sequence.iter), 
                sequence.special,
            ),
            pre_call_actions=True,
        )
    each_sequence = sequence_gen()
    measures = []
    for notation in _each_notation_measure(notation):
        sequence = next(each_sequence)
        measure_tuple = _interpret_notation(func, notation, beats)
        assert len(measure_tuple) == 1
        measures.append(measure_tuple[0])
    return part(*measures)
