"""Marquee Lighted Sign Project - twelve"""

from dataclasses import dataclass
from functools import partial
import logging
from pygame import mixer
from typing_extensions import override

from .musicmode import MusicMode
from music import act_part, measure, part, piece, section, set_mode

log = logging.getLogger('marquee.' + __name__)

@dataclass(kw_only=True)
class Twelve(MusicMode):
    """"""
    colors = (
        (100, 0, 0),
        (100, 50, 0),
        (100, 100, 0),
        (50, 80, 0),
        (0, 100, 0),
        (0, 100, 50),
        (0, 100, 100),
        (0, 60, 100),
        (0, 0, 100),
        (50, 0, 100),
        (100, 0, 100),
        (100, 0, 50),
    )
    tempo = 160

    @override
    def execute(self):
        """"""
        set_mode(self)
        self.lights.set_channels(on=False)
        mixer.init()
        mixer.music.load('modes/twelve.mp3')
        self.prep_lights()
        self.play_music()

    def prep_lights(self):
        """"""
        for i, (r, g, b) in enumerate(self.colors):
            self.lights.set_channels(
                brightness=40,
                color=self.lights.colors.rgb(
                    int(r / 100 * 255),
                    int(g / 100 * 255),
                    int(b / 100 * 255),
                ),
                indices={i},
            )

    def play_music(self):
        """"""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀

        def light_on():
            """"""
            self.lights.set_channels(
                on=True,
                transition=0.0,
                indices={(next(indices) + 2) % self.lights.count},
            )

        indices = iter([i for i in range(self.lights.count)] * 2)
        lights_on = (light_on,) * 12
        lights_off = partial(self.lights.set_channels, on=False)
        count_to_12 = ' |  ♪ ♪ ♪ ♩ ♩ ♪  |  ♩ ♪ ♩ ♩ ♪  |  𝄽 ♩  | '
        piece(
            section(
                act_part(' |  ♩  | ', mixer.music.play),
                act_part(' |  𝄻  |  𝄻  |  𝄻  | '),
            ),
            act_part(count_to_12, *lights_on),
            part(measure(beats=2)),
            act_part(' |  ♩ 𝄽 𝄼  |  𝄻  | ', lights_off),
            part(measure(beats=3)),
            act_part(count_to_12, *lights_on),
            act_part(' |  𝄻  |  ♩  | ', lights_off),
        ).play(tempo=160)
    
