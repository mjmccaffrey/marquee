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
            self.section_a(bell=True),
            self.section_a(bell=False),
            self.buzzer_measure(),
            self.section_b(),
            self.ringer_measure(),
        ).play(tempo=140)

    def init(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            drums(
                '  |  𝅝>  |  𝄻  |  𝄻  |  𝄻  |  ',
            ),
        )

    def section_a(self, bell: bool) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝅘𝅥𝅱 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀 𝅁
        return section(
            drums(
                '  |  ♩ ♩ ♩ ♩  |  ♩> ♩ ♩ ♩  |  𝄾 ♪ ♪ ♪ ♪> ♪ ♪ ♪  |  ♩> ♩ ♩ ♩  |  '
                '  |  3♪> 3♪ 3♪  3♪> 3♪ 3♪  3♪> 3♪ 3♪  3♪> 3♪ 3♪  |  ♩> ♩ ♩ ♩  |  '
                '  |  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 '
                '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  |  ♩> ♩ ♩ ♩  |  ',
                accent='-',
            ),
            lights(
                ' |  ♩  | ' * 8,
                *[self.random_color() for _ in range(8)]
            ),
            part(
                measure(
                    action('𝅘𝅥𝅲', self.ringer.play if bell else lambda: None),
                    action('𝅘𝅥𝅲', self.ringer.rest if bell else lambda: None),
                ),
            ),
        )

    def buzzer_measure(self) -> Section:
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
                    # and
                    action('𝅘𝅥𝅯', self.buzzer.play),
                    action('𝅘𝅥𝅯', self.buzzer.rest),
                    # a
                    action('𝅘𝅥𝅯', self.buzzer.play),
                    action('𝅘𝅥𝅯', self.buzzer.rest),
                )
            )
        )

    def ringer_measure(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            part(
                measure(
                    action('♩', self.ringer.play),
                    action('♩', self.ringer.rest),
                ),
            )
        )

    def section_b(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝅘𝅥𝅱 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀 𝅁
        return section(
            drums(
                # '  |  ♩ ♩ ♩ ♩  |  ♩> ♩ ♩ ♩  |  𝄾 ♪ ♪ ♪ ♪> ♪ ♪ ♪  |  ♩> ♩ ♩ ♩  |  '
                # '  |  3♪> 3♪ 3♪  3♪> 3♪ 3♪  3♪> 3♪ 3♪  3♪> 3♪ 3♪  |  ♩> ♩ ♩ ♩  |  '
                # '  |  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 '
                # '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  |  ♩> ♩ ♩ ♩  |  '
                # '  |  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 '
                # '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  '
                '     3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 '
                '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  | '
                '  |  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 '
                '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  '
                '     3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 '
                '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  | '
                '  |  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 '
                '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  '
                '     3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 '
                '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  | '
                '  |  ♩> ♩ ♩ ♩  |  '
                ,
                accent='-',
            ),
            lights(
                ' |  ♩  | ' * 4,
                *[self.random_color() for _ in range(4)]
            ),
        )

    def random_color(self):
        return dict(
            on=True,
            brightness=100,
            color=self.lights.colors.random(),
        )
    
