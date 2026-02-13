"""Marquee Lighted Sign Project - pacman mode"""

from dataclasses import dataclass, field

from color import Colors, RGB
from .gamemode import Entity, EntityGroup, GameMode, Maze
from .pacman_assets import Dot, Ghost, PacMan, Pinky, Blinky, maze_12
from devices.lightcontroller import LightChannel, ChannelUpdate


@dataclass(kw_only=True)
class PacManGame(GameMode):
    """"""
    # """Level 0 - basic maze."""
    """Level 0 - Blinky."""
    """Level 2 - Blinky and Pinky."""
    # """Level 3 - add bypass."""
    maze: Maze = field(default_factory=lambda: maze_12)
    ticks_per_second: int = 2

    def __post_init__(self):
        """Initialize board and characters."""
        super().__post_init__()
        assert self.lights.gamut is not None  # Lights are color.
        RGB.adjust_incomplete_colors(self.lights.gamut)
        self.PRE_GAME = self.pre_game
        self.WON_GAME = self.won_game
        self.LOST_GAME = self.lost_game

    def execute(self) -> None:
        """"""
        self.state = self.PRE_GAME
        self.start()

    def pre_game(self) -> None:
        """Set up dots and characters."""
        self.play_level(0)
    
    def play_level(self, level: int) -> None:
        """"""
        print("Playing level ", level)
        self.level = level
        self.init_level()
        self.top.set_channels(brightness=0, on=True)
        for d in maze_12.keys() - {7}:
            dot = self.register_entity(Dot(game=self, name=f"dot_{d}"))
            self.place_entity(dot, d)
        self.pacman = self.register_entity(PacMan(game=self))
        self.pinky = self.register_entity(
            Pinky(game=self, wait_ticks=10 if self.level == 0 else 5)
        )
        self.blinky = self.register_entity(
            Blinky(game=self, wait_ticks=999999 if self.level == 0 else 10))
        self.place_entity(self.pacman, 7)
        self.update_lights(self.board)
        self.state = self.PLAY_GAME

    def won_game(self) -> None:
        """"""
        print("You won!")
        self.event_queue.delete_owned_by(self)

    def lost_game(self) -> None:
        """"""
        print("You lost!")
        self.event_queue.delete_owned_by(self)

    def state_logic(self) -> None:
        """"""
        # If ghost and Pac-Man on same square, or 
        # attempted to pass each other, game is over etc.
        assert self.pacman.coord is not None
        if not self.pacman.dot_pieces_remaining:
            if self.level == 0:
                self.play_level(1)
            else:
                self.state = self.WON_GAME
        if self.ghost_got_pacman():
            assert self.pacman.prior_coord is not None
            self.move_character(self.pacman, self.pacman.prior_coord)
            self.state = self.LOST_GAME
        print(self.pacman.coord, self.blinky.coord, self.pinky.coord)

    def ghost_got_pacman(self):
        """"""
        return any(
            self.pacman.coord == ghost.coord
                        or
            self.pacman.prior_coord == ghost.coord and
            self.pacman.coord == ghost.prior_coord
            for ghost in (self.pinky, self.blinky)
        )

    def desired_light_state(
            self, 
            entities: EntityGroup, 
            channel: LightChannel,
        ) -> ChannelUpdate:
        """"""
        # Empty square
        if not entities:
            return ChannelUpdate(channel=channel, on=False)
        assert self.pacman.coord is not None
        # Pac-Man and Ghost
        if PacMan in entities and any(
            ghost in entities
            for ghost in (Pinky, Blinky)
        ):
            brightness, color = Pinky.brightness, Colors.RED
        # 2 Ghosts
        elif len(list(e for e in entities if isinstance(e, Ghost))) > 1:
            brightness, color = Pinky.brightness, Colors.BLUE
        # Other
        else:
            s: list[Entity] = sorted(
                entities.values(), key=lambda e: e.draw_priority,
            )
            brightness, color = s[-1].brightness, s[-1].color
        return ChannelUpdate(
            channel=channel,
            brightness=brightness,
            trans=0,
            color=color,
            on=True,
        )

