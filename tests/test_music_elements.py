
from music import *
from sequence_defs import *

def test_SequenceMeasure():
    sm = SequenceMeasure(build_rows, 0.5, 8, None, beats=4)
    results = [next(sm.seq.iter) for r in range(8)]
    for i in range(8):
        assert results[i] != results [(i + 1) % 8]
