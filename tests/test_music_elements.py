
from music import *
from music import _convert_sustained_notes
from notation import *
from sequences import *

# def test_SequenceMeasure():
#     sm = SequenceMeasure(build_rows, 0.5, 8, None, beats=4)
#     results = [next(sm.seq.iter) for r in range(8)]
#     for i in range(8):
#         assert results[i] != results [(i + 1) % 8]

def test_sustained_notes_1():
    m1 = (Measure((PianoNote(2, False, 'e'),), beats=4),)
    m2 = (Measure((PianoNote(2, False, 'e'), PianoNote(0, True, 'e')), beats=4),)
    _convert_sustained_notes(m1)
    assert m1 == m2
    print()
    print(m1)
    print(m2)
