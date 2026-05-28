"""Marquee Lighted Sign Project - doom mode"""

from enum import auto, StrEnum
from dataclasses import dataclass, field
from functools import partial
import logging
import pygame
from typing_extensions import override

from task import SeqTask
from ..gamemode import GameMode
from devices.color import Colors, RGB

log = logging.getLogger('marquee.' + __name__)


class Sound(StrEnum):
    BARON_ROAR = auto()
    SLAYER_UMF = auto()
    SLAYER_DEATH = auto()
    TELEPORT = auto()


@dataclass(kw_only=True)
class DoomGame(GameMode):
    """"""

    def __post_init__(self):
        """Initialize board and characters."""
        super().__post_init__()
        assert self.lights.gamut is not None  # Lights are color.
        RGB.adjust_incomplete_colors(self.lights.gamut)
        self.init_sound()

# (self.lights.set_channels, on=False)
# (self.play_sound, Sound.TELEPORT)
# (self.play_sound, Sound.SLAYER_UMF)
    @override
    def execute(self):
        """"""
        self.schedule_sequence(
            SeqTask(action=self.init_lights, due=0.0),
            SeqTask(action=self.teleport, due=1.0),
            SeqTask(action=self.slayer_appears, due=1.0),
            SeqTask(action=self.barrons_appear, due=1.0),
            SeqTask(action=self.slayer_dies, due=1.0),
        )
        # music?
        
    def init_sound(self):
        """"""
        pygame.mixer.init()
        self.sounds = {
            sound: pygame.mixer.Sound(f'modes/doom/doom_{sound}.wav')
            for sound in Sound
        }

    def play_sound(self, sound: Sound):
        """"""
        self.sounds[sound].play()

