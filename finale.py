from music import HIGH, PlayMusicMode
from signs import ALL_OFF, ALL_LOW
from sequence_defs import *

class Finale(PlayMusicMode):

    def execute(self):
        self.intro()

    def intro(self):
        s = self
        s.player.sign.set_dimmers("AAAAAAAAAA")
        print(3)
        s.play(
            s.Measure(
                s.Note('♩', s.light("0100000000"))),
            s.Measure(
                s.Note('♩', s.light("00000000000"))),
            s.Measure(),
            s.Measure(
                s.Note('♩', s.light("1110001000")),
                s.Rest('♩'),
                s.Rest('♪'),
                s.Note('♩', s.light("0000000000"))),
            s.Measure(),
            s.Measure(
                s.Note('♩', s.light("0100000000")),
                s.Note('♩', s.light("0001000001")),
                s.Note('♩', s.light("0100000000")),
                s.Note('♩', s.light("0101000001"))),
            s.Measure(
                s.Note('♩', s.light("0100001000")),
                s.Note('♩', s.light("0101100011")),
                s.Note('♩', s.light("0100001000")),
                s.Note('♩', s.light("0101100011"))),
            s.Measure(
                s.Sequence('♩', 4, seq_build_rows, from_top=True)),
            s.Measure(
                s.Sequence('♩', 4, seq_build_rows, from_top=True)),
            s.Measure(
                s.Sequence('♩', 4, seq_build_rows, from_top=False)),
            s.Measure(
                s.Sequence('♩', 4, seq_build_rows, from_top=False)),
        )
