"""Marquee Lighted Sign Project - demo"""

from dataclasses import dataclass
import sys
import time

from lightset_misc import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON
from modes.musicmode import MusicMode
from music import (
    dimmer, dimmer_sequence, light, measure, part, play,
    section, Section, sequence, set_mode
)
from music import(
    act, act_part, drum_part,
    rest, sequence_measure, sequence_part
)
from .sequences import *
from specialparams import ActionParams, ChannelParams


@dataclass
class Demo(MusicMode):
    """Version 3 demo."""

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()

        self.lights.set_channels(brightness=100, on=True, force=True)
        time.sleep(0.5)
        self.lights.set_relays(ALL_ON)

    def execute(self) -> None:
        """Execute version 3 demo."""
        sections = [
            self.pre(),
            self.alternate(),
            self.rotate(),
            self.triplett_a(),
            self.triplett_b(),
            self.rotate_fast(),
            self.dim(),
        ]
        for section in sections:
            section.play()
        sys.exit()

    def pre(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            sequence_part(
                '  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  '
                '  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  '
                '  𝅝 | 𝄻  ',
                sequence(
                    rotate, 4,
                    special=ChannelParams(
                        concurrent=False,
                        brightness_on = 100,
                        brightness_off = 40,
                    ),
                ),
                sequence(
                    blink_all,
                    special=ChannelParams(
                        trans_off=2,
                        trans_on=2,
                    ),
                    on_first=True,
                ),
            ),
            tempo=90,
        )

    def alternate(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            sequence_part(
                '  ♩ ♩ ♩ ♩ | ♩ ♩ ♩ ♩ | ♩  ',
                sequence(center_alternate), 
                sequence(blink_alternate),
            ),
            drum_part(
                '  𝄻  |  𝄻  |  𝄼 𝄽 𝄾 𝄿 𝅘𝅥𝅰- 𝅘𝅥𝅰-  '
            ),
            tempo=75,
        )

    def rotate(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            sequence_part(
                '  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  '
                '  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  '
                '  𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 |  '
                '  𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 |  ',
                sequence(rotate, pattern="100000100000", clockwise=True),
                sequence(rotate, pattern="100000100000", clockwise=False),
                # sequence(build_rows, pattern='1', from_top=True),
                # sequence(build_rows, pattern='1', from_top=False),
            ),
            drum_part(
                '  𝄻  |  𝄻  |  ♪^ 𝄾 𝄼 𝄾 𝄿 𝅘𝅥𝅰^  |  𝅘𝅥𝅰^  '
            ),
            tempo=75,
        )

    def triplett_a(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drum_part(
                " 𝄽 𝄾 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | "
                       "♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ",
                accent='-',
            ),
            act_part(
                "  𝄽 𝄽 | ♩ 𝄽 | ♩ 𝄽  ",
                light(ALL_OFF),
                light(ALL_ON, ChannelParams()),
            ),
            beats=2,
            tempo=80,
        )

    def triplett_b(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drum_part(
                " ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | "
                " ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ ",
                accent='-',
            ),
            sequence_part(
                "  𝄾 ♪ ♪ 𝄾 | 𝄾 ♪ ♪ 𝄾 | ♪ 𝄾 ♪ 𝄾 | 𝄾 ♪ ♪  ",
                sequence(blink_all, on_first=False),
            ),
            beats=2,
            tempo=80,
        )

    def rotate_fast(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        # light(ALL_ON, ChannelParams(trans_on=6))()
        rotations = 11
        pattern = [
            p
            for p in rotate_build_flip(count = rotations * 10)
        ] + ["111111111111"]
        return section(
            part(
                sequence_measure(
                    '♩', rotations * 10 + 1, lambda: iter(pattern), 
                ),
            ),
            drum_part(
                ' ♩^ ♩ ♩ ♩ ♩ ♩^ ♩ ♩ ♩ ♩ ' * rotations + ' ♩^ '
            ),
            beats=rotations * 10 + 1,
            tempo=675,
        )

    def dim(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            part(
                measure(
                    act('♩', light(ALL_ON), light(ALL_ON, ChannelParams()))
                )
            ),
            sequence_part(
                '  𝄻  | ♩ ♩ ♩ ♩ ',
                # sequence(build_rows, special=ChannelParams(trans_off=2), pattern='0'),
            ),
            tempo=60,
        )

    def future_intro(self) -> None:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        play(
            measure(
                act('♩', light(ALL_OFF)),
                act('♩', dimmer(ALL_HIGH)),
                rest('𝅗𝅥'),
            ),
            measure(
                act('♩', light("0100000000")),
            ),
            measure(
                act('♩', light("0000000000")),
            ),
            measure(
                act('♩', light("1110001000")),
                rest('♩𝅘𝅥𝅯'),
                act('♩', light("0000000000")),
                act('♩', dimmer(ALL_LOW)),
            ),
            measure(
                rest('♩'),
                act('♩', light(ALL_ON)),
            ),
            sequence_measure(
                '♩', LIGHT_COUNT, random_once_each, 
                ActionParams(action=dimmer_sequence(100, 2)),
                beats=16,
            ),
            tempo = 90,
        )

