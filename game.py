"""Marquee Lighted Sign Project - game"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field

from color import RGB
from lightset import LightSet


@dataclass(kw_only=True)
class Entity(ABC):
    """Entities are always displayed."""
    color: RGB
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
    lights: LightSet
    schedule: Callable[[Callable, float, str], None]
    board: dict[int, Location]

    characters: list[Character] = field(init=False, default_factory=list)

    def execute(self):
        """Play the game."""
        for character in self.characters:
            character.execute()
        self.schedule(self.execute, 1.0, 'Game tick')

    def create(self, entity_type: type[Entity], coordinate: int):
        """"""
        entity = entity_type(game=self, coordinate=coordinate)  # type: ignore
        if isinstance(entity, Character):
            self.characters.append(entity)
        self._place(entity=entity)

    def move(self, entity: Entity, coordinate: int):
        """Move entity to coordinate."""
        self.board[entity.coordinate].entity = None
        entity.coordinate = coordinate
        self._place(entity=entity)

    def _place(self, entity: Entity) -> None:
        """Place entity on board at its coordinate, and display."""
        self.board[entity.coordinate].entity = entity
        self.lights.set_channels(
            brightness=100,
            color=entity.color,
            channel_indexes=[entity.coordinate],
        )

    def remove(self, entity: Entity):
        """Remove and destroy entity at coordinate."""
        self.board[entity.coordinate].entity = None
        del entity

