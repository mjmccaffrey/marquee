"""Marquee Lighted Sign Project - rhythm"""

from dataclasses import dataclass
import time
from typing_extensions import override

from device_defs import ALL_ON
from . import MusicMode
from music import section, Section, piece
from music import buzzer, drums, lights, ringer
# from .structural.sequences import *

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
        music = piece(
            self.init(),
            self.section_a(bell=True),
            self.section_a(bell=False),
            self.buzzer_measure(),
            self.section_b(),
            self.ringer_measure(),
        )
        self.play(music, tempo=140)
        self.lights.set_channels(brightness=0, transition=8.0)

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
                ' |  ♩ ♩ ♩ ♩  |  ♩> ♩ ♩ ♩  |  𝄾 ♪ ♪ ♪ ♪> ♪ ♪ ♪  |  ♩> ♩ ♩ ♩  | '
                ' |  3♪> 3♪ 3♪  3♪> 3♪ 3♪  3♪> 3♪ 3♪  3♪> 3♪ 3♪  |  ♩> ♩ ♩ ♩  | '
                ' |  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 '
                '    3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  |  ♩> ♩ ♩ ♩  | ',
                accent='-',
            ),
            lights(
                ' |  ♩  | ' * 8,
                *[self.random_color() for _ in range(8)]
            ),
            ringer(
                ' |  𝄻 | ' * 7 + 
                ' |  𝄽 𝄽 𝄽 ' + ('𝅘𝅥𝅲' if bell else '𝅁')
            ),
            # actions(
            #     ' |  𝄻 |  ' * 7 + 
            #     ' |  𝄽 𝄽 𝄽 𝅘𝅥𝅲 𝅘𝅥𝅲 | ',
            #     self.ringer.play if bell else lambda: None,
            #     self.ringer.rest if bell else lambda: None,
            # ),
        )

    def buzzer_measure(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            buzzer(' |  𝄾 𝅘𝅥𝅯 𝄿   ♪ 𝄾   ♪ 𝄾   𝅘𝅥𝅯 𝄿 𝅘𝅥𝅯 𝄿  | '),
            # part(
            #     measure(
            #         # 1
            #         rest('𝄾'),
            #         # and
            #         action('𝅘𝅥𝅯', self.buzzer.play),
            #         action('𝅘𝅥𝅯', self.buzzer.rest),
            #         # 2
            #         action('♪', self.buzzer.play),
            #         action('♪', self.buzzer.rest),
            #         # 3
            #         action('♪', self.buzzer.play),
            #         action('♪', self.buzzer.rest),
            #         # and
            #         action('𝅘𝅥𝅯', self.buzzer.play),
            #         action('𝅘𝅥𝅯', self.buzzer.rest),
            #         # a
            #         action('𝅘𝅥𝅯', self.buzzer.play),
            #         action('𝅘𝅥𝅯', self.buzzer.rest),
            #     )
            # )
        )

    def ringer_measure(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        return section(
            ringer(
                ' |  𝅗𝅥 𝄼  | ',
            ),
            # actions(
            #     ' |  𝅗𝅥 𝅗𝅥  | ',
            #     self.ringer.play,
            #     self.ringer.rest,
            # )
        )

    def section_b(self) -> Section:
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝅘𝅥𝅱 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀 𝅁
        return section(
            drums(
                '  |  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰  3𝅘𝅥𝅰> 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 3𝅘𝅥𝅰 '
                '     3𝅘𝅥𝅯> 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯 3𝅘𝅥𝅯  '
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
    
