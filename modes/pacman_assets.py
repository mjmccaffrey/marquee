"""Marquee Lighted Sign Project - pac_man entities"""

from abc import ABC
from dataclasses import dataclass
import logging
from typing import ClassVar

from devices.color import Color, Colors, RGB
from .gamemode import Character, Entity, GameMode, Maze, Square

log = logging.getLogger('marquee.' + __name__)

BITE_EVENT = "BITE_EVENT"

@dataclass(kw_only=True, repr=False, eq=True, )
class Dot(Entity):
    """"""
    game: GameMode
    color: RGB = Colors.GREEN
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

    def execute(self):
        """Take turn."""
        dir = self.game.joystick.direction
        if dir is None:
            return
        print(dir)
        assert self.coord is not None
        coord = getattr(self.game.maze[self.coord], dir, None)
        if coord is None:
            return
        self.game.move_character(self, coord)
        if Dot in self.game.board[coord]:
            self.bite_dot(coord)

    def bite_dot(self, coord: int) -> None:
        """"""
        self.game.events.notify(BITE_EVENT, etype=Dot, coord=coord)


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
        self.WAITING = self.waiting
        self.EMERGING = self.emerging
        self.CHASING = self.chasing
        self.state = self.WAITING

    def waiting(self) -> None:
        """"""
        if self.game.tick + 1 == self.wait_ticks:
            self.state = self.EMERGING

    def emerging(self) -> None:
        """"""
        assert self.coord is None
        if not any(
            issubclass(e, Character)
            for e in self.game.board[1]
        ):
            self.game.place_entity(self, 1)
            self.state = self.CHASING

    def chasing(self) -> None:
        """"""
        assert self.coord is not None
        self.game.move_character(self, self.coord + self.direction)

    def execute(self) -> None:
        """"""
        self.state()


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
    0: Square(right=1, left=11, down=11, downleft=11),
    1: Square(left=0, right=2),
    2: Square(left=1, down=3, downright=3, right=3),
    3: Square(down=4, left=2, up=2, upleft=2),       
    5: Square(up=4, left=6, down=6, downleft=6),
    6: Square(left=7, right=5, up=5, upright=5),
    7: Square(left=8, right=6),
    8: Square(right=7, left=9, up=9, upleft=9),
    9: Square(up=10, right=8, down=8, downright=8),
    11: Square(down=10, right=0, up=0, upright=0),
}
maze_12: Maze = maze_base | {
    4: Square(right=10, up=3, down=5),
    10: Square(left=4, up=11, down=9),
}
# maze_15: Maze = maze_base | {
#     4: Square(left=14, up=3, down=5),
#     10: Square(right=12, up=11, down=9),
#     12: Square(left=10, right=11),
#     13: Square(left=12, right=14),
#     14: Square(left=13, right=4),
# }

