"""Marquee Lighted Sign Project - twelve"""

from dataclasses import dataclass
import logging
from pygame import mixer
from typing_extensions import override

from devices.color import Colors
from .musicmode import MusicMode
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
        lights_on = tuple(
            dict(
                on=True,
                transition=0.0,
                indices={(i + 2) % self.lights.count},
            )
            for i in range(self.lights.count)
        )
        lights_off = dict(on=False, transition=0.0)
        lights_rotate = tuple(
            dict(
                color=Colors.WHEEL[i:] + Colors.WHEEL[:1],
                transition=0.0,
            )
            for i in range(self.lights.count)
        )


        # light_pairs_off = tuple(
        #     dict(
        #         on=False,
        #         transition=0.0,
        #         indices=i,
        #     )
        #     for i in ({0, 2}, {11, 3}, {10, 4}, {9, 5}, {8, 6}, {1, 7})
        # )
        count_to_12 = ' |  ♪ ♪ ♪ ♩ ♩ ♪  |  ♩ ♪ ♩ ♩ ♪  |  𝄽 ♩  | '
        piece(
            section(
                actions(' |  ♩  | ', mixer.music.play),
                lights( ' |  𝄻  |  𝄻  |  𝄻  | '),
            ),
            lights(count_to_12, *lights_on),
            lights(' |  𝄽 𝄽  | ', beats=2),
            # lights(' |  𝄼 ♩ ♩  |  ♩ ♩ ♩ ♩  | ', *light_pairs_off),
            # lights(' |  𝄻  |  𝄻  | '),
            lights(' |  ♩ 𝄽 ♩ 𝄽  |  ♩ 𝄽 ♩ 𝄽  | ', *lights_rotate),
            lights(' |  𝄽 ♩ 𝄽  | ', lights_off, beats=3),
            lights(count_to_12, *lights_on),
            lights(' |  𝄻  |  ♩  | ', lights_off),
        ).play(tempo=self.tempo)
    
