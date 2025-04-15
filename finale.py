"""Marquee Lighted Sign Project - finale"""

import sys

from definitions import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON, ActionParams
from modes import PlayMusicMode
from music import Sequence
from sequence_defs import *

class Finale(PlayMusicMode):
    """"""

    def execute(self):
        self.body4()
        sys.exit()
        self.test()
        self.intro()
        self.body1()
        self.body2()

    def intro(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s = self
        s.play_measures(
            s.measure(
                s.act('♩', s.light(ALL_OFF)),
                s.act('♩', s.dimmer(ALL_HIGH)),
                s.rest('𝅗𝅥'),
            ),
            s.measure(
                s.act('♩', s.light("0100000000")),
            ),
            s.measure(
                s.act('♩', s.light("0000000000")),
            ),
            s.measure(
                s.act('♩', s.light("1110001000")),
                s.rest('♩𝅘𝅥𝅯'),
                s.act('♩', s.light("0000000000")),
                s.act('♩', s.dimmer(ALL_LOW)),
            ),
            s.measure(
                s.rest('♩'),
                s.act('♩', s.light(ALL_ON)),
            ),
            s.seq_measure(
                '♩', LIGHT_COUNT, seq_random_once_each, 
                ActionParams(action=s.dimmer_seq(100, 2)),
                beats=16,
            ),
            #s.measure(beats=32),
        )
    
    def body1(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s = self
        s.play_parts(
            s.part(
                s.measure(
                    s.rest('𝅗𝅥♩♪𝅘𝅥𝅰'),
                    #s.act('𝅘𝅥𝅰', s.relay(0, 1)),
                    #s.act('𝅘𝅥𝅰', s.relay(2, 3)),
                    #s.act('𝅘𝅥𝅰', s.relay(4, 5)),
                ),
                s.seq_measure(
                    '♪', 8, seq_rotate, 
                    pattern="0100001000", clockwise=True,
                ),
                s.seq_measure(
                    '♪', 8, seq_rotate, 
                    pattern="0100001000", clockwise=False,
                ),
            )
        )

    def body2(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s = self
        s.play_parts(
            s.part(
                s.seq_measure('♪', 8, seq_rows),
                s.seq_measure('♪', 8, seq_rows),
                s.seq_measure('♪', 8, seq_rows),
            ),
            s.part(
                s.measure(
                    s.drum('𝄽♪'),
                    s.rest('♪♪'),
                    s.drum('♪^'),
                ),
                s.measure(
                    s.drum('♪^'),
                ),
                s.measure(
                    s.drum('♪'),
                ),
            ),
        )

    def body3(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s = self
        rows = s.seq(seq_rows)
        s.play_measures(
            *s.notation(s.bell, "♩    ♩C ♩D^ | ♩D ♩E ♩G ♩A | ♩a ♩b ♩c ♩d | 𝄽 𝄽 ♩e 𝄽"),
            *s.notation(s.drum, "3♪C 3♪D    | ♩  ♩- ♩> ♩^ | ♩  ♩- ♩> ♩^   |"),
            *s.notation(rows, "3♪C   3♪D    | ♩  ♩- ♩> ♩^ | ♩  ♩- ♩> ♩^   |"),
        )
        s.play_parts(
            s.bell_part("♩ ♩C ♩D^  | ♩D ♩E ♩G ♩A | ♩a ♩b ♩c ♩d | ♩e"),
            s.drum_part("3♪C 3♪D | ♩ ♩- ♩> ♩^ | ♩ ♩- ♩> ♩^   |"),
            s.seq_part(
                rows,   "3♪C 3♪D | ♩ ♩- ♩> ♩^ | ♩ ♩- ♩> ♩^   |"),
        )

    def body4(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀

        s = self
        s.tempo = 90
        #rows = s.seq(seq_build_rows, pattern="0", from_top=True)
        rows = s.seq(seq_triplet_rhythm)
        # 1231 & 2 1231 & 2 1231 (&) 1232 1231 & 2
        notes = "𝄽 𝄾 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 |" \
                           "♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ | 𝄻 | 𝄻 "
        s.play_parts(
            s.drum_part(notes, beats=2),  # , play_measures beats=2 !!!!!
            s.seq_part(rows, notes, beats=2),
        )
