"""Marquee Lighted Sign Project - rhythm"""

from dataclasses import dataclass
import time
from typing_extensions import override

from device_defs import ALL_HIGH, ALL_ON, ALL_LOW, ALL_ON
from . import MusicMode
from music import (
    dimmer, dimmer_sequence, measure, part, play,
    relay, section, Section, sequence, piece,
)
from music import(
    action, actions, drums,
    rest, sequence_measure, sequences
)
from .structural.sequences import *
from devices.specialparams import ActionParams, ChannelParams


@dataclass
class Rhythm(MusicMode):
    """PyOhio 2026"""

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()

        self.lights.set_channels(brightness=100, on=True, force=True)
        time.sleep(0.5)
        self.lights.set_relays(ALL_ON)
        self.drums.accent_to_relay_count = {
            0: 4, 1: 8, 2: 24, 3: 32,
        }

    @override
    def execute(self) -> None:
        """"""
        piece(
            self.init(),
            self.one(),
            self.one(),
            self.one(),
            self.one(),
            self.one(),
            self.one(),
        ).play(tempo=140)

    def init(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drums(
                '  |  𝅝>  |  𝄻  |  𝄻  |  𝄻  |  ',
            ),
        )

    def one(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drums(
                '  |  ♩ ♩ ♩ ♩  |  ♩> ♩ ♩ ♩  |  𝄾 ♪ ♪ ♪ ♪> ♪ ♪ ♪  |  ♩> ♩ ♩ ♩  |  '
                '  |  3♪> 3♪ 3♪  3♪> 3♪ 3♪  3♪> 3♪ 3♪  3♪> 3♪ 3♪  |  ♩> ♩ ♩ ♩  |  '
                '  |  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 '
                '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  |  ♩> ♩ ♩ ♩  |  ',
                accent='-',
            ),
        )
    #             sequence(
    #                 rotate, 4,
    #                 special=ChannelParams(
    #                     concurrent=False,
    #                     brightness_on = 100,
    #                     brightness_off = 40,
    #                 ),
    #             ),
    #             sequence(
    #                 blink_all,
    #                 special=ChannelParams(
    #                     trans_off=2,
    #                     trans_on=2,
    #                 ),
    #                 on_first=True,
    #             ),
    #         ),
    #         tempo=90,
    #     )

    # def future_intro(self) -> None:
    #     # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
    #     play(
    #         measure(
    #             action('♩', relay(ALL_OFF)),
    #             action('♩', dimmer(ALL_HIGH)),
    #             rest('𝅗𝅥'),
    #         ),
    #         measure(
    #             action('♩', relay("0100000000")),
    #         ),
    #         measure(
    #             action('♩', relay("0000000000")),
    #         ),
    #         measure(
    #             action('♩', relay("1110001000")),
    #             rest('♩𝅘𝅥𝅯'),
    #             action('♩', relay("0000000000")),
    #             action('♩', dimmer(ALL_LOW)),
    #         ),
    #         measure(
    #             rest('♩'),
    #             action('♩', relay(ALL_ON)),
    #         ),
    #         sequence_measure(
    #             '♩', LIGHT_COUNT, random_once_each, 
    #             ActionParams(action=dimmer_sequence(100, 2)),
    #             beats=16,
    #         ),
    #         tempo = 90,
    #     )

