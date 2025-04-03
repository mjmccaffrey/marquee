"""Marquee Lighted Sign Project - finale"""

from music import PlayMusicMode
from signs import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON, ActionParams
from sequence_defs import *

class Finale(PlayMusicMode):
    """"""

    def execute(self):
        self.intro()
        self.body()

    def intro(self):
        s = self
        s.play(
            s.Measure(
                s.Note('♩', s.light(ALL_OFF)),
                s.Note('♩', s.dimmer(ALL_HIGH)),
                s.Rest('𝅗𝅥'),
            ),
            s.Measure(
                s.Note('♩', s.light("0100000000")),
            ),
            s.Measure(
                s.Note('♩', s.light("0000000000")),
            ),
            s.Measure(
                s.Note('♩', s.light("1110001000")),
                s.Rest('♩𝅘𝅥𝅯'),
                s.Note('♩', s.light("0000000000")),
                s.Note('♩', s.dimmer(ALL_LOW)),
            ),
            s.Measure(
                s.Rest('♩'),
                s.Note('♩', s.light(ALL_ON)),
            ),
            s.Measure(
                s.Sequence('♩', LIGHT_COUNT, seq_random_once_each, 
                    ActionParams(action=s.dimmer_seq(100, 2))),
                beats=8),
            s.Measure(beats=8),
        )
    
    def body(self):
        s = self
        s.play(
            s.Measure(
                s.Rest('𝅗𝅥♩♪𝅘𝅥𝅰'),
                s.Note('𝅘𝅥𝅰', s.relay(0, 1)),
                s.Note('𝅘𝅥𝅰', s.relay(2, 3)),
                s.Note('𝅘𝅥𝅰', s.relay(4, 5)),
            ),
            s.Measure(
                s.Sequence('♪', 8, seq_rotate, 
                    pattern="0100001000", clockwise=True),
            ),
            s.Measure(
                s.Sequence('♪', 8, seq_rotate, 
                    pattern="0100001000", clockwise=False),
            ),
            s.Measure(
                s.Note('♪', s.light_seq(seq_rows), s.relay(0, 1)),
                s.Note('♪', s.light_seq(),),
                s.Note('♪', s.light_seq(),),
                s.Note('♪', s.light_seq(),),
                beats=2,
            ),
            s.Measure(
                s.Note('♪', s.light_seq(seq_rows), s.relay(0, 1)),
                s.Note('♪', s.light_seq()),
                s.Note('♪', s.light_seq()),
                s.Note('♪', s.light_seq(), s.relay(0, 1, 2, 3, 4, 5)),
                beats=2,
            ),
            s.Measure(
                s.Note('♪', s.light_seq(seq_rows), s.relay(0, 1, 2, 3, 4, 5)),
                s.Note('♪', s.light_seq()),
                s.Note('♪', s.light_seq()),
                s.Note('♪', s.light_seq()),
                beats=2,
            ),
            s.Measure(
                s.Note('♪', s.light_seq(seq_rows), s.relay(0, 1)),
                s.Note('♪', s.light_seq()),
                s.Note('♪', s.light_seq()),
                # s.Note('♪', s.light("0000011100"), s.relay(2, 3)),
                beats=2,
            ),
            s.Measure(),
            s.Measure(),
        )
