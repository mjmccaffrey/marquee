"""Marquee Lighted Sign Project - gamemode"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Sequence

from color import Color
from lightcontroller import LightChannel, ChannelUpdate
from lightset import LightSet
from .performancemode import PerformanceMode


@dataclass(kw_only=True, repr=False)
class Entity(ABC):
    """Non-character entities cannot move and cannot appear mid-level."""
    color: ClassVar[Color]
    draw_priority: ClassVar[int]
    game: 'GameMode'
    name: str
    brightness: int
    coord: int | None = None

    def __repr__(self):
        """"""
        return self.name


@dataclass(kw_only=True, repr=False)
class Character(Entity, ABC):
    """Characters can move and appear mid-level."""
    turn_priority: ClassVar[int]
 
    @abstractmethod
    def execute_turn(self) -> None:
        """Take turn."""


@dataclass(kw_only=True)
class Square:
    left: int | None = None
    right: int | None = None
    up: int | None = None
    down: int | None = None


Board = dict[int, 'EntityGroup']
EntityGroup = dict[type[Entity], Entity]
Maze = dict[int, Square]


@dataclass(kw_only=True)
class GameMode(PerformanceMode):
    """Play a game with the lights."""
    maze: Maze

    def __post_init__(self):
        """Initialize board and characters."""
        self.board: Board = {coord: {} for coord in sorted(self.maze)}
        assert all(c == i for i, c in enumerate(self.board))
        self.characters_by_name: dict[str, Character] = {}
        self.characters_turn_order: list[Character] = []

    def execute(self):
        """"""
        self.tick: int = 0
        self.update_lights(self.board)
        self.schedule(
            action=self.execute_round,
            due_rel=1.0,
            repeat=True,
        )
        
    def execute_round(self):
        """Execute a game round."""
        old_board = {
            k: v.copy()
            for k, v in self.board.items()
        }
        for character in self.characters_turn_order:
            character.execute_turn()
        self.state_logic()
        delta_board = self.compare_boards(old_board)
        self.update_lights(delta_board)
        self.tick += 1

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
        self.lights.controller.update_channels(updates)

    def print_board(self, board: Board) -> None:
        print("*****")
        for i in board:
            print(i)
            for e in board[i].values():
                print("  ", e.name)
        print("*****")

    def compare_boards(self, old_board: Board) -> Board:
        """Return a partial board with delta of old and new."""
        result = {
            i: self.board[i]
            for i in self.board.keys()
            if old_board[i] != self.board[i]
        }
        return result

    def create_entity(self, etype: type[Entity], name: str) -> Entity:
        """Create entity. Convert color. Place on board."""
        entity = etype(game=self, name=name)  # type: ignore
        if isinstance(entity, Character):
            self.characters_by_name[name] = entity
            self.characters_turn_order.append(entity)
            self.characters_turn_order.sort(key = lambda c: c.turn_priority)
        return entity

    def move_entity(self, entity: Entity, coord: int):
        """Move entity to coord, with wrapping."""
        coord = coord % len(self.board)
        assert entity.coord is not None
        del self.board[entity.coord][type(entity)]
        self.place_entity(entity, coord)

    def place_entity(self, entity: Entity, coord: int):
        """Place entity on board at coord, with wrapping."""
        coord = coord % len(self.board)
        entity.coord = coord
        self.board[entity.coord][type(entity)] = entity

