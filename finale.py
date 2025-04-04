"""Marquee Lighted Sign Project - finale"""

import sys

from music import PlayMusicMode
from signs import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON, ActionParams
from sequence_defs import *

class Finale(PlayMusicMode):
    """"""

    def execute(self):
        self.test()
        sys.exit()
        self.intro()
        self.body1()
        self.body2()

    def test(self):
        s = self
        s.play_measures(
            s.Measure(
                s.Note('♩', s.relay(0, 1)),
                s.Note('♩', s.relay(0, 1)),
                s.Note('♩', s.relay(0, 1)),
                s.Note('♩', s.relay(0, 1)),
                s.Note('3♪', s.relay(0, 1)),
                s.Note('3♪', s.relay(0, 1)),
                s.Note('3♪', s.relay(0, 1)),
                s.Note('♩', s.relay(0, 1)),
                s.Note('♩', s.relay(0, 1, 2, 3, 4, 5)),
                s.Note('♩', s.relay(0, 1, 2, 3, 4, 5)),
                beats=8,
            ),
            s.Measure(
                s.Note('♪', s.relay(0, 1)),
                s.Note('♪', s.relay(0, 1)),
                s.Note('♪', s.relay(0, 1)),
                s.Note('♪', s.relay(0, 1)),
                s.Note('3𝅘𝅥𝅯', s.relay(0, 1)),
                s.Note('3𝅘𝅥𝅯', s.relay(0, 1)),
                s.Note('3𝅘𝅥𝅯', s.relay(0, 1)),
                s.Note('♪', s.relay(0, 1)),
                s.Note('♪', s.relay(0, 1)),
                s.Note('♪', s.relay(0, 1)),
            )
        )

    def intro(self):
        s = self
        s.play_measures(
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
                beats=16),
            #s.Measure(beats=32),
        )
    
    def body1(self):
        s = self
        s.play_parts(
            s.Part(
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
            )
        )

    def body2(self):
        s = self
        s.play_parts(
            s.Part(
                s.Measure(
                    s.Sequence('♪', 8, seq_rows),
                ),
                s.Measure(
                    s.Sequence('♪', 8, seq_rows),
                ),
                s.Measure(
                    s.Sequence('♪', 3, seq_rows),
                ),
            ),
            s.Part(
                s.Measure(
                    s.Note('♪', s.relay(0, 1)),
                    s.Rest('♪♪'),
                    s.Note('♪', s.relay(0, 1, 2, 3, 4, 5)),
                ),
                s.Measure(
                    s.Note('♪', s.relay(0, 1, 2, 3, 4, 5)),
                ),
                s.Measure(
                    s.Note('♪', s.relay(0, 1)),
                ),
            ),
        )
