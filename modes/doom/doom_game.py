"""Marquee Lighted Sign Project - doom mode"""

from enum import StrEnum
from dataclasses import dataclass
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
    BARON_ROAR = 'dsbrssit.wav'
    SLAYER_UMF = 'dsoof.wav'
    SLAYER_DEATH_1 = 'dspldeth.wav'
    SLAYER_DEATH_2 = 'dspdiehi.wav'
    TELEPORT = 'dstelept.wav'


@dataclass(kw_only=True)
class DoomGame(PerformanceMode):
    """"""

    def __post_init__(self):
        """Initialize board and characters."""
        super().__post_init__()
        assert self.lights.gamut is not None  # Lights are color.
        RGB.adjust_incomplete_colors(self.lights.gamut)
        self.init_sound()
        self.lights.set_channels(
            on=False,
            brightness=100,
        )

    def init_sound(self):
        """"""
        pygame.mixer.init()
        self.sounds = {
            sound: pygame.mixer.Sound(f'modes/doom/doom_{sound}')
            for sound in Sound
        }

    def play_sound(self, sound: Sound):
        """"""
        self.sounds[sound].play()

    def slayer_teleports(self):
        """"""
        self.play_sound(Sound.TELEPORT)
        self.lights.set_channels(
            on=True,
            # brightness=100,
            color=Colors.YELLOW,
            transition=1.0,
            indices={1},
        )

    def slayer_appears(self):
        """"""
        self.play_sound(Sound.SLAYER_UMF)
        self.lights.set_channels(
            on=True,
            # brightness=100,
            color=Colors.GREEN,
            transition=0.0,
            indices={1},
        )

    def barons_appear(self, row: int):
        """"""
        self.play_sound(Sound.BARON_ROAR)
        self.lights.set_channels(
            on=True,
            # brightness=100,
            color=Colors.ROSE,
            transition=0.0,
            indices=set(LIGHTS_BY_ROW[row]),
        )

    def slayer_dies(self):
        """"""
        self.schedule(
            action=partial(self.play_sound, Sound.SLAYER_DEATH_1),
        )
        self.schedule(
            action=partial(self.play_sound, Sound.SLAYER_DEATH_2),
            due=0.75,
        )
        self.lights.set_channels(
            on=True,
            # brightness=100,
            color=Colors.RED,
            transition=0.0,
        )

    def fade(self):
        """"""
        for i, row in enumerate(LIGHTS_BY_ROW):
            self.schedule(
                action=partial(
                    self.lights.set_channels,
                    on=False,
                    transition=2.0,
                    indices=set(row),
                ),
                due=i / 4,
            )
        
    @override
    def execute(self):
        """"""
        self.schedule_sequence(
            SeqTask(self.slayer_teleports, due=1.0),
            SeqTask(self.slayer_appears, due=2.0),
            SeqTask(partial(self.barons_appear, row=4), due=2.0),
            SeqTask(partial(self.barons_appear, row=3), due=0.6),
            SeqTask(partial(self.barons_appear, row=2), due=0.6),
            SeqTask(partial(self.barons_appear, row=1), due=0.6),
            SeqTask(self.slayer_dies, due=0.6),
            SeqTask(self.fade, due=0.5),
        )
        
