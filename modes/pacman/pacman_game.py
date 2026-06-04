"""Marquee Lighted Sign Project - pacman mode"""

from dataclasses import dataclass
from enum import auto, StrEnum
from functools import partial
from itertools import cycle
import logging
import pygame
from typing import Any, cast
from typing_extensions import override

from devices.color import Colors, RGB
from devices.devices_misc import ButtonName
from ..gamemode import Entity, EntityGroup, GameMode
from . import pacman_assets as assets
from .pacman_assets import (
    Dot, Fruit, Ghost, PacMan, Pinky, Blinky, Sound,
    maze_base, maze_with_passage,
)
from devices.lightcontroller import LightChannel, ChannelUpdate

log = logging.getLogger('marquee.' + __name__)


@override
class GameState(StrEnum):
    """"""
    PRE_GAME = auto()
    PLAY_GAME = auto()
    PRE_LEVEL_0 = auto()
    PRE_LEVEL_1 = auto()
    POST_LEVEL_0 = auto()
    GAME_LOST = auto()
    GAME_WON = auto()


class Event(StrEnum):
    """"""
    BITE = auto()


@dataclass(kw_only=True)
class PacManGame(GameMode):
    """"""
    squares: int = 12
    ticks_per_second: float = 2.0
    # mazes = {
    #     12: maze_base,
    #     15: maze_with_passage,
    # }
    pacman_start = 7
    fruit_start = 13

    def __post_init__(self):
        """Initialize board and characters."""
        super().__post_init__()
        self.lights = self.combined
        assert self.lights.gamut is not None  # Lights are color.
        RGB.adjust_incomplete_colors(self.lights.gamut)
        self.init_sound()
        self.events.subscribe(Event.BITE, self.pacman_bite)
        self.state = GameState.PRE_GAME
        # self.maze = self.mazes[self.squares]
        self.level: int

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

    @override
    def button_action(self, button: ButtonName) -> int | None:
        """"""
        if (
            button == ButtonName.GAME_START and
            self.state == GameState.PRE_GAME
        ):
            self.change_state(GameState.PRE_LEVEL_0)
        else:
            return super().button_action(button)

    @override
    def interrupt_action(self, args: tuple[Any, ...]) -> None:
        """"""

    def pacman_bite(self, etype: type, coord: int):
        """Track remaining. Brighten extra bulb."""
        match etype:
            case assets.Dot:
                dot = cast(Dot, self.board[coord][etype])
                dot.bitten()
                if dot.consumed:
                    del self.board[coord][Dot]
                # assert self.extra is not None
                # self.extra.set_channels(
                #     brightness=int(
                #         (self.dot_bites_maximum  - 
                #         self.dot_bites_remaining) * 
                #         100 / self.dot_bites_maximum
                #     )
                # )
                self.play_sound(Sound.CHOMP)
            case assets.Fruit:
                del self.board[coord][Fruit]
                self.play_sound(Sound.EATFRUIT)
            case _:
                raise RuntimeError(etype)

    @override
    def init_level(self) -> None:
        """"""
        super().init_level()
        assert self.extra is not None
        self.extra.set_channels(brightness=0, on=True)
        self.extra.set_relays(True)
        for index in self.maze.keys():
            dot = self.register_entity(
                Dot(game=self, name=f"dot_{index}")
            )
            self.place_entity(dot, index)
        self.fruit = self.register_entity(
            Fruit(name='orange', game=self)
        )
        self.pacman = self.register_entity(
            PacMan(game=self, bite_event=Event.BITE)
        )
        self.blinky = self.register_entity(
            Blinky(
                game=self, 
                direction=+1,
                wait_ticks=75 if self.level == 0 else 50,
            )
        )
        self.pinky = self.register_entity(
            Pinky(
                game=self, 
                direction=-1,
                wait_ticks=999999 if self.level == 0 else 100,
            )
        )
        self.ghosts = (self.pinky, self.blinky)
        self.update_lights(self.board)

    def play_level(self) -> None:
        """"""
        self.place_entity(self.pacman, self.pacman_start)
        cast(Dot, self.board[self.pacman_start][Dot]).bitten()
        self.update_lights(self.board)
        self.schedule(
            action=partial(self.change_state, GameState.PLAY_GAME), 
            due=2.0,
        )

    def pre_game_state(self) -> None:
        """"""
        log.info("Waiting for Start Game button press")
        self.buttons.game_start.set_light(True)

    def pre_level_0_state(self) -> None:
        """"""
        self.play_sound(Sound.BEGINNING)
        self.level = 0
        self.schedule(due=3.0, action=partial(self.init_level))
        self.schedule(due=5.0, action=partial(self.play_level))

    def pre_level_1_state(self) -> None:
        """"""
        self.level = 1
        self.schedule(action=partial(self.init_level))
        self.schedule(due=2.0, action=partial(self.play_level))

    def post_level_0_state(self) -> None:
        """"""
        self.play_sound(Sound.INTERMISSION)
        for i, c in zip(range(4), cycle((Colors.WHITE, Colors.BLUE))):
            kwargs = dict(color=c, transition=0)
            if i == 0:
                kwargs |= dict(on=True)
            self.schedule(
                due=(1 + i),
                action=partial(self.lights.set_channels, **kwargs),
            )
        self.level = 1
        self.schedule(
            due=6.0, action=partial(self.change_state, GameState.PRE_LEVEL_1)
        )

    def game_won_state(self) -> None:
        """"""
        log.info("You won!")
        self.play_sound(Sound.EXTRAPAC)
        self.schedule(due=5.0, action=partial(self.change_state, GameState.PRE_GAME))

    def game_lost_state(self) -> None:
        """"""
        log.info("You lost!")
        self.play_sound(Sound.DEATH)
        self.schedule(due=5.0, action=partial(self.change_state, GameState.PRE_GAME))

    @override
    def execute_state(self) -> None:
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
        """"""
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
            self.place_entity(self.fruit, self.fruit_start)
            self.update_lights(self.board)  # ???? !!!!

    def ghost_got_pacman(self) -> bool:
        """"""
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
        """"""
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

