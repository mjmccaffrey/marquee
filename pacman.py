"""Marquee Lighted Sign Project - pac_man"""

from abc import ABC
from dataclasses import dataclass
from pprint import pprint
from typing import ClassVar

from bulb import HueBulb
from color import Color, Colors, RGB
from lightgame import (
    Board, Character, Entity, EntityGroup, LightGame, Maze, Square,
)
from hue import HueBridge
from lightcontroller import LightChannel, ChannelUpdate
from modes.playmode import PlayMode
from repl_misc import light_states


@dataclass(kw_only=True, repr=False)
class Dot(Entity):
    """"""
    brightness = 50
    color: RGB = Colors.WHITE
    draw_priority: int = 1


@dataclass(kw_only=True, repr=False)
class PacMan(Character):
    """"""
    color: ClassVar[Color] = RGB(252, 234, 63)
    draw_priority: ClassVar[int] = 3
    turn_priority: ClassVar[int] = 1

    def execute_turn(self):
        """Take turn."""

        def _move_to(coord: int) -> None:
            """"""
            dest = self.game.board[coord]
            if Dot in dest:
                dest[Dot].brightness -= 50
                print(f"BRIGHTNESS AT {coord} IS NOW {dest[Dot].brightness}")
                if dest[Dot].brightness <= 0:
                    del dest[Dot]
            self.game.move_entity(self, coord)

        # TEST
        keystrokes = {'l': 'left', 'r': 'right', 'u': 'up', 'd': 'down'}
        direction = input("move:").lower()
        match direction:
            case '.':
                dest = None
            case key if key in keystrokes:
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
    draw_priority: ClassVar[int] = 2
    turn_priority: ClassVar[int] = 2

    def execute_turn(self) -> None:
        """"""


@dataclass(kw_only=True, repr=False)
class Pinky(Ghost):
    """"""
    color: ClassVar[Color] = RGB(252, 234, 63)


@dataclass(kw_only=True, repr=False)
class Blinky(Ghost):
    """"""
    color: ClassVar[Color] = RGB(252, 234, 63)


class PacManGame(PlayMode):
    """"""

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

    def setup(self, level: int) -> None:
        """"""
        """Level 0 - basic maze."""
        """Level 1 - add Pinky."""
        """Level 2 - add Blinky."""
        """Level 3 - add bypass."""
        controller = self.player.lights.controller
        assert isinstance(controller, HueBridge)
        bulb = controller.bulb_model
        assert isinstance(bulb, HueBulb)
        RGB.adjust_incomplete_colors(bulb.gamut)
        self.game = LightGame(
            lights=self.player.lights,
            maze=self.maze_12,
            schedule=self.schedule,
            state_logic=self.state_logic,
            light_updates=self.light_updates,
        )
        self.pacman = self.game.create_entity(etype=PacMan, name="Pac-Man")
        self.game.place_entity(self.pacman, 7)
        self.pinky = self.game.create_entity(etype=Pinky, name="Pinky")
        self.blinky = self.game.create_entity(etype=Blinky, name="Blinky")
        for d in self.maze_12.keys() - {7}:
            dot = self.game.create_entity(etype=Dot, name=f"dot_{d}")
            self.game.place_entity(dot, d)

    def state_logic(self) -> None:
        """"""
        # If ghost and Pac-Man on same square, game is over etc.
        if any(
            ghost in self.game.board[self.pacman.coord]
            for ghost in (Pinky, Blinky)
        ):
            print("COLLISION")
    
    def desired_light_state(
            self, 
            entities: EntityGroup, 
            channel: LightChannel,
        ) -> ChannelUpdate:
        """"""
        # Nothing
        if not entities:
            return ChannelUpdate(channel=channel, on=False)
        if any(
            ghost in self.game.board[self.pacman.coord]
            for ghost in (Pinky, Blinky)
        ):
            # Pac-Man and Ghost
            brightness, color = Pinky.brightness, Colors.RED
        elif len(list(e for e in entities if isinstance(e, Ghost))) > 1:
            # 2 Ghosts
            brightness, color = Pinky.brightness, Colors.BLUE
        else:
            # Other
            s: list[type[Entity]] = sorted(
                entities, key=lambda e: e.draw_priority, reverse=True,
            )
            for e in s:
                print(e.brightness, e.color)
            brightness, color = s[0].brightness, s[0].color
        return ChannelUpdate(
            channel=channel,
            brightness=brightness,
            trans=0,
            color=color,
            on=True,
        )

    def light_updates(self, delta: Board) -> list[ChannelUpdate]:
        """"""
        result = [
            self.desired_light_state(
                entities=e, channel=self.player.lights.channels[i],
            )
            for i, e in delta.items()
        ]
        # print("LIGHT UPDATES:")
        # pprint(result)
        return result

    def execute(self) -> None:
        """"""
        self.setup(level=0)
        self.game.start()

