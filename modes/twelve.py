"""Marquee Lighted Sign Project - twelve"""

from dataclasses import dataclass
from functools import partial
import logging
import pygame
from typing_extensions import override

from .musicmode import MusicMode
from music import act_part, section, set_mode

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
        # Turn all off
        self.lights.set_channels(on=False)

        # Set up sound
        pygame.mixer.init()
        pygame.mixer.music.load('modes/twelve.mp3')

        # Set each color
        for i, (r, g, b) in enumerate(self.colors):
            self.lights.set_channels(
                brightness=28,
                color=self.lights.colors.rgb(
                    int(r / 100 * 255),
                    int(g / 100 * 255),
                    int(b / 100 * 255),
                ),
                channel_indexes={i},
            )

        next = self.play_basic()
        # restart_seconds = self.play_music()
        # log.info(f"{restart_seconds=}")

    def play_basic(self):
        """"""

        def schedule_12(delay: float):
            """"""
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
                        channel_indexes={i},
                    )
                )
            self.schedule(
                due=delay + 4.0,
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
        schedule_12(3 * 24 / bps)


    def play_music(self) -> float:
        """"""
        set_mode(self)
        indices = iter(range(self.lights.count))

        def turn_on():
            """"""
            index = next(indices)
            self.lights.set_channels(
                on=True,
                transition=0.0,
                channel_indexes={index},
            )

        def play_mp3():
            """"""
            pygame.mixer.music.play()

        song = section(
            # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
            act_part(
                '  ♩  ',
                play_mp3,
            ),
            act_part(
                '  𝄻  |  𝄻  |  𝄻  |  '
                '  ♪ ♪ ♪ ♩ ♩ ♪  |  ♩ ♪ ♩ ♩ ♪  |  𝄽 ♩  ',
                turn_on,
            ),
        )
        restart = song.play(tempo=self.tempo)
        return restart
    
