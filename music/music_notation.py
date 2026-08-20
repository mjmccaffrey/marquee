"""Marquee Lighted Sign Project - music_notation"""

# NOTE: This module does not truly support sustained notes.
#       Essentially all instruments / notes 
#       in the music package are percussive, 
#       and in effect have zero length.
#       Exceptions are BellSet, Ringer, and Buzzer,
#       whose play methods schedule the 'release'
#       of the played note(s).

from collections.abc import Callable, Iterator
from enum import IntEnum
from itertools import cycle
import logging

from .music_elements import (
    ActionNote, Note, BellNote, DrumNote, 
    LightNote, LightChannelNote, LightRelayNote,
    DinNote, BuzzerNote, RingerNote, Rest,
)
from .music_collections import Measure, Part
from .music_processing import part

log = logging.getLogger('marquee.' + __name__)

note_duration_map: dict[str, float] = {
    '𝅝': 4,      '𝅗𝅥': 2,       '♩': 1,
    '♪': 0.5,    '𝅘𝅥𝅯': 0.25,   '𝅘𝅥𝅰': 0.125,  
    '𝅘𝅥𝅱': 0.0625, '𝅘𝅥𝅲': 0.03125,
}
rest_duration_map: dict[str, float] = {
    '𝄻': 4,     '𝄼': 2,       '𝄽': 1,
    '𝄾': 0.5,    '𝄿': 0.25,   '𝅀': 0.125,  
    '𝅁': 0.0625, '𝅂': 0.03125,
}
symbol_duration_map = note_duration_map | rest_duration_map

class Bell(IntEnum):
    e = 7;  d = 6
    c = 5;  b = 4
    a = 3;  G = 2
    # F#
    E = 1;  D = 0

bell_pitch_map = {k: int(v) for k, v in Bell.__members__.items()}
drum_accent_map = {
    '': 0, '-': 1, '>': 2, '^': 3,
}
drum_pitch_map = {
    'h': 0, 'l': 1,
}


def _interpret_symbols(
    symbols: str, 
    accent_map: dict = {},
    pitch_map: dict = {},
) -> tuple[float, set, int, bool]:
    """Return duration, pitches, accent, and is_rest
       from a single set of symbols. """
    def interpret(symbols: str) -> tuple[float, set, int, bool]:
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
                s not in symbol_duration_map 
                for s in symbols
            ):
                raise ValueError(f"Invalid symbol in '{symbols}'.")
            if any(
                s1 in rest_duration_map and s2 in note_duration_map 
                for s1 in symbols for s2 in symbols
            ):
                raise ValueError("Cannot mix note and rest symbols.")
            is_rest: bool = symbols[0] in rest_duration_map
            duration = sum(
                (rest_duration_map if is_rest else note_duration_map)[s]
                for s in symbols
            )
            pitches, accent = set(), 0
        return duration, pitches, accent, is_rest
    return interpret(symbols)


def _each_notation_measure(notation: str) -> Iterator[str]:
    """Yield non-empty measures of notation."""
    for measure in notation.split('|'):
        if measure.replace(' ', ''):
            yield measure


def _interpret_notation(
    create_note: Callable[[str], Note],
    notation: str, 
    beats: int = 4,
) -> tuple[Measure, ...]:
    """Return measures from notation using create_note."""
    def create_measure(measure) -> Measure:
        return Measure(
            tuple(
                create_note(symbols)
                for symbols in measure.split()
            ),
            beats = beats,
        )
    result = tuple(
        create_measure(measure)
        for measure in _each_notation_measure(notation)
    )
    return result


def rest(symbols: str) -> Rest:
    """Validate symbols and return Rest."""
    duration, pitches, accent, is_rest = _interpret_symbols(symbols)
    if pitches or accent:
        raise ValueError("Rest cannot have pitch or accent.")
    return Rest(duration)


def action(
    symbols: str, 
    action: Callable | Iterator[Callable]
) -> ActionNote | Rest:
    """Validate symbols and return ActionNote or Rest."""
    duration, pitches, accent, is_rest = _interpret_symbols(symbols)
    if is_rest:
        return rest(symbols)
    if pitches or accent:
        raise ValueError("Action note cannot have pitch or accent.")
        pass
    if isinstance(action, Iterator):
        action = next(action)
    return ActionNote(duration=duration, action=action)


