"""Marquee Lighted Sign Project - pacman mode"""

from dataclasses import dataclass, field
from functools import partial
from itertools import cycle
import logging
from typing import Any

from devices.color import Colors, RGB
from devices.devices_misc import ButtonInterface
from .gamemode import Entity, EntityGroup, GameMode, Maze
from .pacman_assets import (
    Dot, BITE_EVENT, Ghost, PacMan, Pinky, Blinky, maze_12
)
from devices.lightcontroller import LightChannel, ChannelUpdate

log = logging.getLogger('marquee.' + __name__)

PACMAN_START = 7

@dataclass(kw_only=True)
class PacManGame(GameMode):
    """"""
    # """Level 0 - basic maze."""
    """Level 0 - Blinky."""
    """Level 2 - Blinky and Pinky."""
    # """Level 3 - add bypass."""
    maze: Maze = field(default_factory=lambda: maze_12)
    ticks_per_second: float = 2.0

    def __post_init__(self):
        """Initialize board and characters."""
        super().__post_init__()
        assert self.lights.gamut is not None  # Lights are color.
        RGB.adjust_incomplete_colors(self.lights.gamut)
        self.buttons.game_start.set_light(True)
        self.dot_bites_maximum = (self.lights.count - 1) * 2
        self.events.subscribe(BITE_EVENT, self.pacman_bite)
        self.game_start_pressed = False
        self.PRE_GAME_STATE = self.pre_game_state
        self.PRE_LEVEL_1_STATE = self.pre_level_1_state
        self.PRE_LEVEL_1_STATE = self.pre_level_1_state
        self.POST_LEVEL_1_STATE = self.post_level_1_state
        self.GAME_WON_STATE = self.game_won_state
        self.GAME_LOST_STATE = self.game_lost_state
        self.state = self.PRE_GAME_STATE

    def button_action(self, button: ButtonInterface) -> int | None:
        """If direction button pushed, change displayed color set.
           Otherwise, call parent's button handler."""
        if button == self.buttons.game_start:
            self.game_start_pressed = True
        else:
            return super().button_action(button)
        
    def interrupt_action(self, args: tuple[Any, ...]) -> None:
        """"""
    
    def pacman_bite(self, etype: type, coord: int):
        """Track remaining. Brighten top bulb."""
        dot = self.board[coord][etype]
        dot.brightness -= 50
        if dot.brightness <= 0:
            del self.board[coord][Dot]
        self.dot_bites_remaining -= 1
        self.top.set_channels(
            brightness=int(
                (self.dot_bites_maximum  - 
                 self.dot_bites_remaining) * 
                100 / self.dot_bites_maximum
            )
        )

    def play_level(self, level: int) -> None:
        """"""
        log.info(f"Playing level {level}")
        self.dot_bites_remaining = self.dot_bites_maximum
        self.level = level
        self.init_level()
        self.top.set_channels(brightness=0, on=True)
        self.top.set_relays(True)
        for d in maze_12.keys() - {PACMAN_START}:
            dot = self.register_entity(Dot(game=self, name=f"dot_{d}"))
            self.place_entity(dot, d)
        self.pacman = self.register_entity(PacMan(game=self))
        self.blinky = self.register_entity(
            Blinky(
                game=self, 
                direction=+1,
                wait_ticks=20 if self.level == 0 else 10,
            )
        )
        self.pinky = self.register_entity(
            Pinky(
                game=self, 
                direction=-1,
                wait_ticks=999999 if self.level == 0 else 20,
            )
        )
        self.ghosts = (self.pinky, self.blinky)
        self.place_entity(self.pacman, PACMAN_START)
        self.update_lights(self.board)
        self.change_state(self.PLAY_GAME_STATE)

    def pre_game_state(self) -> None:
        """"""
        if self.game_start_pressed:
            self.game_start_pressed = False
            self.change_state(self.PRE_LEVEL_1_STATE)
        else:
            self.schedule(due=0.1, action=self.pre_game_state)

    def pre_level_1_state(self) -> None:
        """Set up dots and characters."""
        self.play_level(0)

    def post_level_1_state(self) -> None:
        """"""
        for i, c in zip(range(4), cycle((Colors.WHITE, Colors.BLUE))):
            kwargs = dict(color=c, transition=0)
            if i == 0:
                kwargs |= dict(on=True)
            self.schedule(
                due=(1 + i),
                action=partial(self.lights.set_channels, **kwargs),
            )
        self.schedule(due=6.0, action=partial(self.change_state, self.pre_level_1_state))

    def game_won_state(self) -> None:
        """"""
        log.info("You won!")

    def game_lost_state(self) -> None:
        """"""
        log.info("You lost!")

    def state_logic(self) -> None:
        """"""
        # If ghost and Pac-Man on same square, or 
        # attempted to pass each other, game is over etc.
        assert self.pacman.coord is not None
        if not self.dot_bites_remaining:
            if self.level == 0:
                self.change_state(self.POST_LEVEL_1_STATE)
            else:
                self.change_state(self.GAME_WON_STATE)
        if self.ghost_got_pacman():
            self.change_state(self.GAME_LOST_STATE)

    def ghost_got_pacman(self) -> bool:
        """"""
        for ghost in self.ghosts:
            if self.pacman.coord == ghost.coord:
                return True
            if (
                self.pacman.prior_coord == ghost.coord and
                self.pacman.coord == ghost.prior_coord
            ):
                assert self.pacman.prior_coord is not None
                self.move_character(self.pacman, self.pacman.prior_coord)
                return True
        return False

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
        if (
            PacMan in entities and 
            any(type(ghost) in entities for ghost in self.ghosts)
        ):
            brightness, color = Ghost.brightness, Colors.BLUE
        # 2 Ghosts
        elif len(list(e for e in entities if isinstance(e, Ghost))) > 1:
            brightness, color = Pinky.brightness, Colors.BLUE
        # Other
        else:
            s: list[Entity] = sorted(
                entities.values(), key=lambda e: e.draw_priority,
            )
            brightness, color = s[-1].brightness, s[-1].color
        #
        return ChannelUpdate(
            channel=channel,
            brightness=brightness,
            transition=0,
            color=color,
            on=True,
        )

