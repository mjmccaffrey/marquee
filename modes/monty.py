"""Marquee Lighted Sign Project - monty"""

from collections import deque
from dataclasses import dataclass
from itertools import cycle
import logging
import pygame
from typing_extensions import override

from devices.color import Colors
from light_defs import *
from . import MusicMode
from music import lights, piece

log = logging.getLogger('marquee.' + __name__)


def rotate(d: deque) -> tuple:
    d.rotate(1)
    return tuple(d)


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
        colors=deque((Colors.RED, Colors.YELLOW, Colors.WHITE))
        colors_rotating = tuple(
            rotate(colors)
            for _ in range(10)
        )
        rotate_colors = tuple(
            dict(
                color=colors,
                transition=0.0,
                group=group,
            )
            for group, colors in zip(
                cycle(("1_of_3", "2_of_3", "3_of_3")),
                colors_rotating,
            )
        )
        music = piece(
            lights('| ♩ ♩ ♩ ♩ |', *each_side_red),
            lights('| ♩ ♩ ♩ ♩ |', *each_side_gold),
            # lights('| ♩ ♩ ♩ ♩ |', *each_side_tri),
            lights('| ♩ ♩ ♩ ♩ | ♩ ♩ ♩ ♩ |', *rotate_colors),
        )
        self.play(music, tempo=120)
        Colors.DEEP_GOLD
        Colors.RED
        Colors.ROSE
        Colors.WHITE


