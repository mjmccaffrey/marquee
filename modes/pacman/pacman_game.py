"""Marquee Lighted Sign Project - pacman mode"""

from dataclasses import dataclass
from enum import auto, StrEnum
from functools import partial
from itertools import cycle
import logging
import pygame
from typing import cast
from typing_extensions import override

from devices.color import Colors, RGB
from devices.devices_misc import ButtonName, Device
from light_defs import LIGHTS_CUPOLA
from ..abstract.gamemode import Entity, EntityGroup, GameMode
from . import pacman_assets as assets
from .pacman_assets import (
    Dot, Fruit, Ghost, GhostState, PacMan, Pinky, Blinky, Sound,
    passage_maze,
)
from devices.lightcontroller import LightChannel, ChannelUpdate

log = logging.getLogger('marquee.' + __name__)


@override
class GameState(StrEnum):
    """Game state."""
    PRE_GAME = auto()
    PLAY_GAME = auto()
    PRE_LEVEL_0 = auto()
    PRE_LEVEL_1 = auto()
    POST_LEVEL_0 = auto()
    GAME_LOST = auto()
    GAME_WON = auto()


class Event(StrEnum):
    """Event communicated with EventSystem."""
    PACMAN_BITE = auto()
    GHOST_STATE = auto()


@dataclass(kw_only=True)
class PacManGame(GameMode):
    """Pac-Man game."""
    ticks_per_second: float = 1.7

    def __post_init__(self):
        """Initialize board and characters."""
        super().__post_init__()
        self.pacman_coord = 7
        self.fruit_coord = 13 if self.maze == passage_maze else 7
        self.lights = self.combined
        assert self.lights.gamut is not None  # Lights are color.
        RGB.adjust_incomplete_colors(self.lights.gamut)
        self.init_sound()
        self.events.subscribe(Event.GHOST_STATE, self.ghost_state)
        self.events.subscribe(Event.PACMAN_BITE, self.pacman_bite)
        self.state = GameState.PRE_GAME
        self.level: int

    def init_sound(self):
        """Load sounds."""
        self.sounds = {
            sound: pygame.mixer.Sound(f'modes/pacman/pacman_{sound}.wav')
            for sound in Sound
        }

    def play_sound(self, sound: Sound):
        """Play sound."""
        self.sounds[sound].play()

    @override
    def button_action(self, button: ButtonName) -> int | None:
        """Handle Game Start button push."""
        if (
            button == ButtonName.GAME_START and
            self.state == GameState.PRE_GAME
        ):
            self.change_state(GameState.PRE_LEVEL_0)
        else:
            return super().button_action(button)

    def ghost_state(self, ghost: Ghost, state: GhostState) -> None:
        """"""
        match state:
            case GhostState.WAITING:
                pass
            case GhostState.EMERGING:
                self.lights.set_channels(
                    index=LIGHTS_CUPOLA,
                    on=True,
                    color=ghost.color,
                    brightness=80,
                )
            case GhostState.CHASING:
                self.lights.set_channels(
                    index=LIGHTS_CUPOLA,
                    on=False,
                )

    def pacman_bite(self, etype: type, coord: int) -> None:
        """Effect PacMan bighting something."""
        match etype:
            case assets.Dot:
                dot = cast(Dot, self.board[coord][etype])
                dot.bitten()
                if dot.consumed:
                    del self.board[coord][Dot]
                self.play_sound(Sound.EATDOT)
            case assets.Fruit:
                del self.board[coord][Fruit]
                self.play_sound(Sound.EATFRUIT)
            case _:
                raise RuntimeError(etype)

    @override
    def init_level(self) -> None:
        """Initialize either level."""
        super().init_level()
        for index in self.maze.keys():
            dot = self.register_entity(
                Dot(game=self, name=f"dot_{index}")
            )
            self.place_entity(dot, index)
        self.fruit = self.register_entity(
            Fruit(
                game=self,
                color=Colors.VIOLET if self.level == 0 else Colors.ORANGE,
            )
        )
        self.pacman = self.register_entity(
            PacMan(
                game=self, 
                bite_event=Event.PACMAN_BITE,
                joystick=self.devices[Device.JOYSTICK],
            )
        )
        self.blinky = self.register_entity(
            Blinky(
                game=self, 
                state_event=Event.GHOST_STATE,
                direction=+1,
                wait_ticks=65 if self.level == 0 else 40,
                emerge_ticks=75 if self.level == 0 else 50,
            )
        )
        self.pinky = self.register_entity(
            Pinky(
                game=self, 
                state_event=Event.GHOST_STATE,
                direction=-1,
                wait_ticks=999989 if self.level == 0 else 90,
                emerge_ticks=999999 if self.level == 0 else 100,
            )
        )
        self.ghosts = (self.pinky, self.blinky)
        self.lights.set_channels(
            on=False,
            index=LIGHTS_CUPOLA,
        )
        self.update_lights()

    def play_level(self) -> None:
        """Play either level."""
        self.place_entity(self.pacman, self.pacman_coord)
        cast(Dot, self.board[self.pacman_coord][Dot]).bitten()
        self.update_lights()
        self.sounds[Sound.SIREN].play(-1)
        self.change_state(GameState.PLAY_GAME)

    def pre_game_state(self) -> None:
        """Before game starts."""
        log.info("Waiting for Start Game button press")
        self.buttons.game_start.set_light(True)
        self.lights.set_channels(
            on=True,
            brightness=50,
            color=PacMan.color,
        )

    def pre_level_0_state(self) -> None:
        """Before level 0 starts."""
        self.play_sound(Sound.BEGINNING)
        self.level = 0
        self.schedule(due=3.0, action=partial(self.init_level))
        self.schedule(due=5.0, action=partial(self.play_level))

    def pre_level_1_state(self) -> None:
        """Before level 1 starts."""
        self.level = 1
        self.schedule(action=partial(self.init_level))
        self.schedule(due=2.0, action=partial(self.play_level))

    def post_level_0_state(self) -> None:
        """Play music. Blink all maze lights. Start level 1."""
        self.sounds[Sound.SIREN].stop()
        self.play_sound(Sound.INTERMISSION)
        for i, c in zip(range(4), cycle((Colors.WHITE, Colors.BLUE))):
            kwargs = dict(
                color=c, 
                transition=0, 
                # group='0.15' if self.maze == passage_maze else '0.12'
            )
            if i == 0:
                kwargs |= dict(on=True)
            self.schedule(
                due=(1 + i * 1.5),
                action=partial(self.lights.set_channels, **kwargs),
            )
        self.level = 1
        self.schedule(
            due=6.0, action=partial(self.change_state, GameState.PRE_LEVEL_1)
        )

    def game_won_state(self) -> None:
        """Game won."""
        log.info("You won!")
        self.sounds[Sound.SIREN].stop()
        self.sounds[Sound.EXTRAPAC].play(2)
        self.lights.set_channels(
            index=LIGHTS_CUPOLA,
            color=PacMan.color,
            brightness=PacMan.brightness,
            on=True,
        )
        self.schedule(due=5.0, action=partial(self.change_state, GameState.PRE_GAME))

    def game_lost_state(self) -> None:
        """Game lost."""
        log.info("You lost!")
        self.sounds[Sound.SIREN].stop()
        self.play_sound(Sound.DEATH)
        self.lights.set_channels(
            index=LIGHTS_CUPOLA,
            color=self.lights.colors.RED,
            brightness=80,
            on=True,
        )
        self.schedule(due=5.0, action=partial(self.change_state, GameState.PRE_GAME))

    @override
    def execute_state(self) -> None:
        """Execute self.state."""
        assert isinstance(self.state, GameState)
        print(self.state)
        match self.state:
            case GameState.PLAY_GAME:
                func = self.play_game_state
            case GameState.PRE_GAME:
                func = self.pre_game_state
            case GameState.PRE_LEVEL_0:
                func = self.pre_level_0_state
            case GameState.PRE_LEVEL_1:
                func = self.pre_level_1_state
            case GameState.POST_LEVEL_0:
                func = self.post_level_0_state
            case GameState.GAME_LOST:
                func = self.game_lost_state
            case GameState.GAME_WON:
                func = self.game_won_state
        func()

    @override
    def state_logic(self) -> None:
        """Respond to various game events."""
        # If ghost and Pac-Man on same square, or 
        # attempted to pass each other, game is over etc.
        if not any(
            Dot in entities 
            for entities in self.board.values()
        ):
            if self.level == 0:
                self.change_state(GameState.POST_LEVEL_0)
            else:
                self.change_state(GameState.GAME_WON)
            return
        if self.ghost_got_pacman():
            self.change_state(GameState.GAME_LOST)
            return
        if self.tick == 16:
            self.place_entity(self.fruit, self.fruit_coord)

    def ghost_got_pacman(self) -> bool:
        """Ghost and PacMan entered same square, or passed each other."""
        for ghost in self.ghosts:
            if self.pacman.coord == ghost.coord:
                return True
            if (
                self.pacman.prior_coord == ghost.coord and
                self.pacman.coord == ghost.prior_coord
            ):
                assert self.pacman.prior_coord is not None
                self.move_character(self.pacman, self.pacman.prior_coord)
                return True
        return False

    @override
    def desired_light_state(
            self, 
            entities: EntityGroup, 
            channel: LightChannel,
        ) -> ChannelUpdate:
        """Return ChannelUpdate given contents of maze square."""
        # Empty square
        if not entities:
            return ChannelUpdate(channel=channel, on=False)
        # Pac-Man and Ghost
        if (
            PacMan in entities and 
            any(type(ghost) in entities for ghost in self.ghosts)
        ):
            brightness, color = Ghost.brightness, Colors.BLUE
        # 2 Ghosts
        elif len(list(e for e in entities if isinstance(e, Ghost))) > 1:
            brightness, color = Pinky.brightness, Colors.BLUE
        # Other
        else:
            s: list[Entity] = sorted(
                entities.values(), key=lambda e: e.draw_priority,
            )
            brightness, color = s[-1].brightness, s[-1].color
        #
        return ChannelUpdate(
            channel=channel,
            brightness=brightness,
            transition=0,
            color=color,
            on=True,
        )

