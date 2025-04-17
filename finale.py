"""Marquee Lighted Sign Project - finale"""

import sys
import time

from definitions import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON, ActionParams
from modes import PlayMusicMode
from sequence_defs import *

class Finale(PlayMusicMode):
    """"""

    def execute(self):
        self.original_2()
        sys.exit()
        self.tempo = 90
        # self.intro()
        # self.body1()
        # self.body4()
        # self.body5()

    def original_2(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s = self
        s.tempo = 75
        print(time.time())
        s.play_measures(s.measure())
        print(time.time())
        # A
        print(time.time())
        part_a = self.prepare_parts(
            s.seq_part(
                (s.seq(center_alternate), 
                    ' ♩ ♩ ♩ ♩ '),
                (s.seq(blink_alternate), 
                    ' ♩ ♩ ♩ ♩ '),
                (s.seq(blink_alternate),
                    ' ♩ '    ),
            ),
            s.drum_part(
                ' 𝄻 | 𝄻 | 𝄼 𝄽 𝄾 𝄿 𝅘𝅥𝅰- 𝅘𝅥𝅰- '
            ),
        )
        print(time.time())
        # B
        print(time.time())
        part_b = self.prepare_parts(
            s.seq_part(
                (s.seq(rotate, pattern="0100001000", clockwise=True),
                    ' ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ '),
                (s.seq(rotate, pattern="0100001000", clockwise=False),
                    ' ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ '),
                (s.seq(build_rows, pattern='1', from_top=True),
                    ' 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 '),
                (s.seq(build_rows, pattern='1', from_top=False),
                    ' 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 '),
            ),
            s.drum_part(
                ' 𝄻 | 𝄼 𝄽 𝄾 ♪^ | ♪^ 𝄾 𝄼 𝄾 𝄿 𝅘𝅥𝅰^ | 𝅘𝅥𝅰^ '
            ),
        )
        print(time.time())
        # C
        # 1231 & 2 1231 & 2 1231 (&) 1232 1231 & 2
        notes = "𝄽 𝄾 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 |" \
                           "♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ "  # | 𝄻 | 𝄻 "
        part_c = self.prepare_parts(
            s.drum_part(notes, beats=2),
            s.part(
                s.measure(
                    s.act('♩', s.light(ALL_OFF)),
                    s.act('♩', s.dimmer(ALL_LOW)),
                    beats=2,
                ),
            ),
        )
        # D
        part_d = self.prepare_parts(
            s.drum_part(notes, beats=2),
            s.seq_part((s.seq(triplet_rhythm), notes), beats=2),
        )
        
        print(time.time())
        s.play_measures(*part_a)
        print(time.time())

        print(time.time())
        s.play_measures(*part_b)
        print(time.time())

        print(time.time())
        s.play_measures(*part_c)
        print(time.time())

        print(time.time())
        s.play_measures(*part_d)
        print(time.time())

    def intro(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s = self
        s.tempo = 90
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
                '♩', LIGHT_COUNT, random_once_each, 
                ActionParams(action=s.dimmer_seq(100, 2)),
                beats=16,
            ),
            #s.measure(beats=32),
        )
    

    def body3(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s = self
        rows = s.seq(each_row)
        s.play_measures(
            *s.notation(s.bell, "♩    ♩C ♩D^ | ♩D ♩E ♩G ♩A | ♩a ♩b ♩c ♩d | 𝄽 𝄽 ♩e 𝄽"),
            *s.notation(s.drum, "3♪C 3♪D    | ♩  ♩- ♩> ♩^ | ♩  ♩- ♩> ♩^   |"),
            *s.notation(rows, "3♪C   3♪D    | ♩  ♩- ♩> ♩^ | ♩  ♩- ♩> ♩^   |"),
        )
        s.play_parts(
            s.bell_part("♩ ♩C ♩D^  | ♩D ♩E ♩G ♩A | ♩a ♩b ♩c ♩d | ♩e"),
            s.drum_part("3♪C 3♪D | ♩ ♩- ♩> ♩^ | ♩ ♩- ♩> ♩^   |"),
            s.seq_part(
                (rows,  "3♪C 3♪D | ♩ ♩- ♩> ♩^ | ♩ ♩- ♩> ♩^   |")),
        )

    def body4(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀

        s = self
        #rows = s.seq(build_rows, pattern="0", from_top=True)
        rows = s.seq(triplet_rhythm)
        # 1231 & 2 1231 & 2 1231 (&) 1232 1231 & 2
        notes = "𝄽 𝄾 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 |" \
                           "♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ "  # | 𝄻 | 𝄻 "
        s.play_parts(
            s.drum_part(notes, beats=2),  # , play_measures beats=2 !!!!!
            s.part(
                s.measure(
                    s.act('♩', s.light(ALL_OFF)),
                    s.act('♩', s.dimmer(ALL_LOW)),
                    beats=2,
                ),
            ),
        )
        s.play_parts(
            s.drum_part(notes, beats=2),  # , play_measures beats=2 !!!!!
            s.seq_part((rows, notes), beats=2),
        )

    def body5(self):
        s = self
        s.tempo = 600
        s.light(ALL_ON, DimmerParams(transition_on=6))()
        s.play_measures(
            s.seq_measure(
                '♪', 80, rotate, 
                pattern="0111111111", clockwise=True,
            ),
        )
