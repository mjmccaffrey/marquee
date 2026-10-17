"""Marquee Lighted Sign Project - gamemode"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import auto, StrEnum
import logging
from typing import ClassVar, TypeVar
from typing_extensions import override

from devices.color import Color
from devices.lightcontroller import LightChannel, ChannelUpdate
from .performancemode import PerformanceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True, repr=False)
class SubEntity(ABC):
    """Less than a full entity."""
    name: str
    symbol: str
    color: ClassVar[Color]
    brightness: int = 100

    @override
    def __repr__(self):
        """"""
        return self.name


@dataclass(kw_only=True, repr=False)
class SpecialRender(SubEntity):
    """For board display purposes."""
    color: Color | None = None


@dataclass(kw_only=True, repr=False)
class Entity(SubEntity, ABC):
    """Physical entities appear in the game."""
    draw_priority: ClassVar[int]
    game: 'GameMode'
    coord: int | None = None


@dataclass(kw_only=True, repr=False)
class Character(Entity, ABC):
    """Characters can move."""
    turn_priority: ClassVar[int]
    prior_coord: int | None = None
 
    @abstractmethod
    def execute(self) -> None:
        """Take turn."""


@dataclass(kw_only=True)
class Square:
    left: int | None
    right: int | None
    up: int | None
    down: int | None
    upleft: int | None
    downleft: int | None
    upright: int | None
    downright: int | None


Board = dict[int, 'EntityGroup']
EntityGroup = dict[type[Entity], Entity]
BoardRendition = tuple[SubEntity, ...]
Maze = dict[int, Square]
render_empty = SpecialRender(name="Empty", symbol='_')


class GameState(StrEnum):
    PLAY_GAME = auto()


@dataclass(kw_only=True)
class GameMode(PerformanceMode):
    """Play a game with the lights."""
    maze: Maze
    ticks_per_second: float # !!! adjust by speed_factor

    def __post_init__(self) -> None:
        """"""
        super().__post_init__()
        self.state = GameState.PLAY_GAME

    def desired_light_state(
        self, 
        rendition: SubEntity,
        channel: LightChannel,
    ) -> ChannelUpdate:
        """Return ChannelUpdate."""
        if rendition == render_empty:
            return ChannelUpdate(channel=channel, on=False)
        return ChannelUpdate(
            channel=channel,
            brightness=rendition.brightness,
            transition=0,
            color=rendition.color,
            on=True,
        )

    @abstractmethod
    def square_rendition(self, entities: EntityGroup) -> SubEntity:
        """"""

    @abstractmethod
    def state_logic(self) -> None:
        """"""

    def execute_state(self) -> None:
        match self.state:
            case GameState.PLAY_GAME:
                func = self.play_game_state
            case _:
                raise RuntimeError(self.state)
        func()
    
    def change_state(self, state: StrEnum) -> None:
        """"""
        print(f'{state=}')
        self.player.tasks.delete_owned_by(self)
        self.state = state
        self.schedule(action=self.execute_state)

    def init_level(self) -> None:
        """"""
        self.board: Board = {coord: {} for coord in sorted(self.maze)}
        self.characters_by_name: dict[str, Character] = {}
        self.characters_turn_order: list[Character] = []
        self.tick: int = 0

    @override
    def execute(self) -> None:
        """"""
        self.execute_state()

    def play_game_state(self) -> None:
        """"""
        self.schedule(
            action=self.play_game_round,
            due=(1 / self.ticks_per_second),
            repeat=True,
        )

    def play_game_round(self) -> None:
        """Execute a game round."""
        previous_board = self.copy_board()
        self.characters_take_turns()
        self.state_logic()
        # print(f"{self.previous_board=}")
        # print(f"         {self.board=}")
        if self.board != previous_board:
            self.render_board()
        # else:
        #     print('boards are equal')
        self.tick += 1

    def characters_take_turns(self) -> None:
        """"""
        for character in self.characters_turn_order:
            character.execute()

    def copy_board(self) -> Board:
        """"""
        return {
            i: {t: e for t, e in eg.items()}
            for i, eg in self.board.items()
        }

    def render_board(self) -> None:
        """"""
        rendition = tuple(
            self.square_rendition(e)
            for e in self.board.values()
        )
        self.update_lights(rendition)
        self.print_board(rendition)

    def update_lights(self, rendition: BoardRendition) -> None:
        """Send (unfiltered) desired light states to lightset."""
        desired = [
            self.desired_light_state(
                rendition=r, 
                channel=c,
            )
            for r, c in zip(rendition, self.lights.channels)
        ]
        self.lights.update_channels(desired)

    def print_board(self, rendition: BoardRendition) -> None:
        """"""

    def print_board_debug(self) -> None:
        """"""
        log.info("*****")
        for i in self.board:
            log.info(i)
            for e in self.board[i].values():
                log.info("  " + e.name)
        log.info("*****")

    E = TypeVar("E", bound=Entity)

    def register_entity(self, entity: E) -> E:
        """Register and return new entity."""
        if isinstance(entity, Character):
            self.characters_by_name[entity.name] = entity
            self.characters_turn_order.append(entity)
            self.characters_turn_order.sort(key = lambda c: c.turn_priority)
        return entity

    def place_entity(self, entity: Entity, coord: int) -> None:
        """Place entity on board at coord."""
        coord = coord % len(self.board)
        entity.coord = coord
        self.board[entity.coord][type(entity)] = entity

    def move_character(self, character: Character, coord: int) -> None:
        """Move character to coord."""
        coord = coord % len(self.board)
        assert character.coord is not None
        del self.board[character.coord][type(character)]
        character.prior_coord = character.coord
        self.place_entity(character, coord)

