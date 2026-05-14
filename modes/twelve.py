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
        for i, color in enumerate(Colors.WHEEL):
            self.lights.set_channels(
                brightness=self.brightness,
                color=color,
                indices={i},
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
        lights_off = dict(on=False)
        count_to_12 = ' |  ♪ ♪ ♪ ♩ ♩ ♪  |  ♩ ♪ ♩ ♩ ♪  |  𝄽 ♩  | '
        piece(
            section(
                actions(' |  ♩  | ', mixer.music.play),
                lights( ' |  𝄻  |  𝄻  |  𝄻  | '),
            ),
            lights(count_to_12, *lights_on),
            lights('  𝅀  ', beats=2),
            lights(' |  ♩  |  𝄻  | ', lights_off),
            lights('  𝅀  ', beats=3),
            lights(count_to_12, *lights_on),
            lights(' |  𝄻  |  ♩  | ', lights_off),
        ).play(tempo=self.tempo)
    
