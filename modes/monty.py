"""Marquee Lighted Sign Project - monty"""

from dataclasses import dataclass
import logging
import pygame
from typing_extensions import override

from devices.color import Colors
from light_defs import *
from . import MusicMode
from music import lights, piece

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class Monty(MusicMode):
    """"""
    brightness: int

    @override
    def execute(self):
        """"""
        self.lights.set_channels(
            on=True,
            brightness=self.brightness,
            color=Colors.DEEP_GOLD,
        )
        pygame.mixer.music.load('modes/monty.mp3')
        pygame.mixer.music.play()
        self.schedule(due=0.5, action=self.perform)

    def perform(self):
        """Play music and lights."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        each_side_red = tuple(
            dict(
                color=Colors.RED,
                transition=0.0,
                index=lights,
            )
            for lights in [
                LIGHTS_TOP, LIGHTS_LEFT, LIGHTS_RIGHT, LIGHTS_BOTTOM,
            ]
        )
        each_side_gold = tuple(
            dict(
                color=Colors.DEEP_GOLD,
                transition=0.0,
                index=lights,
            )
            for lights in [
                LIGHTS_BOTTOM, LIGHTS_LEFT + LIGHTS_RIGHT, LIGHTS_TOP, [Light.CP],
            ]
        )
        each_side_tri = tuple(
            dict(
                color=(Colors.RED, Colors.YELLOW, Colors.WHITE),
                transition=0.0,
                index=lights,
            )
            for lights in [
                LIGHTS_TOP, LIGHTS_LEFT, LIGHTS_RIGHT, LIGHTS_BOTTOM,
            ]
        )
        music = piece(
            lights('| ♩ ♩ ♩ ♩ |', *each_side_red),
            lights('| ♩ ♩ ♩ ♩ |', *each_side_gold),
            lights('| ♩ ♩ ♩ ♩ |', *each_side_tri),
        )
        self.play(music, tempo=120)
        Colors.DEEP_GOLD
        Colors.RED
        Colors.ROSE
        Colors.WHITE


