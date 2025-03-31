from music import HIGH, PlayMusicMode
from signs import ALL_OFF, ALL_LOW
from sequence_defs import *

class Finale(PlayMusicMode):

    def execute(self):
        s.intro()

    def intro(self):
        s = self
        s.player.sign.set_dimmers("AAAAAAAAAA")
        print(3)
        s.play(
            s.Measure(
                s.Note('♩', s.light("01000000000"))),
            s.Measure(
                s.Note('♩', s.light("00000000000"))),
            s.Measure(
                s.Rest('𝅝')),
            s.Measure(
                s.Note('♩', s.light("11100010000")),
                s.Rest('𝅗𝅥'),
                s.Note('♩', s.light("00000000000"))),
            s.Measure(),
            s.Measure(
                s.Note('♩', s.light("01000000000")),
                s.Note('♩', s.light("00010000001")),
                s.Note('♩', s.light("01000000000")),
                s.Note('♩', s.light("00010000001"))),
            s.Measure(
                s.Note('♩', s.light("01000010000")),
                s.Note('♩', s.light("00010101001")),
                s.Note('♩', s.light("01000010000")),
                s.Note('♩', s.light("00010101001"))),
            s.Measure(
                s.Sequence('♩', 4, seq_build_rows, from_top=True)),
            s.Measure(
                s.Sequence('♩', 4, seq_build_rows, from_top=True)),
            s.Measure(
                s.Sequence('♩', 4, seq_build_rows, from_top=False)),
            s.Measure(
                s.Sequence('♩', 4, seq_build_rows, from_top=False)),
        )
