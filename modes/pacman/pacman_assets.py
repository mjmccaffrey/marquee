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

BITE_EVENT = "BITE_EVENT"

@dataclass(kw_only=True, repr=False, eq=True)
class Dot(Entity):
    """"""
    game: GameMode
    color: ClassVar[Color] = RGB(255, 176, 124)
    brightness: int = 80
    draw_priority: int = 1


@dataclass(kw_only=True, repr=False, eq=True)
class Fruit(Entity):
    """"""
    game: GameMode
    color: RGB = Colors.ORANGE
    brightness: int = 80
    draw_priority: int = 1


@dataclass(kw_only=True, repr=False)
class PacMan(Character):
    """"""
    game: GameMode
    name: str = "PacMan"
    color: ClassVar[Color] = RGB(252, 234, 63)
    brightness: int = 80
    draw_priority: ClassVar[int] = 3
    turn_priority: ClassVar[int] = 1

    @override
    def execute(self):
        """Take turn."""
        dir = self.game.joystick.direction
        if dir is None:
            return
        # log.info(f'{dir=}')
        assert self.coord is not None
        coord = getattr(self.game.maze[self.coord], dir, None)
        if coord is None:
            return
        self.game.move_character(self, coord)
        edible = {e for e in self.game.board[coord] if e in {Dot, Fruit}}
        for e in edible:
            self.game.events.notify(BITE_EVENT, etype=e, coord=coord)


class Sound(StrEnum):
    BEGINNING = auto()
    CHOMP = auto()
    DEATH = auto()
    EATFRUIT = auto()
    EATGHOST = auto()
    EXTRAPAC = auto()
    INTERMISSION = auto()
    

class GhostState(StrEnum):
    """"""
    WAITING = auto()
    EMERGING = auto()
    CHASING = auto()

@dataclass(kw_only=True, repr=False)
class Ghost(Character, ABC):
    """"""
    brightness: int = 80
    draw_priority: ClassVar[int] = 2
    turn_priority: ClassVar[int] = 2
    wait_ticks: int
    direction: int

    def __post_init__(self):
        """Initialize states."""
        self.state = GhostState.WAITING

    def waiting(self) -> None:
        """"""
        if self.game.tick + 1 == self.wait_ticks:
            self.state = GhostState.EMERGING

    def emerging(self) -> None:
        """"""
        assert self.coord is None
        if not any(
            issubclass(e, Character)
            for e in self.game.board[1]
        ):
            self.game.place_entity(self, 1)
            self.state = GhostState.CHASING

    def chasing(self) -> None:
        """"""
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
    """"""
    name: str = "Blinky"
    color: ClassVar[Color] = Colors.RED


@dataclass(kw_only=True, repr=False)
class Pinky(Ghost):
    """"""
    name: str = "Pinky"
    color: ClassVar[Color] = Colors.MAGENTA


@dataclass(kw_only=True, repr=False)
class Inky(Ghost):
    """"""
    name: str = "Inky"
    color: ClassVar[Color] = Colors.TEAL


@dataclass(kw_only=True, repr=False)
class Clyde(Ghost):
    """"""
    name: str = "Clyde"
    color: ClassVar[Color] = Colors.ORANGE


maze_base: Maze = {
    0: Square(right=1, down=11),
    1: Square(left=0, right=2),
    2: Square(left=1, down=3),
    3: Square(down=4, left=2),       
    4: Square(up=3, down=5),
    5: Square(up=4, left=6),
    6: Square(left=7, up=5),
    7: Square(left=8, right=6),
    8: Square(right=7, up=9),
    9: Square(up=10, right=8),
    10: Square(down=9, up=11),
    11: Square(down=10, right=0),
}
maze_passage: Maze = maze_base | {
    4: Square(left=14, up=3, down=5),
    10: Square(right=12, down=9, up=11),
    12: Square(left=10, right=13),
    13: Square(left=12, right=14),
    14: Square(left=13, right=4),
}

