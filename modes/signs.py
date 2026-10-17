"""Marquee Lighted Sign Project - signs 2026"""

from typing_extensions import override

from . import MusicMode
from music import lights, piece

import pygame


class Signs(MusicMode):
    """Signs song excerpt."""

    @override
    def execute(self) -> None:
        """Perform Signs song."""
        pygame.mixer.music.load('modes/signs_3.wav')
        self.lights.set_channels(on=False, transition=0.0)
        self.schedule(action=self.perform, due=0.25)

    def perform(self):
        """Play music and lights."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        pygame.mixer.music.play()
        even = [0, 2, 4, 6, 8, 10]
        odd = [1, 3, 5, 7, 9, 11]
        sequence = [
            dict(
                on=True, 
                color=self.lights.colors.RED, 
                brightness=100,
                transition=0.0,
                force=True,
            ),
            dict(
                color=self.lights.colors.DEEP_GOLD, 
                transition=0.0,
            ),
            dict(
                index=even,
                color=self.lights.colors.RED, 
                transition=0.0,
            ),
            dict(
                index=even,
                color=self.lights.colors.DEEP_GOLD,
                transition=0.0,
            ),
            dict(
                index=odd,
                color=self.lights.colors.RED,
                transition=0.0,
            ),
            dict(
                on=False,
                transition=6.0,
            ),
        ]
        music = piece(
            lights(
                ' | ♩  ♩  ♩  𝅘𝅥𝅲 𝅘𝅥𝅲 𝅁 𝅀 𝄿 𝄾 | 𝄻 | 𝅝 | ', 
                *sequence,
            ),
        )
        self.play(music, tempo=75)

