"""Marquee Lighted Sign Project - finale"""

import sys

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
        s.play(s.measure())
        # A # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        section_a = self.section(
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
        # B # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        section_b = self.section(
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
                ' 𝄻 | 𝄻 | ♪^ 𝄾 𝄼 𝄾 𝄿 𝅘𝅥𝅰^ | 𝅘𝅥𝅰^ '
            ),
        )
        # C # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        # 1231 & 2 1231 & 2 1231 (&) 1232 1231 & 2
        notes_1 = "     𝄽 𝄾 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | " \
                           "♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 "
        notes_2 = " ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | " \
                           "♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ "
        section_c = self.section(
            s.drum_part(notes_1, beats=2),
        )
        # D # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        section_d = self.section(
            s.drum_part(notes_2, accent='>'),
            s.seq_part((s.seq(triplet_rhythm), notes_2)),
            beats=2,
        )
        section_a.play()
        section_b.play()
        section_c.play()
        section_d.play()

        s.play(s.measure(s.act('♩', s.light(ALL_OFF, DimmerParams()))))

        # E # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s.light(ALL_ON, DimmerParams(transition_on=6))()
        rotations = 10
        pattern = [
            p for _ in range(rotations)
                for p in rotate(
                    pattern="0111111111", clockwise=True)
        ] +                ["1111111111"]
        section_e = s.section(
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
        section_e.play()

        # F # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        section_f = s.section(
            s.seq_part(
                (s.seq(build_rows, DimmerParams(transition_off=4), pattern='0'), 
                    ' 𝄻 | 𝄻 | ♩ ♩ ♩ ♩ '),
            ),
            tempo=45,
        )
        section_f.play()

    def intro(self):
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s = self
        s.tempo = 90
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
        )
    