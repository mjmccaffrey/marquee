from music import *
import pytest

def test_interpret_symbols_duration():
    assert interpret_symbols('♩') == (1, "", "", False)
    assert interpret_symbols('♩𝅘𝅥𝅯') == (1.25, "", "", False)
    assert interpret_symbols('3♪') == (1/3, "", "", False)
    assert interpret_symbols('𝄻') == (4, "", "", True)
    with pytest.raises(ValueError, match="Cannot mix"):
        interpret_symbols('♩𝄻>')
    with pytest.raises(ValueError, match="empty"):
        interpret_symbols('A')

def test_interpret_symbols_accent():
    assert interpret_symbols('♪^') == (0.5, "", "^", False)
    assert interpret_symbols('3♩>') == (2/3, "", ">", False)
    assert interpret_symbols('3♩A>') == (2/3   , "A", ">", False)

def test_interpret_symbols_pitch():
    with pytest.raises(ValueError, match="Invalid symbol."):
        interpret_symbols('3♩q>')
    assert interpret_symbols('♩A>') == (1, "A", ">", False)
    assert interpret_symbols('♩Ad>') == (1, "Ad", ">", False)

def test_interpret_notation_measure_count():
    def rest(s: str) -> Rest:
        return Rest(1)
    assert len(interpret_notation(rest, "")) == 0
    assert len(interpret_notation(rest, "|||")) == 0
    assert len(interpret_notation(rest, "♩")) == 1
    assert len(interpret_notation(rest, "♩ ♩ ♩ | ♩ ♩", beats=5)) == 2
    assert all(
        isinstance(o, Measure) 
        for o in interpret_notation(rest, "♩ ♩ ♩ | ♩ ♩", beats=5)
    )

def test_interpret_notation_measure_length():
    def rest(s: str) -> Rest:
        return Rest(1)
    assert all(
        o.beats == 5 
        for o in interpret_notation(rest, "♩ ♩ ♩ | ♩ ♩", beats=5)
    )

def test_interpret_notation_empty_measures():
    def rest(s: str) -> Rest:
        return Rest(1)
    measures = interpret_notation(rest, " | ♩ ♩ ♩ | ♩ ♩ | ")
    assert len(measures) == 2
    assert len(measures[0].elements) == 3
    assert len(measures[1].elements) == 2
