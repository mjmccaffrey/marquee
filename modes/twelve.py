"""Marquee Lighted Sign Project - twelve"""

from dataclasses import dataclass
import logging
from pygame import mixer
from typing_extensions import override

from devices.color import Colors
from . import MusicMode
from music import lights, piece

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class Twelve(MusicMode):
    """"""
    brightness: int

    @override
    def execute(self):
        """"""
        self.lights.set_channels(
            on=False,
            brightness=self.brightness,
            color=Colors.WHEEL,
        )
        mixer.init()
        mixer.music.load('modes/twelve.mp3')
        mixer.music.play()
        self.schedule(due=0.25, action=self.play)

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
        lights_all_off = dict(on=False, transition=0.8)
        each_light_off = tuple(
            dict(
                on=False,
                transition=1.25,
                indices={i},
            )
            for i in range(self.lights.count)
        )
        count_to_12 = ' |  ♪ ♪ ♪ ♩ ♩ ♪  |  ♩ ♪ ♩ ♩ ♪  |  𝄽 ♩ 𝄽 𝄽  | '
        piece(
            lights( ' |  𝄻  |  𝄻  |  𝄻  | '),
            lights(count_to_12, *each_light_on),
            lights(' |  𝄽 𝄽  | ', beats=2),
            lights(' |  3♩ 3♩ 3♩ 3♩ 3♩ 3♩ |  3♩ 3♩ 3♩ 3♩ 3♩ 3♩  | ', *each_light_off),
            lights(' |  𝄽 𝄽 𝄽  | ', beats=3),
            lights(count_to_12, *each_light_on),
            lights(' |  𝄻  |  ♩  | ', lights_all_off),
        ).play(tempo=160)
    
