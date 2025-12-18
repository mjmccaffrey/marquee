"""Marquee Lighted Sign Project - lightgame"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, Protocol

from color import Color
from lightcontroller import ChannelUpdate
from lightset import LightSet
from modes.basemode import ScheduleCallback


class LightUpdateCallback(Protocol):
    def __call__(self, delta: 'Board') -> list[ChannelUpdate]:
        ...

class StateLogicCallback(Protocol):
    def __call__(self) -> None:
        ...


@dataclass(kw_only=True)
class Entity(ABC):
    """"""
    color: ClassVar[Color]
    draw_priority: ClassVar[int]
    game: 'LightGame'
    name: str
    coord: int = field(init=False)


@dataclass(kw_only=True)
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
EntityGroup = dict[type, Entity]
Maze = dict[int, Square]


@dataclass(kw_only=True)
class LightGame:
    """Play a game with the lights."""
    lights: LightSet
    maze: Maze
    schedule: ScheduleCallback
    state_logic: StateLogicCallback
    light_updates: LightUpdateCallback

    def __post_init__(self):
        """Initialize board and characters."""
        self.board: Board = {coord: {} for coord in self.maze}
        self.characters: list[Character] = []

    def execute_round(self):
        """Execute one game round."""
        self.execute_one_round()
        self.schedule(
            action=self.execute_round,
            due=1.0,
            name='game round',
        )
        
    def execute_one_round(self):
        """Execute one game round."""

        print("BEFORE COPY:")
        self.print_board(self.board)
        old_board = {
            k: v.copy()
            for k, v in self.board.items()
        }
        
        for character in self.characters:
            character.execute_turn()
        delta_board = self.compare_boards(old_board)
        updates = self.light_updates(delta_board)
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
        entities = zip(self.board.values(), old_board.values())
        result = {
            i: new
            for i, (new, old) in enumerate(entities)               
            if new != old
        }
        print("OLD:")
        self.print_board(old_board)
        print("NEW:")
        self.print_board(self.board)
        print("DELTA:")
        self.print_board(result)
        return result

    def create_entity(self, etype: type[Entity], name: str) -> Entity:
        """Create entity. Convert color. Place on board."""
        entity = etype(game=self, name=name)  # type: ignore
        if isinstance(entity, Character):
            self.characters.append(entity)
            self.characters.sort(key = lambda c: c.turn_priority)
        return entity

    def move_entity(self, entity: Entity, coord: int):
        """Move entity to coordinate."""
        del self.board[entity.coord][type(entity)]
        self.place_entity(entity, coord)

    def place_entity(self, entity: Entity, coord: int):
        """Place entity on board at coord."""
        entity.coord = coord
        self.board[entity.coord][type(entity)] = entity

