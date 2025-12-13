
import pytest

from color import *
from lightgame import *

def test_lightgame():
    pass

class E1(Entity):
    name='E1'
    color=Colors.RED
    draw_priority=1

class E2(Entity):
    name='E2'
    color=Colors.RED
    draw_priority=1

def board_1() -> Board:
    return {
        0: {E1: E1(coord=0)},
        1: {E2: E2(coord=1)},
        2: {},
    }

def game_1():
    return LightGame(
        converter=None,  # type: ignore
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
        0: {E1: E1(coord=0)},
        1: {},
        2: {E2: E2(coord=1)},
    }
    assert game.compare_boards(board_1()) == {
        1: {},
        2: {E2: E2(coord=1)},
    }

def test_lightgame_compare_boards_move_to_occupied():
    game = game_1()
    game.board = {
        0: {},
        1: {E2: E2(coord=1), E1: E1(coord=0)},
        2: {},
    }
    assert game.compare_boards(board_1()) == {
        0: {},
        1: {E2: E2(coord=1), E1: E1(coord=0)},
    }
