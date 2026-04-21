"""Marquee Lighted Sign Project - gamemode"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import ClassVar, TypeVar

from devices.color import Color
from devices.lightcontroller import LightChannel, ChannelUpdate
from .performancemode import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True, repr=False)
class Entity(ABC):
    """Non-character entities cannot move and cannot appear mid-level."""
    color: ClassVar[Color]
    draw_priority: ClassVar[int]
    game: 'GameMode'
    name: str
    brightness: int = 100
    coord: int | None = None

    def __repr__(self):
        """"""
        return self.name


@dataclass(kw_only=True, repr=False)
class Character(Entity, ABC):
    """Characters can move and appear mid-level."""
    turn_priority: ClassVar[int]
    prior_coord: int | None = None
 
    @abstractmethod
    def execute(self) -> None:
        """Take turn."""


@dataclass(kw_only=True)
class Square:
    left: int | None = None
    right: int | None = None
    up: int | None = None
    down: int | None = None
    upleft: int | None = None
    downleft: int | None = None
    upright: int | None = None
    downright: int | None = None


Board = dict[int, 'EntityGroup']
EntityGroup = dict[type[Entity], Entity]
Maze = dict[int, Square]
E = TypeVar("E", bound=Entity)

@dataclass(kw_only=True)
class GameMode(PerformanceMode):
    """Play a game with the lights."""
    maze: Maze
    ticks_per_second: float # !!! adjust by speed_factor

    def __post_init__(self):
        """"""
        self.PLAY_GAME_STATE = self.play_game_state
        self.state: Callable[[], None]

    @abstractmethod
    def desired_light_state(
            self, 
            entities: EntityGroup, 
            channel: LightChannel,
        ) -> ChannelUpdate:
        """"""

    @abstractmethod
    def state_logic(self):
        """"""

    def change_state(self, state: Callable):
        """"""
        self.tasks.delete_owned_by(self)
        self.state = state

    def init_level(self):
        """"""
        self.board: Board = {coord: {} for coord in sorted(self.maze)}
        self.characters_by_name: dict[str, Character] = {}
        self.characters_turn_order: list[Character] = []
        self.tick: int = 0

    def execute(self) -> None:
        """"""
        self.state()

    def play_game_state(self):
        """"""
        self.schedule(
            action=self.play_game_round,
            due=(1 / self.ticks_per_second),
            repeat=True,
        )

    def play_game_round(self):
        """Execute a game round."""
        old_board = {
            k: v.copy()
            for k, v in self.board.items()
        }
        for character in self.characters_turn_order:
            character.execute()
        delta_board = self.compare_boards(old_board)
        self.update_lights(delta_board)
        self.state_logic()
        self.tick += 1

    def light_updates(self, board: Board) -> list[ChannelUpdate]:
        """"""
        return [
            self.desired_light_state(
                entities=e, channel=self.lights.channels[i],
            )
            for i, e in board.items()
        ]

    def update_lights(self, board: Board):
        """"""
        updates = self.light_updates(board)
        self.lights.update_channels(updates)

    def print_board(self, board: Board) -> None:
        """"""
        log.info("*****")
        for i in board:
            log.info(i)
            for e in board[i].values():
                log.info("  " + e.name)
        log.info("*****")

    def compare_boards(self, old_board: Board) -> Board:
        """Return a partial board with delta of old and new."""
        result = {
            i: self.board[i]
            for i in self.board.keys()
            if old_board[i] != self.board[i]
        }
        return result

    def register_entity(self, entity: E) -> E:
        """Register and return new entity."""
        if isinstance(entity, Character):
            self.characters_by_name[entity.name] = entity
            self.characters_turn_order.append(entity)
            self.characters_turn_order.sort(key = lambda c: c.turn_priority)
        return entity

    def place_entity(self, entity: Entity, coord: int):
        """Place entity on board at coord, with wrapping."""
        coord = coord % len(self.board)
        entity.coord = coord
        self.board[entity.coord][type(entity)] = entity

    def move_character(self, character: Character, coord: int):
        """Move character to coord, with wrapping."""
        coord = coord % len(self.board)
        assert character.coord is not None
        del self.board[character.coord][type(character)]
        character.prior_coord = character.coord
        self.place_entity(character, coord)