def actions(
    notation: str, 
    *actions: Callable,
    beats=4,
) -> Part:
    """Produce action part from notation."""
    if not actions:
        actions = (lambda: None, )
    action_cycle = cycle(actions)

    def create_act(symbols: str) -> ActionNote | Rest:
        """Return ActionNote for next action in cycle."""
        return action(symbols, action_cycle)
    
    return part(
        *_interpret_notation(create_act, notation, beats)
    )


def bell(symbols: str) -> BellNote | Rest:
    """Validate symbols and return BellNote or Rest."""
    duration, pitches, accent, is_rest = _interpret_symbols(
        symbols,
        pitch_map=bell_pitch_map
    )
    if is_rest:
        return rest(symbols)
    if accent:
        raise ValueError("Bell note cannot have accent.")
    if not pitches:
        raise ValueError("Bell note must have at least one pitch.")
    return BellNote(duration, pitches=pitches)


def bells(notation: str, beats=4) -> Part:
    """Produce bell part from notation."""
    return part(
        *_interpret_notation(bell, notation, beats)
    )


def drum(symbols: str) -> DrumNote | Rest:
    """Validate symbols and return DrumNote or Rest."""
    duration, pitches, accent, is_rest = _interpret_symbols(
        symbols, 
        accent_map=drum_accent_map,
        pitch_map=drum_pitch_map,
    )
    if is_rest:
        return rest(symbols)
    if not pitches:
        # raise ValueError("Drum note must have at least one pitch.")
        pitches={0, 1}
    return DrumNote(duration, accent=accent, pitches=pitches)


def drums(notation: str, accent: str = '', beats=4) -> "Part":
    """Produce drum part from notation."""
    return part(
        *_interpret_notation(drum, notation, beats),
        accent=drum_accent_map[accent],
    )


def _light(
    note_type: type[LightNote],
    symbols: str, 
    kwargs: dict | Iterator[dict] = {}
) -> LightNote | Rest:
    """Validate symbols and return concrete LightNote or Rest."""
    duration, pitches, accent, is_rest = _interpret_symbols(symbols)
    if is_rest:
        return rest(symbols)
    if pitches or accent:
        raise ValueError("Light / relay note cannot have pitch or accent.")
    if isinstance(kwargs, Iterator):
        kwargs = next(kwargs)
    return note_type(duration, kwargs=kwargs)


def _lights(
    note_type: type[LightNote],
    notation: str, 
    *kwargs: dict,
    beats=4,
) -> Part:
    """Produce lights part from notation."""
    if not kwargs:
        kwargs = ({},)
    kwargs_cycle = cycle(kwargs)

    def create_light(symbols: str) -> LightNote | Rest:
        """Return concrete LightNote."""
        return _light(note_type, symbols, kwargs_cycle)
    
    return part(
        *_interpret_notation(create_light, notation, beats)
    )


def lights(
    notation: str, 
    *kwargs: dict,
    beats=4,
) -> Part:
    """Produce lights part from notation."""
    return _lights(LightChannelNote, notation, *kwargs, beats=beats)


def relays(
    notation: str, 
    *kwargs: dict,
    beats=4,
) -> Part:
    """Produce lights part from notation."""
    return _lights(LightRelayNote, notation, *kwargs, beats=beats)


def _din_note(
    note_type: type[DinNote],
    symbols: str, 
) -> DinNote | Rest:
    """Validate symbols and return concrete DinNote or Rest."""
    duration, pitches, accent, is_rest = _interpret_symbols(symbols)
    if is_rest:
        return rest(symbols)
    if pitches or accent:
        raise ValueError("Buzzer / ringer note cannot have pitch or accent.")
    return note_type(duration)

def _din(
    note_type: type[DinNote],
    notation: str, 
    beats=4,
) -> Part:
    """Produce din part from notation."""

    def create_din(symbols: str) -> DinNote | Rest:
        """Return concrete DinNote."""
        return _din_note(note_type, symbols)

    return part(
        *_interpret_notation(create_din, notation, beats)
    )


def buzzer(
    notation: str, 
    beats=4,
) -> Part:
    """Produce buzzer part from notation."""
    return _din(BuzzerNote, notation, beats=beats)


def ringer(
    notation: str, 
    beats=4,
) -> Part:
    """Produce ringer part from notation."""
    return _din(RingerNote, notation, beats=beats)

