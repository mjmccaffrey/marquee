"""Marquee Lighted Sign Project - demo"""

from dataclasses import dataclass
import sys
import time
from typing_extensions import override

from device_defs import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON
from . import MusicMode
from music import (
    dimmer, dimmer_sequence, measure, part, play,
    relay, section, Section, sequence,
)
from music import(
    action, actions, drums,
    rest, sequence_measure, sequences
)
from .sequences import *
from devices.specialparams import ActionParams, ChannelParams


@dataclass
class Demo(MusicMode):
    """Version 3 demo."""

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()

        self.lights.set_channels(brightness=100, on=True, force=True)
        time.sleep(0.5)
        self.lights.set_relays(ALL_ON)

    @override
    def execute(self) -> None:
        """Execute version 3 demo."""
        sections = [
            self.pre(),
            self.alternate(),
            self.rotate(),
            self.triplett_a(),
            self.triplett_b(),
            self.rotate_fast(),
            # self.dim(),
        ]
        for section in sections:
            print(section.play())
        # sys.exit()

    def pre(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            sequences(
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
            sequences(
                '  ♩ ♩ ♩ ♩ | ♩ ♩ ♩ ♩ | ♩  ',
                sequence(center_alternate), 
                sequence(blink_alternate),
            ),
            drums(
                '  𝄻  |  𝄻  |  𝄼 𝄽 𝄾 𝄿 l𝅘𝅥𝅰 l𝅘𝅥𝅰  '
            ),
            tempo=75,
        )

    def rotate(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            sequences(
                '  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  '
                '  ♪ ♪ ♪ ♪ ♪ ♪ ♪ ♪ |  '
                '  𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 |  '
                '  𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 𝅘𝅥𝅯 |  ',
                sequence(rotate, pattern="100000100000", clockwise=True),
                sequence(rotate, pattern="100000100000", clockwise=False),
                # sequence(build_rows, pattern='1', from_top=True),
                # sequence(build_rows, pattern='1', from_top=False),
            ),
            drums(
                '  𝄻  |  𝄻  |  ♪^ 𝄾 𝄼 𝄾 𝄿 h𝅘𝅥𝅰  |  h𝅘𝅥𝅰  '
            ),
            tempo=75,
        )

    def triplett_a(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drums(
                " 𝄽 𝄾 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | "
                       "♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ",
                accent='-',
            ),
            actions(
                "  𝄽 𝄽 | ♩ 𝄽 | ♩ 𝄽  ",
                relay(ALL_OFF),
                relay(ALL_ON, ChannelParams()),
            ),
            beats=2,
            tempo=80,
        )

    def triplett_b(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drums(
                " ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪> ♪ ♪ 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | "
                " ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 ♪> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 | ♪ ♪^ ♪^ ",
                accent='-',
            ),
            sequences(
                "  𝄾 ♪ ♪ 𝄾 | 𝄾 ♪ ♪ 𝄾 | ♪ 𝄾 ♪ 𝄾 | 𝄾 ♪ ♪  ",
                sequence(blink_all, on_first=False),
            ),
            beats=2,
            tempo=80,
        )

    def rotate_fast(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        # relay(ALL_ON, ChannelParams(trans_on=6))()
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
            drums(
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
                    action('♩', relay(ALL_ON, ChannelParams()))
                )
            ),
            sequences(
                '  𝄻  | ♩ ♩ ♩ ♩ ',
                # sequence(build_rows, special=ChannelParams(trans_off=2), pattern='0'),
            ),
            tempo=60,
        )

    def future_intro(self) -> None:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        play(
            measure(
                action('♩', relay(ALL_OFF)),
                action('♩', dimmer(ALL_HIGH)),
                rest('𝅗𝅥'),
            ),
            measure(
                action('♩', relay("0100000000")),
            ),
            measure(
                action('♩', relay("0000000000")),
            ),
            measure(
                action('♩', relay("1110001000")),
                rest('♩𝅘𝅥𝅯'),
                action('♩', relay("0000000000")),
                action('♩', dimmer(ALL_LOW)),
            ),
            measure(
                rest('♩'),
                action('♩', relay(ALL_ON)),
            ),
            sequence_measure(
                '♩', LIGHT_COUNT, random_once_each, 
                ActionParams(action=dimmer_sequence(100, 2)),
                beats=16,
            ),
            tempo = 90,
        )

