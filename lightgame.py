"""Marquee Lighted Sign Project - game"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field

from color import Color, RGB, XY
from lightcontroller import LightChannel, ChannelUpdate
from lightset import LightSet
import rgbxy


@dataclass(kw_only=True)
class Entity(ABC):
    """"""
    game: 'Game'
    name: str
    color: Color
    coord: int
    draw_priority: int


@dataclass(kw_only=True)
class Character(Entity, ABC):
    """Characters can move and appear mid-level."""
    turn_priority: int

    @abstractmethod
    def execute(self) -> None:
        """Take turn."""


@dataclass(kw_only=True)
class Square:
    left: int | None = None
    right: int | None = None
    up: int | None = None
    down: int | None = None

type EntitiesOnSquare = dict[type, Entity]

@dataclass(kw_only=True)
class Game:
    """"""
    converter: rgbxy.Converter
    lights: LightSet
    maze: dict[int, Square]
    schedule: Callable[[Callable, float, str], None]
    state_logic: Callable[[], None]
    board: dict[int, EntitiesOnSquare] = field(init=False)
    characters: list[Character] = field(init=False)

    def __post_init__(self):
        """Initialize board and characters."""
        self.board = {coord: {} for coord in self.maze}
        self.characters = []

    def execute(self):
        """Execute one game turn."""
        # saved_board = self.board.copy()
        for character in self.characters:
            character.execute()
        # SEND ENTIRE BOARD TO SET_CHANNELS AND LET IT DO A DIFF?

    def create_entity(self, etype: type[Entity], name: str) -> Entity:
        """Create entity. Convert color. Place on board."""
        entity = etype(game=self, name=name, coord=coord)  # type: ignore
        if isinstance(c := entity.color, RGB):
            entity.color = XY(*self.converter.rgb_to_xy(c.red, c.green, c.blue))
        if isinstance(entity, Character):
            self.characters.append(entity)
            self.characters.sort(key = lambda c: c.turn_priority)
        return entity

    def move(self, entity: Entity, coord: int):
        """Move entity to coordinate."""
        del self.board[entity.coord][type(entity)]
        self.place(entity, coord)

    def place(self, entity: Entity, coord: int):
        """"""
        entity.coord = coord
        self.board[entity.coord][type(entity)] = entity

    def draw_board(self):
        """Leave it to lightset to determine what actual changes
           to the lights are needed."""
        potential_updates = [
            self.desired_light_state(square, channel)
            for channel, square in zip(
                self.lights.channels,
                self.board.values(),
            )
        ]
        self.lights.controller.update_channels(potential_updates)

