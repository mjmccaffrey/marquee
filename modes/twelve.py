"""Marquee Lighted Sign Project - twelve"""

from dataclasses import dataclass
import logging
from pygame import mixer
from typing_extensions import override

from devices.color import Colors
from . import MusicMode
from music import actions, lights, piece, section

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class Twelve(MusicMode):
    """"""
    brightness: int
    tempo: int = 160

    @override
    def execute(self):
        """"""
        self.lights.set_channels(on=False)
        mixer.init()
        mixer.music.load('modes/twelve.mp3')
        self.prep_lights()
        self.play()

    def prep_lights(self):
        """Prepare each light for turning on."""
        self.lights.set_channels(
            brightness=self.brightness,
            color=Colors.WHEEL,
        )

    def play(self):
        """Play music and lights."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        each_light_on = tuple(
            dict(
                on=True,
                brightness=100,
                transition=0.0,
                indices={(i + 2) % self.lights.count},
            )
            for i in range(self.lights.count)
        )
        lights_all_off = dict(on=False)
        light_groups_off = tuple(
            dict(
                on=False,
                indices=i,
            )
            for i in ({11, 0, 1}, {8, 9, 10}, {5, 6, 7}, {2, 3, 4})
        )
        count_to_12 = ' |  ♪ ♪ ♪ ♩ ♩ ♪  |  ♩ ♪ ♩ ♩ ♪  |  𝄽 ♩  | '
        piece(
            section(
                actions(' |  ♩  | ', mixer.music.play),
                lights( ' |  𝄻  |  𝄻  |  𝄻  | '),
            ),
            lights(count_to_12, *each_light_on),
            lights(' |  𝄽 𝄽  | ', beats=2),
            lights(' |  ♩ 𝄽 ♩ 𝄽  |  ♩ 𝄽 ♩ 𝄽  | ', *light_groups_off),
            # lights(' |  𝄻  |  𝄻  | '),
            lights(' |  𝄽 𝄽 𝄽  | ', beats=3),
            lights(count_to_12, *each_light_on),
            lights(' |  𝄻  |  ♩  | ', lights_all_off),
        ).play(tempo=self.tempo)
    
