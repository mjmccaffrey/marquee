"""Marquee Lighted Sign Project - doom mode"""

from enum import auto, StrEnum
from dataclasses import dataclass, field
from functools import partial
import logging
import pygame
from typing_extensions import override

from light_defs import LIGHTS_BY_ROW
from task import SeqTask
from ..performancemode import PerformanceMode
from devices.color import Colors, RGB

log = logging.getLogger('marquee.' + __name__)


class Sound(StrEnum):
    BARON_ROAR = auto()
    SLAYER_UMF = auto()
    SLAYER_DEATH = auto()
    TELEPORT = auto()


@dataclass(kw_only=True)
class DoomGame(PerformanceMode):
    """"""

    def __post_init__(self):
        """Initialize board and characters."""
        super().__post_init__()
        assert self.lights.gamut is not None  # Lights are color.
        RGB.adjust_incomplete_colors(self.lights.gamut)
        self.init_sound()
        self.lights.set_channels(on=False)

    def init_sound(self):
        """"""
        pygame.mixer.init()
        self.sounds = {
            sound: pygame.mixer.Sound(f'modes/pacman/pacman_{sound}.wav')
            for sound in Sound
        }

    def play_sound(self, sound: Sound):
        """"""
        self.sounds[sound].play()

    def slayer_teleports(self):
        """"""
        self.play_sound(Sound.TELEPORT)
        self.lights.set_channels(
            color=Colors.TEAL,
            transition=1.0,
            indices={1},
        )

    def slayer_appears(self):
        """"""
        self.play_sound(Sound.SLAYER_UMF)
        self.lights.set_channels(
            color=Colors.GREEN,
            transition=0.0,
            indices={1},
        )

    def barons_appear(self, row: int):
        """"""
        self.play_sound(Sound.BARON_ROAR)
        self.lights.set_channels(
            color=Colors.RED,
            transition=0.0,
            indices=set(LIGHTS_BY_ROW[row]),
        )

    def slayer_dies(self):
        """"""
        self.play_sound(Sound.SLAYER_DEATH)
        self.lights.set_channels(
            color=Colors.RED,
            transition=0.0,
        )

    def fade(self):
        """"""
        for i, row in enumerate(LIGHTS_BY_ROW):
            self.schedule(
                action=partial(
                    self.lights.set_channels,
                    brightness=0,
                    transition=1.0,
                    indices=set(row),
                ),
                due=i / 2,
            )
        
    @override
    def execute(self):
        """"""
        self.schedule_sequence(
            SeqTask(self.slayer_teleports, due=1.0),
            SeqTask(self.slayer_appears, due=1.0),
            SeqTask(partial(self.barons_appear, 4), due=1.0),
            SeqTask(partial(self.barons_appear, 3), due=1.0),
            SeqTask(partial(self.barons_appear, 2), due=1.0),
            SeqTask(partial(self.barons_appear, 1), due=1.0),
            SeqTask(self.slayer_dies, due=1.0),
            SeqTask(self.fade, due=1.0),
        )
        
