from music import HIGH, PlayMusicMode
from sequence_defs import *

class Finale(PlayMusicMode):

    def intro(self):
        s = self
        s.Measure(
            s.Note('♩', s.light("01000000000")))
        s.Measure(
            s.Note('♩', self.light("00000000000")))
        s.Measure(
            s.Rest('𝅝'))
        s.Measure(
            s.Note('♩', self.light("11100010000")),
            s.Rest('𝅗𝅥'),
            s.Note('♩', self.light("00000000000")))
        s.Measure(
            s.Note('♪', self.dimmer(HIGH, 7)),
            s.Note('♪', self.dimmer(HIGH, 4)),
            s.Note('♪', self.dimmer(HIGH, 9)),
            s.Note('♪', self.dimmer(HIGH, 1)),
            s.Note('♪', self.dimmer(HIGH, 8)),
            s.Note('♪', self.dimmer(HIGH, 5)),
            s.Note('♪', self.dimmer(HIGH, 2)),
            s.Note('♪', self.dimmer(HIGH, 6)))
        s.Measure(
            s.Note('♪', self.dimmer(HIGH, 0)),
            s.Note('♪', self.dimmer(HIGH, 3)))
        s.Measure()
        s.Measure(
            s.Note('♩', self.light("01000000000")),
            s.Note('♩', self.light("00010000001")),
            s.Note('♩', self.light("01000000000")),
            s.Note('♩', self.light("00010000001")))
        s.Measure(
            s.Note('♩', self.light("01000010000")),
            s.Note('♩', self.light("00010101001")),
            s.Note('♩', self.light("01000010000")),
            s.Note('♩', self.light("00010101001")))
        s.Measure(
            s.Sequence('♩', 4, seq_build_rows, from_top=True))
        s.Measure(
            s.Sequence('♩', 4, seq_build_rows, from_top=True))
        s.Measure(
            s.Sequence('♩', 4, seq_build_rows, from_top=False))
        s.Measure(
            s.Sequence('♩', 4, seq_build_rows, from_top=False))
