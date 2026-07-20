"""Marquee Lighted Sign Project - signs 2026"""

from typing_extensions import override

from device_defs import ALL_OFF, ALL_ON
from . import MusicMode, all_on, blink_all, random_each
from music import (
    actions, bells, drums, lights,
    dimmer_sequence_flip, piece, section, Section, sequence,
)
import pygame


class Signs(MusicMode):
    """Signs song excerpt."""

    @override
    def execute(self) -> None:
        """Perform Signs song."""
        pygame.mixer.music.load('modes/signs_3.mp3')
        pygame.mixer.music.play()
        self.schedule(action=self.play)

    def play(self):
        """Play music and lights."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        even = [i for i in range(self.lights.count) if not i % 2]
        odd = [i for i in range(self.lights.count) if i % 2]
        sequence = [
            dict(
                on=True, 
                color=self.lights.colors.RED, 
                brightness=100,
                transition=0.0,
            ),
            dict(
                color=self.lights.colors.DEEP_GOLD, 
                transition=0.0,
            ),
            dict(
                index=even,
                color=self.lights.colors.RED, 
            ),
        ]
        piece(
            lights(
                ' | ♩  ♩  𝅘𝅥𝅯 𝄿 𝄿 𝄿  ♩ | ', 
                *sequence,
            ),
        ).play(tempo=75)

