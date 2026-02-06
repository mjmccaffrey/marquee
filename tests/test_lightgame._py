
import pytest

from color import *
from lightgame import *

def test_lightgame():
    pass

@dataclass(kw_only=True)
class E1(Entity):
    color=Colors.RED
    draw_priority=1

@dataclass(kw_only=True)
class E2(Entity):
    color=Colors.RED
    draw_priority=1

def board_1(game: LightGame) -> Board:
    return {
        0: {E1: E1(name='E1', game=game)},
        1: {E2: E2(name='E2', game=game)},
        2: {},
    }

def game_1():
    return LightGame(
        lights=None,  # type: ignore
        maze = {
            i: Square()
            for i in range(9)
        },
        schedule=None,  # type: ignore
        state_logic=None,   # type: ignore
        light_updates=None,  # type: ignore
    )

def test_lightgame_compare_boards_move_to_empty():
    game = game_1()
    game.board = {
        0: {E1: E1(name='E1', game=game)},
        1: {},
        2: {E2: E2(name='E2', game=game)},
    }
    assert game.compare_boards(board_1(game)) == {
        1: {},
        2: {E2: E2(name='E2', game=game)},
    }

def test_lightgame_compare_boards_move_to_occupied():
    game = game_1()
    game.board = {
        0: {},
        1: {E2: E2(name='E2', game=game), E1: E1(name='E1', game=game)},
        2: {},
    }
    assert game.compare_boards(board_1(game)) == {
        0: {},
        1: {E2: E2(name='E2', game=game), E1: E1(name='E1', game=game)},
    }
