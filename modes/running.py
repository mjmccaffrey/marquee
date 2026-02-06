"""Marquee Lighted Sign Project - running mode"""

from dataclasses import dataclass, field

from color import Colors, RGB
from devices.lightcontroller import LightChannel, ChannelUpdate
from .gamemode import Character, EntityGroup, GameMode, Maze
from .pacman_assets import maze_12


class Dot(Character):
    """"""
    brightness = 100
    draw_priority = 1
    turn_priority = 1
    direction: int
    speed: int

    def execute_turn(self) -> None:
        """Take turn."""
        assert self.coord is not None
        if self.game.tick and (self.game.tick % self.speed) == 0:
            self.game.move_entity(self, self.coord + self.direction)


class OneTwo(Dot):
    """Grouped dots."""
    color = Colors.YELLOW
    direction = +1
    speed = 5

class One(OneTwo):
    """Grouped dots."""

class Two(OneTwo):
    """Grouped dots."""

class Three(Dot):
    """Solitary dot."""
    color = Colors.BLUE
    direction = -1
    speed = 1


@dataclass(kw_only=True)
class Running(GameMode):
    """"""
    maze: Maze = field(default_factory=lambda: maze_12)

    def __post_init__(self):
        """Initialize board and characters."""
        super().__post_init__()
        assert self.lights.gamut is not None  # Color lights
        RGB.adjust_incomplete_colors(self.lights.gamut)
        self.one = self.create_entity(etype=One, name="one")
        self.two = self.create_entity(etype=Two, name="two")
        self.three = self.create_entity(etype=Three, name="three")
        self.place_entity(self.one, 0)
        self.place_entity(self.two, 1)
        self.place_entity(self.three, 6)

    def state_logic(self) -> None:
        """No state logic required."""
        pass
    
    def desired_light_state(
            self, 
            entities: EntityGroup, 
            channel: LightChannel,
        ) -> ChannelUpdate:
        """Return desired light state given entities on square."""
        if not entities:
            return ChannelUpdate(channel=channel, on=False)
        elif len(entities) == 1:
            brightness, color = 100, list(entities.values())[0].color
        else:   
            brightness, color = 100, Colors.GREEN
        return ChannelUpdate(
            channel=channel,
            brightness=brightness,
            trans=0.1,
            color=color,
            on=True,
        )

