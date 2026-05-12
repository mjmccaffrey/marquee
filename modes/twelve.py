"""Marquee Lighted Sign Project - twelve"""

from dataclasses import dataclass
from functools import partial
import logging
import pygame
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
        self.lights.set_channels(on=False)
        pygame.mixer.init()
        pygame.mixer.music.load('modes/twelve.mp3')
        self.prep_lights()
        # self.play_basic()
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

    def play_basic(self):
        """"""

        def schedule_12(delay: float):
            """"""
            #
            delays = (0.0,) + tuple(
                (n / bps) 
                for n in notes[:-1]
            )
            for i, d in enumerate(delays):
                delay += d
                self.schedule(
                    due=delay,
                    action=partial(
                        self.lights.set_channels,
                        on=True,
                        transition=0.0,
                        indices={(i + 2) % self.lights.count},
                    )
                )
            #
            self.schedule(
                due=delay + 2.0,
                action=partial(
                    self.lights.set_channels,
                    on=False,
                ),
            )
        
        notes = (
            0.5, 0.5, 0.5, 1, 1, 0.5,
            1, 0.5, 1, 1, 1.5, 1,
        )
        bps = self.tempo / 60
        pygame.mixer.music.play()
        schedule_12(3 * 4 / bps)
        schedule_12(9.25 * 4 / bps)


    def play_music(self):
        """"""
        set_mode(self)
        indices = iter([i for i in range(self.lights.count)] * 2)

        def turn_on():
            """"""
            index = next(indices)
            self.lights.set_channels(
                on=True,
                transition=0.0,
                indices={(index + 2) % self.lights.count},
            )

        def play_mp3():
            """"""
            pygame.mixer.music.play()

        lights_on = (turn_on,) * 12
        lights_off = partial(self.lights.set_channels, on=False)
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        count_to_12 = '  |  ♪ ♪ ♪ ♩ ♩ ♪  |  ♩ ♪ ♩ ♩ ♪  |  𝄽 ♩  |  '
        piece(
            section(
                act_part(' |  ♩  | ', play_mp3),
                act_part(' |  𝄻  |  𝄻  |  𝄻  | '),
            ),
            act_part(count_to_12, *lights_on),
            part(measure(beats=2)),
            act_part('  ♩ 𝄽 𝄼  ', lights_off),
            part(measure(beats=3)),
            act_part(count_to_12, *lights_on),
        ).play(tempo=160)
    
