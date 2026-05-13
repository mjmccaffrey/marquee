"""Marquee Lighted Sign Project - twelve"""

from dataclasses import dataclass
from functools import partial
import logging
from pygame import mixer
from typing_extensions import override

from devices.color import Colors
from .musicmode import MusicMode
from music import act_part, piece, set_mode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class Twelve(MusicMode):
    """"""
    brightness: int
    TEMPO = 160

    @override
    def execute(self):
        """"""
        set_mode(self)
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

    def light_on(self, index: int):
        """Turn the next light on."""
        self.lights.set_channels(
            on=True,
            transition=0.0,
            indices={index},
        )

    def play(self):
        """Play music and lights."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        lights_on = tuple(
            partial(self.light_on, (i + 2) % self.lights.count)
            for i in range(self.lights.count)
        )
        lights_off = partial(self.lights.set_channels, on=False)
        count_to_12 = ' |  ♪ ♪ ♪ ♩ ♩ ♪  |  ♩ ♪ ♩ ♩ ♪  |  𝄽 ♩  | '
        piece(
            act_part(' |  ♩  |  𝄻  |  𝄻  | ', mixer.music.play),
            act_part(count_to_12, *lights_on),
            act_part('', beats=2),
            act_part(' |  ♩  |  𝄻  | ', lights_off),
            act_part('', beats=3),
            act_part(count_to_12, *lights_on),
            act_part(' |  𝄻  |  ♩  | ', lights_off),
        ).play(tempo=self.TEMPO)
    
