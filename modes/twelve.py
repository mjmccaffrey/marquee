"""Marquee Lighted Sign Project - twelve"""

from dataclasses import dataclass
import logging
import pygame
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
            # brightness=self.brightness,
            # color=Colors.WHEEL,
        )
        pygame.mixer.music.load('modes/twelve.mp3')
        pygame.mixer.music.play()
        self.schedule(due=0.25, action=self.play)

    def perform(self):
        """Play music and lights."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        each_on = tuple(
            dict(
                on=True,
                brightness=100,
                color=c,
                transition=0.0,
                index=(i + 2) % self.lights.count,
                force=True,
            )
            for i, c in enumerate(Colors.WHEEL)
        )
        each_off = tuple(
            dict(
                on=False,
                transition=0.8,
                index=i,
            )
            for i in range(self.lights.count)
        )
        all_off = dict(on=False, transition=1.6)
        music = piece(
            lights('| 𝄻 | 𝄻 | 𝄻 |'),
            lights('| ♪ ♪ ♪ ♩ ♩ ♪ | ♩ ♪ ♩ ♩ ♪ | 𝄽 ♩ 𝄽 𝄽 |', *each_on),
            lights('| 𝄽 𝄽 |', beats=2),
            lights('| 3♩ 3♩ 3♩ 3♩ 3♩ 3♩ | 3♩ 3♩ 3♩ 3♩ 3♩ 3♩ |', *each_off),
            lights('| 𝄽 𝄽 𝄽 |', beats=3),
            lights('| ♪ ♪ ♪ ♩ ♩ ♪ | ♩ ♪ ♩ ♩ ♪ | 𝄽 ♩ 𝄽 𝄽 |', *each_on),
            lights('| 𝄻 | ♩ |', all_off),
        )
        self.play(music, tempo=160)

