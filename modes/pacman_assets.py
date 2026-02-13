"""Marquee Lighted Sign Project - pac_man entities"""

from abc import ABC
from typing import ClassVar
from dataclasses import dataclass

from color import Color, Colors, RGB
from .gamemode import Character, Entity, GameMode, Maze, Square
# from debug import light_states


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
    dot_pieces_maximum: int = 22
    dot_pieces_remaining: int = dot_pieces_maximum

    def execute_turn(self):
        """Take turn."""

        # TEST
        keystrokes = {'l': 'left', 'r': 'right', 'u': 'up', 'd': 'down'}
        direction = input(f"move {self.game.tick}:").lower()
        match direction:
            case '.':
                coord = None
            case key if key in keystrokes:
                assert self.coord is not None
                coord = getattr(
                    self.game.maze[self.coord],
                    keystrokes[key],
                )
            case 'c':
                assert self.coord is not None
                coord = (self.coord + 1) % 12
            case _:
                coord = None
                # light_states(self.game.lights)
        if coord is not None:
            self.game.move_character(self, coord)
            if Dot in self.game.board[coord]:
                self.eat_dot_piece(coord)

    def eat_dot_piece(self, coord: int) -> None:
        """"""
        self.dot_pieces_remaining -= 1
        b = int(
                (self.dot_pieces_maximum  - 
                 self.dot_pieces_remaining) * 
                100 / self.dot_pieces_maximum
        )
        self.game.top.set_channels(
            brightness=b,
        )
        dot = self.game.board[coord][Dot]
        dot.brightness -= 65
        if dot.brightness <= 0:
            del self.game.board[coord][Dot]

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
        if self.game.tick == self.wait_ticks:
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

    def execute_turn(self) -> None:
        """"""
        self.state()


@dataclass(kw_only=True, repr=False)
class Blinky(Ghost):
    """"""
    name: str = "Blinky"
    color: ClassVar[Color] = Colors.RED
    direction: int = -1


@dataclass(kw_only=True, repr=False)
class Pinky(Ghost):
    """"""
    name: str = "Pinky"
    color: ClassVar[Color] = Colors.MAGENTA
    direction: int = +1


maze_base: Maze = {
    0: Square(left=11, right=1, down=11),
    1: Square(left=0, right=2),
    2: Square(left=1, right=3, down=3),
    3: Square(left=2, up=2, down=4),       
    5: Square(left=6, up=4, down=6),
    6: Square(left=7, right=5, up=5),
    7: Square(left=8, right=6),
    8: Square(left=9, right=7, up=9),
    9: Square(right=8, up=10, down=8),
    11: Square(right=0, up=0, down=10),
}
maze_12: Maze = maze_base | {
    4: Square(up=3, down=5),
    10: Square(up=11, down=9),
}
maze_15: Maze = maze_base | {
    4: Square(left=14, up=3, down=5),
    10: Square(right=12, up=11, down=9),
    12: Square(left=10, right=11),
    13: Square(left=12, right=14),
    14: Square(left=13, right=4),
}

