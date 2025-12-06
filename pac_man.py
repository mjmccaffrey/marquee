"""Marquee Lighted Sign Project - pac_man"""

from color import Colors, RGB
from dataclasses import dataclass

from game import Character, Entity, Game, Location
from hue import HueBridge
from modes.playmode import PlayMode

@dataclass(kw_only=True)
class Dot(Entity):
    """"""
    color: RGB = Colors.WHITE


@dataclass(kw_only=True)
class PacMan(Character):
    """"""
    color: RGB = Colors.YELLOW

    def execute(self, current_location: Location):
        """Take turn."""

        print("PAC-MAN EXECUTE")
        # TEST: NO MOMENTUM
        keystrokes = {'l': 'left', 'r': 'right', 'u': 'up', 'd': 'down'}
        direction = input("move:").lower()
        match direction:
            case '.':
                dest = None
            case key if key in keystrokes:
                dest = getattr(
                    current_location,
                    keystrokes[key],
                )
            case _:
                raise ValueError(direction)
        if dest is not None:
            self._move(dest)
        self.game.schedule(self.game.execute, 1.0, 'Game tick')

    def _move(self, destination: int) -> None:
        """"""
        in_the_way = self.game.board[destination].entity
        match in_the_way:
            case None:
                pass
            case Dot():
                self.game.remove(in_the_way)
            case _:
                raise ValueError()
        self.game.move(self, destination)
            

"""Level 1 - basic maze."""
"""Level 2 - add Pinky."""
"""Level 3 - add Blinky."""
"""Level 4 - add bypass."""

class PacManGame(PlayMode):
    """"""

    def setup(self) -> None:
        """"""
        board_12 = {
            0: Location(right=1, down=11),
            1: Location(left=0, right=2),
            2: Location(left=1, down=3),
            3: Location(left=2, right=4, down=4),
            4: Location(up=3, down=5),
            5: Location(up=4, left=6),
            6: Location(left=7, right=5, up=5),
            7: Location(left=8, right=6),
            8: Location(left=9, right=7, up=9),
            9: Location(right=8, up=10, down=8),
            10: Location(up=11, down=9),
            11: Location(right=0, up=0, down=10),
        }
        controller = self.player.lights.controller
        assert isinstance(controller, HueBridge)
        game = Game(
            converter=controller.converter,
            lights=self.player.lights,
            schedule=self.schedule,
            board=board_12,
        )
        game.create(entity_type=PacMan, coordinate=7)
        for l in board_12.keys() - {7}:
            game.create(entity_type=Dot, coordinate=l)

    def execute(self) -> None:
        """"""
        self.setup()
        self.execute()        

