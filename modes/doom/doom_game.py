"""Marquee Lighted Sign Project - doom mode"""

from enum import StrEnum
from dataclasses import dataclass
from functools import partial
import logging
import pygame
from typing_extensions import override

from light_defs import LIGHTS_BY_ROW, LIGHTS_BY_SIDE
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
    passage: bool

    def __post_init__(self):
        """Initialize board and characters."""
        super().__post_init__()
        if self.passage:
            self.lights = self.combined
            LIGHTS_BY_ROW[2].extend([12, 13, 14])
            LIGHTS_BY_SIDE.insert(0, [])
        self.slayer_coord = {13 if self.passage else 1}
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
        pygame.mixer.music.load('modes/doom/doom_d_runni2.mp3')
        
    def play_sound(self, sound: Sound):
        """"""
        self.sounds[sound].play()

    def start_music(self):
        """"""
        pygame.mixer.music.play(-1)

    def fade_music(self):
        """"""
        pygame.mixer.music.fadeout(2000)

    def slayer_teleports(self):
        """"""
        self.play_sound(Sound.TELEPORT)
        self.lights.set_channels(
            on=True,
            # brightness=100,
            color=Colors.YELLOW,
            transition=1.0,
            indices=self.slayer_coord,
        )

    def slayer_appears(self):
        """"""
        self.play_sound(Sound.SLAYER_UMF)
        self.lights.set_channels(
            on=True,
            # brightness=100,
            color=Colors.GREEN,
            transition=0.0,
            indices=self.slayer_coord,
        )

    def barons_appear(self, step: int):
        """"""
        self.play_sound(Sound.BARON_ROAR)
        self.lights.set_channels(
            on=True,
            # brightness=100,
            color=Colors.ROSE,
            transition=0.0,
            indices=set(
                LIGHTS_BY_SIDE[step]
                if self.passage else
                LIGHTS_BY_ROW[step]
            )
        )

    def slayer_dies(self):
        """"""
        self.schedule(
            action=partial(self.play_sound, Sound.SLAYER_DEATH_1),
            due=0.0,
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

    def fade_lights(self):
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
            SeqTask(self.start_music, due=0.0),
            SeqTask(self.slayer_teleports, due=2.0),
            SeqTask(self.slayer_appears, due=2.0),
            SeqTask(partial(self.barons_appear, step=4), due=2.0),
            SeqTask(partial(self.barons_appear, step=3), due=0.6),
            SeqTask(partial(self.barons_appear, step=2), due=0.6),
            SeqTask(partial(self.barons_appear, step=1), due=0.6),
            SeqTask(self.slayer_dies, due=0.6),
            SeqTask(self.fade_lights, due=0.5),
            SeqTask(self.fade_music, due=2.0),
        )
        
