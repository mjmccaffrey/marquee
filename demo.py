"""Marquee Lighted Sign Project - finale"""

import sys

from definitions import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON, ActionParams
from modes import PlayMusicMode
from sequence_defs import *

class Demo(PlayMusicMode):
    """"""

    def execute(s):  # type: ignore

        s.play(s.measure(), s.measure())

        # A # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        section_intro = s.section(
            s.seq_part(
                (s.seq(center_alternate), 
                    ' ♩ ♩ ♩ ♩ '),
                (s.seq(blink_alternate), 
                    ' ♩ ♩ ♩ ♩ '),
                (s.seq(blink_alternate),
                    ' ♩ '    ),
            ),
            s.drum_part(
                    '  𝄻  |  𝄻  |  𝄼 𝄽 𝄾 𝄿 𝅘𝅥𝅰- 𝅘𝅥𝅰-  '
            ),
            tempo=75,
        )
        # B # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        section_b = s.section(
            s.seq_part(
                (s.seq(rotate, pattern="0100001000", clockwise=True),
                    ' ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ '),
                (s.seq(rotate, pattern="0000100001", clockwise=False),
                    ' ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ '),
                (s.seq(build_rows, pattern='1', from_top=True),
                    ' 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 '),
                (s.seq(build_rows, pattern='1', from_top=False),
                    ' 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 '),
            ),
            s.drum_part(
                '  𝄻  |  𝄻  |  ♪^ 𝄾 𝄼 𝄾 𝄿 𝅘𝅥𝅰^  |  𝅘𝅥𝅰^  '
            ),
            tempo=75,
        )
        # C # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        section_3_1= s.section(
            s.drum_part(
                " 𝄽 𝄾 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | "
                       "♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 "
            ),
            s.seq_part(
                (s.seq(random_flip, DimmerParams(concurrent=False), light_pattern='0000000000'), 
                 ' ♪ ♪ ♪ ♪ |  ♪ ♪ ♪ ♪ | ♪ ♪ ♪ ♪ | ♪ ♪ ♪ ♪ | ♪ ♪ ♪ ♪'),
            ),
            beats=2,
            tempo=75,
        )
        print(section_3_1._measures)
        # D # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        d = (   " ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | "
                " ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ "
        )
        section_3_2 = s.section(
            s.drum_part(d, accent='>'),
            s.seq_part((s.seq(triplet_rhythm), d)),
            beats=2,
            tempo=75,
        )
        # E # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s.light(ALL_ON, DimmerParams(transition_on=6))()
        rotations = 10
        pattern = [
            p for _ in range(rotations)
                for p in rotate(
                    pattern="0111111111", clockwise=True)
        ] +                ["1111111111"]
        section_finale = s.section(
            s.part(
                s.seq_measure(
                    '♪', rotations * 10 + 1, lambda: iter(pattern), 
                ),
            ),
            s.drum_part(
                ' ♪^ 𝄾 𝄾 𝄾 𝄾 ♪^ 𝄾 𝄾 𝄾 𝄾 ' * rotations + ' ♪^ '
            ),
            beats=60,
            tempo=675,
        )
        # F # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        section_dim = s.section(
            s.part(
                s.measure(
                    s.act('♩', s.light(ALL_ON), s.light(ALL_ON, DimmerParams()))
                )
            ),
            s.seq_part(
                (s.seq(build_rows, DimmerParams(transition_off=3), pattern='0'), 
                    '  𝄻  | ♩ ♩ ♩ ♩ '),
            ),
            tempo=60,
        )
        # F # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        section_step = s.section(
            s.drum_part(
                ' 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯   𝅘𝅥𝅯> 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯   𝅘𝅥𝅯 𝅘𝅥𝅯> 𝅘𝅥𝅯 𝅘𝅥𝅯   𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 | ' * 4
            ),
            tempo=110,
        )

        #section_intro.play()
        #section_b.play()
        #section_3_1.play()
        #section_3_2.play()
        # section_finale.play()
        section_step.play()
        section_dim.play()
        sys.exit()

    def future_intro(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s = self
        s.play(
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
            tempo = 90,
        )
