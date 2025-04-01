"""Marquee Lighted Sign Project - finale"""

from music import PlayMusicMode
from signs import ALL_HIGH, ALL_OFF, ALL_ON, ALL_LOW, ALL_ON, HIGH, RelayOverride
from sequence_defs import *

class Finale(PlayMusicMode):
    """"""

    def execute(self):
        self.intro()

    def intro(self):
        s = self
        s.play(
            s.Measure(
                s.Note('♩', s.dimmer(ALL_HIGH)),
                s.Rest('𝅗𝅥♩')),
            s.Measure(
                s.Note('♩', s.light("0100000000"))),
            s.Measure(
                s.Note('♩', s.light("0000000000"))),
            s.Measure(
                s.Note('♩', s.light("1110001000")),
                s.Rest('♩♪'),
                s.Note('♩', s.light("0000000000"))),
            s.Measure(
                s.Note('♩', s.dimmer(ALL_LOW)),
                s.Note('♩', s.light(ALL_ON))),
            s.Measure(
                s.Sequence('♩', LIGHT_COUNT, seq_random_once_each, 
                    RelayOverride(action=s.dimmer_seq(100, 2))),
                beats=8),
            s.Measure(beats=8),
            s.Measure(
                s.Rest('𝅗𝅥♩♪𝅘𝅥𝅰'),
                s.Note('𝅘𝅥𝅰', s.relay(10, 11)),
                s.Note('𝅘𝅥𝅰', s.relay(12, 13)),
                s.Note('𝅘𝅥𝅰', s.relay(14, 15)),
            ),
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
            s.Measure(),
            s.Measure(
                s.Sequence('♩', 4, seq_build_rows, from_top=False)),
            s.Measure(),
        )
