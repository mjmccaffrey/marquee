"""Marquee Lighted Sign Project - rhythm"""

from dataclasses import dataclass
import time
from typing_extensions import override

from device_defs import ALL_HIGH, ALL_LOW, ALL_ON
from . import MusicMode
from music import (
    dimmer, dimmer_sequence, measure, part, play,
    relay, section, Section, sequence, piece,
)
from music import(
    action, actions, drums,
    rest, ringer, sequence_measure, sequences
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
            self.two(),
            self.one(),
            self.two(),
            self.one(),
            self.two(),
        ).play(tempo=140)

    def init(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drums(
                '  |  𝅝>  |  𝄻  |  𝄻  |  𝄻  |  ',
            ),
        )

    def one(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝅘𝅥𝅱 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀 𝅁
        return section(
            drums(
                '  |  ♩ ♩ ♩ ♩  |  ♩> ♩ ♩ ♩  |  𝄾 ♪ ♪ ♪ ♪> ♪ ♪ ♪  |  ♩> ♩ ♩ ♩  |  '
                '  |  3♪> 3♪ 3♪  3♪> 3♪ 3♪  3♪> 3♪ 3♪  3♪> 3♪ 3♪  |  ♩> ♩ ♩ ♩  |  '
                '  |  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 '
                '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  |  ♩> ♩ ♩ ♩  |  '
                # '  |  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 '
                # '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  '
                # '     3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 '
                # '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  |  ♩> ♩ ♩ ♩  |  '
                ,
                accent='-',
            ),
        )

    def two(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            ringer('  𝅘𝅥𝅱  ')
            # part(
            #     measure(
            #         action('𝅘𝅥𝅱', self.ringer.play),
            #         action('𝅘𝅥𝅱', self.ringer.rest),
            #     )
            # )
        )

