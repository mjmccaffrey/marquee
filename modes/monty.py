"""Marquee Lighted Sign Project - monty"""

from dataclasses import dataclass
from itertools import cycle
import logging
import pygame
import time
from typing import Any
from typing_extensions import override

from devices.color import Colors, RGB
from light_defs import *
from . import MusicMode
from music import actions, lights, piece


log = logging.getLogger('marquee.' + __name__)

ORANGE_YELLOW = RGB(255, 180, 0)


def rotate(d: tuple, i: int) -> tuple:
    i %= len(d)
    return d[i:] + d[:i]


@dataclass(kw_only=True)
class Monty(MusicMode):
    """"""
    brightness: int

    @override
    def execute(self):
        """"""
        RGB.adjust_incomplete_colors(self.lights.gamut)
        self.lights.set_channels(
            on=True,
            brightness=self.brightness,
            color=Colors.RED,
        )
        self.lights.set_channels(
            on=False,
            index=Light.CP,
        )
        time.sleep(10)
        pygame.mixer.music.load('modes/monty.mp3')
        pygame.mixer.music.play()
        self.schedule(due=0.5, action=self.perform)

    def perform(self):
        """Play music and lights."""
        # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
        top_down = tuple(
            dict(
                color=ORANGE_YELLOW,
                transition=0.0,
                index=lights,
            )
            for lights in [
                LIGHTS_TOP, LIGHTS_LEFT, LIGHTS_RIGHT, LIGHTS_BOTTOM,
            ]
        )
        bottom_up: list[dict[str, Any]] = [
            dict(
                color=Colors.RED,
                transition=0.0,
                on=True,
                index=lights,
            )
            for lights in [
                LIGHTS_BOTTOM, LIGHTS_LEFT + LIGHTS_RIGHT, LIGHTS_TOP, [Light.CP],
            ]
        ]
        bottom_up[-1]['color'] = ORANGE_YELLOW
        colors = (ORANGE_YELLOW, Colors.WHITE, Colors.RED)
        color_rotation = tuple(
            c 
            for i in range(36)
            for c in rotate(colors, i)
        )
        thirds = cycle(("1_of_3", "2_of_3", "3_of_3"))
        rotate_colors = tuple(
            dict(
                color=color,
                transition=0.0,
                group=group,
            )
            for group, color in zip(thirds, color_rotation)
        )
        music = piece(
            lights('| ♩ ♩ ♩ ♩ |', *top_down),
            lights('| ♩ ♩ ♩ ♩ |', *bottom_up),
            lights('| ♩ ♩ ♩ ♩ |' * 9, *rotate_colors),
            actions(
                '| ♩ |', 
                lambda: self.lights.set_channels(
                    color=ORANGE_YELLOW,
                    transition=2.0
                )
            )
        )
        self.play(music, tempo=120)

