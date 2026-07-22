"""Marquee Lighted Sign Project - rhythm"""

from dataclasses import dataclass
import time
from typing_extensions import override

from device_defs import ALL_HIGH, ALL_LOW, ALL_ON
from . import MusicMode
from music import (
    lights, measure, part,
    relay, rest, section, Section, sequence, piece,
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
        self.lights = self.combined
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
            self.play_drums(),
            self.play_ringer(),
            self.play_drums(),
            self.play_buzzer(),
            self.play_drums(),
            self.play_ringer(),
        ).play(tempo=140)

    def init(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drums(
                '  |  𝅝>  |  𝄻  |  𝄻  |  𝄻  |  ',
            ),
        )

    def play_drums(self) -> Section:
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
            lights(
                ' |  ♩  | ' * 8,
                *[
                    dict(
                        on=True,
                        brightness=100,
                        color=self.lights.colors.random(),
                    )
                    for i in range(8)
                ],
            ),
        )

    def play_ringer(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝅘𝅥𝅱 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            part(
                measure(
                    action('𝅘𝅥𝅲', self.ringer.play),
                    action('𝅘𝅥𝅲', self.ringer.rest),
                )
            )
        )

    def play_buzzer(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            part(
                measure(
                    # 1
                    rest('𝄾'),
                    # and
                    action('𝅘𝅥𝅯', self.buzzer.play),
                    action('𝅘𝅥𝅯', self.buzzer.rest),
                    # 2
                    action('♪', self.buzzer.play),
                    action('♪', self.buzzer.rest),
                    # 3
                    action('♪', self.buzzer.play),
                    action('♪', self.buzzer.rest),
                    action('𝅘𝅥𝅯', self.buzzer.play),
                    action('𝅘𝅥𝅯', self.buzzer.rest),
                    action('𝅘𝅥𝅯', self.buzzer.play),
                    action('𝅘𝅥𝅯', self.buzzer.rest),
                    # action('♪', self.buzzer.play),
                    # action('♪', self.buzzer.rest),
                )
            )
        )

