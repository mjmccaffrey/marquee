from notation import *
from notation import _interpret_notation, _interpret_symbols
import pytest

a = {
    '-': 1, '>': 2, '^': 3,
}
p = {
    'e': 7, 'd': 6,
    'c': 5, 'b': 4,
    'a': 3, 'G': 2, 
    # F#
    'E': 1, 'D': 0,
}

def test__interpret_symbols_duration():
    assert _interpret_symbols('♩') == (1, set(), 0, False)
    assert _interpret_symbols('♩𝅘𝅥𝅯') == (1.25, set(), 0, False)
    assert _interpret_symbols('3♪') == (1/3, set(), 0, False)
    assert _interpret_symbols('𝄻') == (4, set(), 0, True)
    with pytest.raises(ValueError, match="Cannot mix"):
        _interpret_symbols('♩𝄻')
    with pytest.raises(ValueError, match="empty"):
        _interpret_symbols('A', pitch_map=p)

def test__interpret_symbols_accent():
    assert _interpret_symbols('♪^', accent_map=a) == (0.5, set(), 3, False)
    assert _interpret_symbols('3♩>', accent_map=a) == (2/3, set(), 2, False)
    assert _interpret_symbols('A3♩>', accent_map=a, pitch_map=p) == (2/3, {3}, 2, False)

def test__interpret_symbols_pitch():
    with pytest.raises(ValueError, match="Invalid symbol."):
        _interpret_symbols('q3♩>', accent_map=a, pitch_map=p)
    assert _interpret_symbols('A♩>', accent_map=a, pitch_map=p) == (1, {3}, 2, False)
    assert _interpret_symbols('aD♩>', accent_map=a, pitch_map=p) == (1, {4, 0}, 2, False)

def test__interpret_notation_measure_count():
    def rest(s: str) -> Rest:
        return Rest(1)
    assert len(_interpret_notation(rest, "")) == 0
    assert len(_interpret_notation(rest, "|||")) == 0
    assert len(_interpret_notation(rest, "♩")) == 1
    assert len(_interpret_notation(rest, "♩ ♩ ♩ | ♩ ♩", beats=5)) == 2
    assert all(
        isinstance(o, Measure) 
        for o in _interpret_notation(rest, "♩ ♩ ♩ | ♩ ♩", beats=5)
    )

def test__interpret_notation_measure_length():
    def rest(s: str) -> Rest:
        return Rest(1)
    assert all(
        o.beats == 5 
        for o in _interpret_notation(rest, "♩ ♩ ♩ | ♩ ♩", beats=5)
    )

def test__interpret_notation_empty_measures():
    def rest(s: str) -> Rest:
        return Rest(1)
    measures = _interpret_notation(rest, " | ♩ ♩ ♩ | ♩ ♩ | ")
    assert len(measures) == 2
    assert len(measures[0].elements) == 3
    assert len(measures[1].elements) == 2
