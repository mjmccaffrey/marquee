"""Marquee Lighted Sign Project - game"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field

from color import Color, Colors, RGB, XY
from lightset import LightSet
import rgbxy


@dataclass(kw_only=True)
class Entity(ABC):
    """Entities are always displayed."""
    color: Color
    game: 'Game'
    coordinate: int


@dataclass(kw_only=True)
class Character(Entity, ABC):
    """Entity that moves."""

    @abstractmethod
    def execute(self) -> None:
        """Take turn."""


@dataclass(kw_only=True)
class Location:
    left: int | None = None
    right: int | None = None
    up: int | None = None
    down: int | None = None
    entity: Entity | None = None


@dataclass(kw_only=True)
class Game:
    """"""
    converter: rgbxy.Converter
    lights: LightSet
    schedule: Callable[[Callable, float, str], None]
    board: dict[int, Location]

    characters: list[Character] = field(init=False, default_factory=list)

    def execute(self):
        """Play the game."""
        for character in self.characters:
            character.execute()

    def create(self, entity_type: type[Entity], coordinate: int):
        """Create entity. Convert color. Place on board."""
        entity = entity_type(game=self, coordinate=coordinate)  # type: ignore
        if isinstance(c := entity.color, RGB):
            entity.color = XY(*self.converter.rgb_to_xy(c.red, c.green, c.blue))
        if isinstance(entity, Character):
            self.characters.append(entity)
        self._place(entity=entity)

    def move(self, entity: Entity, coordinate: int):
        """Move entity to coordinate."""

        old = entity.coordinate
        self.lights.set_channels(
            color=XY(0.0, 0.0),
            brightness=0,
            channel_indexes=[old],
        )

        self.board[entity.coordinate].entity = None
        entity.coordinate = coordinate
        self._place(entity=entity)

    def _place(self, entity: Entity) -> None:
        """Place entity on board at its coordinate, and display."""
        self.board[entity.coordinate].entity = entity
        self.lights.set_channels(
            brightness=100,
            color=entity.color,
            on=True,
            channel_indexes=[entity.coordinate],
        )

    def remove(self, entity: Entity):
        """Remove and destroy entity at coordinate."""
        self.board[entity.coordinate].entity = None
        del entity

