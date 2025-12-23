"""Marquee Lighted Sign Project - pac_man entities"""

from abc import ABC
from typing import ClassVar
from dataclasses import dataclass

from color import Color, Colors, RGB
from lightgame import Character, Entity
from repl_misc import light_states


@dataclass(kw_only=True, repr=False)
class Dot(Entity):
    """"""
    color: RGB = Colors.WHITE
    brightness: int = 80
    draw_priority: int = 1


@dataclass(kw_only=True, repr=False)
class PacMan(Character):
    """"""
    color: ClassVar[Color] = RGB(252, 234, 63)
    brightness: int = 80
    draw_priority: ClassVar[int] = 3
    turn_priority: ClassVar[int] = 1

    def execute_turn(self):
        """Take turn."""

        def _move_to(coord: int) -> None:
            """"""
            dest = self.game.board[coord]
            if Dot in dest:
                dest[Dot].brightness -= 65
                # print(f"BRIGHTNESS AT {coord} IS NOW {dest[Dot].brightness}")
                if dest[Dot].brightness <= 0:
                    del dest[Dot]
            self.game.move_entity(self, coord)

        # TEST
        keystrokes = {'l': 'left', 'r': 'right', 'u': 'up', 'd': 'down'}
        direction = input(f"move {self.game.tick}:").lower()
        match direction:
            case '.':
                dest = None
            case key if key in keystrokes:
                assert self.coord is not None
                dest = getattr(
                    self.game.maze[self.coord],
                    keystrokes[key],
                )
            case _:
                dest = None
                light_states(self.game.lights)
        if dest is not None:
            _move_to(dest)


@dataclass(kw_only=True, repr=False)
class Ghost(Character, ABC):
    """"""
    brightness: int = 80
    draw_priority: ClassVar[int] = 2
    turn_priority: ClassVar[int] = 2
    sleep_ticks: int
    direction: int

    def execute_turn(self) -> None:
        """"""
        if self.game.tick < self.sleep_ticks:
            return
        if self.coord is None:
            if not any(
                issubclass(e, Character)
                for e in self.game.board[1]
            ):
                self.game.place_entity(self, 1)
        else:
            pacman = self.game.characters_by_name['pacman']
            if pacman.coord == self.coord 
            self.game.move_entity(self, self.coord + self.direction)


@dataclass(kw_only=True, repr=False)
class Pinky(Ghost):
    """"""
    color: ClassVar[Color] = Colors.MAGENTA
    sleep_ticks: int = 10
    direction: int = +1


@dataclass(kw_only=True, repr=False)
class Blinky(Ghost):
    """"""
    color: ClassVar[Color] = Colors.GREEN
    sleep_ticks: int = 15
    direction: int = -1

