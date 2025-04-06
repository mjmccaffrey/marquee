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
        assert s.interpret_symbols('♩') == (1, 0, None)
        assert s.interpret_symbols('♩𝅘𝅥𝅯') == (1.25, 0, None)
        assert s.interpret_symbols('3♪') == (0.75, 0, None)
        assert s.interpret_symbols('♪^') == (0.5, 8, None)
        assert s.interpret_symbols('3♩>') == (1.5, 6, None)
        assert s.interpret_symbols('3♩>A') == (1.5, 3, 6)
        s.play_measures(
            s.measure(
                s.note('♩', s.relay(0, 1)),
                s.note('♩', s.relay(0, 1)),
                s.note('♩', s.relay(0, 1)),
                s.note('♩', s.relay(0, 1)),
                s.note('3♪', s.relay(0, 1)),
                s.note('3♪', s.relay(0, 1)),
                s.note('3♪', s.relay(0, 1)),
                s.note('♩', s.relay(0, 1)),
                s.note('♩', s.relay(0, 1, 2, 3, 4, 5)),
                s.note('♩', s.relay(0, 1, 2, 3, 4, 5)),
                beats=8,
            ),
            s.measure(
                s.note('♪', s.relay(0, 1)),
                s.note('♪', s.relay(0, 1)),
                s.note('♪', s.relay(0, 1)),
                s.note('♪', s.relay(0, 1)),
                s.note('3𝅘𝅥𝅯', s.relay(0, 1)),
                s.note('3𝅘𝅥𝅯', s.relay(0, 1)),
                s.note('3𝅘𝅥𝅯', s.relay(0, 1)),
                s.note('♪', s.relay(0, 1)),
                s.note('♪', s.relay(0, 1)),
                s.note('♪', s.relay(0, 1)),
            )
        )

    def intro(self):
        s = self
        s.play_measures(
            s.measure(
                s.note('♩', s.light(ALL_OFF)),
                s.note('♩', s.dimmer(ALL_HIGH)),
                s.rest('𝅗𝅥'),
            ),
            s.measure(
                s.note('♩', s.light("0100000000")),
            ),
            s.measure(
                s.note('♩', s.light("0000000000")),
            ),
            s.measure(
                s.note('♩', s.light("1110001000")),
                s.rest('♩𝅘𝅥𝅯'),
                s.note('♩', s.light("0000000000")),
                s.note('♩', s.dimmer(ALL_LOW)),
            ),
            s.measure(
                s.rest('♩'),
                s.note('♩', s.light(ALL_ON)),
            ),
            s.measure(
                s.sequence('♩', LIGHT_COUNT, seq_random_once_each, 
                    ActionParams(action=s.dimmer_seq(100, 2))),
                beats=16),
            #s.measure(beats=32),
        )
    
    def body1(self):
        s = self
        s.play_parts(
            s.part(
                s.measure(
                    s.rest('𝅗𝅥♩♪𝅘𝅥𝅰'),
                    s.note('𝅘𝅥𝅰', s.relay(0, 1)),
                    s.note('𝅘𝅥𝅰', s.relay(2, 3)),
                    s.note('𝅘𝅥𝅰', s.relay(4, 5)),
                ),
                s.measure(
                    s.sequence('♪', 8, seq_rotate, 
                        pattern="0100001000", clockwise=True),
                ),
                s.measure(
                    s.sequence('♪', 8, seq_rotate, 
                        pattern="0100001000", clockwise=False),
                ),
            )
        )

    def body2(self):
        s = self
        s.play_parts(
            s.part(
                s.measure(
                    s.sequence('♪', 8, seq_rows),
                ),
                s.measure(
                    s.sequence('♪', 8, seq_rows),
                ),
                s.measure(
                    s.sequence('♪', 3, seq_rows),
                ),
            ),
            s.part(
                s.measure(
                    s.click('♪'),
                    s.rest('♪♪'),
                    s.click('♪^'),
                ),
                s.measure(
                    s.click('♪^'),
                ),
                s.measure(
                    s.click('♪'),
                ),
            ),
        )

    def body3(self):
        s = self
        s.play_measures(
            *s.notation(s.bells, "♩ ♩C ♩D^  | ♩D ♩E ♩G ♩A | ♩a ♩b ♩c ♩d | ♩e"),
            *s.notation(s.clicks, "3♪C 3♪D | ♩ ♩- ♩> ♩^ | ♩ ♩- ♩> ♩^   |"),
        )
        s.play_parts(
            *s.bell_part("♩ ♩C ♩D^  | ♩D ♩E ♩G ♩A | ♩a ♩b ♩c ♩d | ♩e"),
            *s.click_part("3♪C 3♪D | ♩ ♩- ♩> ♩^ | ♩ ♩- ♩> ♩^   |"),
        )
