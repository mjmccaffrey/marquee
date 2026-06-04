"""Marquee Lighted Sign Project - pac_man entities"""

from abc import ABC
from dataclasses import dataclass
from enum import auto, StrEnum
import logging
from typing import ClassVar
from typing_extensions import override

from devices.color import Color, Colors, RGB
from ..gamemode import Character, Entity, GameMode, Maze, Square

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True, repr=False, eq=True)
class Dot(Entity):
    game: GameMode
    color: ClassVar[Color] = RGB(255, 176, 124)
    brightness: int = 50
    draw_priority: int = 1

    def bitten(self):
        """Change state accordingly of bitten dot."""
        self.brightness -= 40

    @property
    def consumed(self):
        """Has the dot been completely eaten?"""
        return self.brightness <= 0


@dataclass(kw_only=True, repr=False, eq=True)
class Fruit(Entity):
    game: GameMode
    color: RGB = Colors.ORANGE
    brightness: int = 80
    draw_priority: int = 2


@dataclass(kw_only=True, repr=False)
class PacMan(Character):
    game: GameMode
    bite_event: str
    name: str = "PacMan"
    color: ClassVar[Color] = RGB(252, 234, 63)
    brightness: int = 80
    draw_priority: ClassVar[int] = 4
    turn_priority: ClassVar[int] = 1

    def next_coord(self):
        """Next square, based on joystick and maze."""
        dir = self.game.joystick.direction
        if dir is None:
            return
        assert self.coord is not None
        return getattr(self.game.maze[self.coord], dir, None)

    @override
    def execute(self):
        """Take turn."""
        coord = self.next_coord()
        if coord is not None:
            self.game.move_character(self, coord)
            edible = {e for e in self.game.board[coord] if e in {Dot, Fruit}}
            for e in edible:
                self.game.events.notify(self.bite_event, etype=e, coord=coord)


class Sound(StrEnum):
    BEGINNING = auto()
    CHOMP = auto()
    DEATH = auto()
    EATFRUIT = auto()
    EATGHOST = auto()
    EXTRAPAC = auto()
    INTERMISSION = auto()
    

class GhostState(StrEnum):
    WAITING = auto()
    EMERGING = auto()
    CHASING = auto()

@dataclass(kw_only=True, repr=False)
class Ghost(Character, ABC):
    brightness: int = 80
    draw_priority: ClassVar[int] = 3
    turn_priority: ClassVar[int] = 2
    wait_ticks: int
    direction: int

    def __post_init__(self):
        """Initialize states."""
        self.state = GhostState.WAITING

    def waiting(self) -> None:
        """Waiting to enter emerge."""
        if self.game.tick + 1 == self.wait_ticks:
            self.state = GhostState.EMERGING

    def emerging(self) -> None:
        """Entering maze as soon as able."""
        assert self.coord is None
        if not any(
            issubclass(e, Character)
            for e in self.game.board[1]
        ):
            self.game.place_entity(self, 1)
            self.state = GhostState.CHASING

    def chasing(self) -> None:
        """In maze and chasing PacMan."""
        assert self.coord is not None
        coord = (self.coord + self.direction) % len(maze_base)
        self.game.move_character(self, coord)

    @override
    def execute(self) -> None:
        """Take turn."""
        match self.state:
            case GhostState.WAITING:
                self.waiting()
            case GhostState.EMERGING:
                self.emerging()
            case GhostState.CHASING:
                self.chasing()


@dataclass(kw_only=True, repr=False)
class Blinky(Ghost):
    name: str = "Blinky"
    color: ClassVar[Color] = Colors.RED


@dataclass(kw_only=True, repr=False)
class Pinky(Ghost):
    name: str = "Pinky"
    color: ClassVar[Color] = Colors.MAGENTA


@dataclass(kw_only=True, repr=False)
class Inky(Ghost):
    name: str = "Inky"
    color: ClassVar[Color] = Colors.TEAL


@dataclass(kw_only=True, repr=False)
class Clyde(Ghost):
    name: str = "Clyde"
    color: ClassVar[Color] = Colors.ORANGE


maze_base: Maze = {
    0: Square(
        right=1, upright=1, downright=1,
        left=11, down=11, downleft=11,
        up=None, upleft=None,
    ),
    1: Square(
        left=0, downleft=0, upleft=0,
        right=2, downright=2, upright=2,
        up=None, down=None,
    ),
    2: Square(
        left=1, upleft=1, downleft=1,
        right=3, down=3, downright=3,
        up=None, upright=None,
    ),
    3: Square(
        down=4, downright=4, upright=4,
        left=2, up=2, upleft=2,
        right=None, downleft=None,
    ),       
    4: Square(
        up=3, upleft=3, upright=3,
        down=5, downleft=5, downright=5,
        left=None, right=None,
    ),
    5: Square(
        up=4, upleft=4, upright=4,
        left=6, down=6, downleft=6,
        right=None, downright=None,
    ),
    6: Square(
        left=7, downleft=7, upleft=7,
        up=5, right=5, upright=5,
        down=None, downright=5,
    ),
    7: Square(
        left=8, upleft=8, downleft=8,
        right=6, upright=6, downright=6,
        up=None, down=None,
    ),
    8: Square(
        right=7, downright=7, upright=7,
        up=9, left=9, upleft=9, 
        down=None, downleft=None,
    ),
    9: Square(
        up=10, upright=10, upleft=10,
        right=8, down=8, downright=8,
        left=None, downleft=None,
    ),
    10: Square(
        down=9, downleft=9, downright=9,
        up=11, upleft=11, upright=11,
        left=None, right=None,
    ),
    11: Square(
        down=10, downleft=10, downright=10,
        right=0, up=0, upright=0,
        left=None, upleft=None,
    ),
}
maze_with_passage: Maze = maze_base | {
    4: Square(
        up=3, upleft=3, upright=3,
        down=5, downleft=5, downright=5,
        left=14,
        right=None,
    ),
    10: Square(
        down=9, downleft=9, downright=9,
        up=11, upleft=11, upright=11,
        right=12,
        left=None,
    ),
    12: Square(
        left=10, upleft=10, downleft=10,
        right=13, upright=13, downright=13,
        up=None, down=None,
    ),
    13: Square(
        left=12, upleft=12, downleft=12,
        right=14, upright=14, downright=14,
        up=None, down=None,
    ),
    14: Square(
        left=13, upleft=13, downleft=13,
        right=4, upright=4, downright=4,
        up=None, down=None,
    ),
}

