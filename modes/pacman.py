"""Marquee Lighted Sign Project - pacman mode"""

from color import Colors, RGB
from .gamemode import (
    Entity, EntityGroup, GameMode,
)
from .pacman_assets import Dot, Ghost, PacMan, Pinky, Blinky, maze_12
from lightcontroller import LightChannel, ChannelUpdate


class PacManGame(GameMode):
    """"""
    """Level 0 - basic maze."""
    """Level 1 - add Pinky."""
    """Level 2 - add Blinky."""
    """Level 3 - add bypass."""

    def __post_init__(self):
        """Initialize board and characters."""
        super().__post_init__()
        assert self.lights.gamut is not None  # Color lights
        RGB.adjust_incomplete_colors(self.lights.gamut)
        self.pacman = self.create_entity(etype=PacMan, name="pacman")
        self.place_entity(self.pacman, 7)
        self.pinky = self.create_entity(etype=Pinky, name="pinky")
        self.blinky = self.create_entity(etype=Blinky, name="blinky")
        for d in maze_12.keys() - {7}:
            dot = self.create_entity(etype=Dot, name=f"dot_{d}")
            self.place_entity(dot, d)

    def state_logic(self) -> None:
        """"""
        # If ghost and Pac-Man on same square, game is over etc.
        assert self.pacman.coord is not None
        if any(
            ghost in self.board[self.pacman.coord]
            for ghost in (Pinky, Blinky)
        ):
            print("COLLISION")
    
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

