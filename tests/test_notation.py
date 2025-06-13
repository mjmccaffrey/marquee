from notation import *
from notation import _interpret_notation, _interpret_symbols
import pytest

def test__interpret_symbols_duration():
    assert _interpret_symbols('♩') == (1, "", "", False)
    assert _interpret_symbols('♩𝅘𝅥𝅯') == (1.25, "", "", False)
    assert _interpret_symbols('3♪') == (1/3, "", "", False)
    assert _interpret_symbols('𝄻') == (4, "", "", True)
    with pytest.raises(ValueError, match="Cannot mix"):
        _interpret_symbols('♩𝄻>')
    with pytest.raises(ValueError, match="empty"):
        _interpret_symbols('A')

def test__interpret_symbols_accent():
    assert _interpret_symbols('♪^') == (0.5, "", "^", False)
    assert _interpret_symbols('3♩>') == (2/3, "", ">", False)
    assert _interpret_symbols('3♩A>') == (2/3   , "A", ">", False)

def test__interpret_symbols_pitch():
    with pytest.raises(ValueError, match="Invalid symbol."):
        _interpret_symbols('3♩q>')
    assert _interpret_symbols('♩A>') == (1, "A", ">", False)
    assert _interpret_symbols('♩Ad>') == (1, "Ad", ">", False)

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
