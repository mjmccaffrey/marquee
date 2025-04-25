"""Marquee Lighted Sign Project - demo"""

import sys

from definitions import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON, ActionParams
from modes import PlayMusicMode
from sequence_defs import *

class Demo(PlayMusicMode):
    """"""

    def execute(self):
        """"""
        sections = [
            self.pre(),
            self.alternate(),
            self.rotate(),
            self.triplett_a(),
            self.triplett_b(),
            self.rotate_fast(),
            self.dim(),
        ]
        # s.play(s.measure(), s.measure())
        for section in sections:
            section.play()
        sys.exit()

    def pre(s):  # type: ignore
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return s.section(
            s.seq_part(
                (   
                    s.seq(
                        rotate,
                        special=DimmerParams(
                            concurrent=False,
                            brightness_on = 100,
                            brightness_off = 40,
                        )
                    ),
                    '  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |    '
                    '  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪  '
                )
            ),
            s.seq_part(
                (   
                    s.seq(
                        blink_all,
                        special=DimmerParams(
                            transition_off=2,
                            transition_on=2,
                        ),
                        on_first=True,
                    ),
                    '  𝄻 |  𝄻 |  𝄻 |  𝄻 | 𝅝 | 𝅝  ',
                )
            ),
            tempo=90,
        )

    def alternate(s):  # type: ignore
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return s.section(
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
    
    def rotate(s):  # type: ignore
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return s.section(
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
    
    def triplett_a(s):  # type: ignore
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return s.section(
            s.drum_part(
                " 𝄽 𝄾 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | "
                       "♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ",
                accent='-',
            ),
            s.act_part(
                "  𝄽 𝄽 | ♩ 𝄽 | ♩ 𝄽  ",
                s.light(ALL_OFF),
                s.light(ALL_ON, DimmerParams()),
            ),
            # s.seq_part(
            #     (s.seq(random_flip, DimmerParams(concurrent=False), light_pattern='0000000000'), 
            #      ' ♪ ♪ ♪ ♪ |  ♪ ♪ ♪ ♪ | ♪ ♪ ♪ ♪ | ♪ ♪ ♪ ♪ | ♪ ♪ ♪ ♪'),
            # ),
            beats=2,
            tempo=80,
        )

    def triplett_b(s):  # type: ignore
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return s.section(
            s.drum_part(
                " ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | "
                " ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ "
            ),
            s.seq_part(
                (
                    s.seq(blink_all, on_first=False),
                    # s.seq(lambda: cycle(chain(all_on(), all_off()))), 
                    " 𝄾 ♪ ♪ 𝄾 | 𝄾 ♪ ♪ 𝄾 | "
                    " ♪ 𝄾 ♪ 𝄾 | 𝄾 ♪ ♪ "
                ),
            ),
            beats=2,
            tempo=80,
        )
    
    def rotate_fast(s):  # type: ignore
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        s.light(ALL_ON, DimmerParams(transition_on=6))()
        rotations = 10
        pattern = [
            p for _ in range(rotations)
                for p in rotate(
                    pattern="0111111111", clockwise=True)
        ] +                ["1111111111"]
        return s.section(
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

    def dim(s):  # type: ignore
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return s.section(
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
