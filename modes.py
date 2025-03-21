"""Marquee Lighted Sign Project - modes"""

from abc import ABC, abstractmethod
from collections.abc import Callable
import time
from typing import Any

from buttons import Button
from sequence_defs import *
from signs import ALL_HIGH, ALL_ON

class Mode(ABC):
    """"""

    _modes: list["Mode"] = []
    
    def __init__(
        self,
        player: Any,  # Player
        name: str,
        preset_dimmers: bool = False,
        preset_relays: bool = False,
    ):
        Mode._modes.append(self)
        self.player = player
        self.name = name
        self.preset_dimmers = preset_dimmers
        self.preset_relays = preset_relays

    @classmethod
    def mode_index(cls, current: int, delta: int) -> int:
        """"""
        lower, upper = 1, len(cls._modes) - 1
        value = current + delta % (upper - lower + 1)
        if (dif := value - upper) > 0:
            value = lower + dif - 1
        elif (dif := value - lower) < 0:
            value = upper + dif + 1
        return value

    @abstractmethod
    def button_action(self, button: Button):
        """"""

    def execute(self):
        """"""
        if self.player.pass_count == 1:
            if self.preset_dimmers:
                self.player.sign.set_dimmers(ALL_HIGH)
            if self.preset_relays:
                self.player.sign.set_lights(ALL_ON)
 
class PlayMode(Mode):
    """"""

    def __init__(
        self,
        player: Any,  # Player
        name: str,
        execute_func: Callable,
        preset_dimmers: bool = False,
        preset_relays: bool = False,
    ):
        super().__init__(player, name, preset_dimmers, preset_relays)
        self.execute_func = execute_func
        self.direction = +1

    def button_action(self, button: Button):
        """"""
        new_mode = None
        match button.name:
            case 'body_mode_select' | 'remote_mode_select':
                new_mode = 0
            case 'remote_mode_up':
                self.player.sign.click()
                new_mode = self.mode_index(self.player.current_mode, -1)
            case 'remote_mode_down':
                self.player.sign.click()
                new_mode = self.mode_index(self.player.current_mode, +1)
            # case 'remote_demo_mode':
            #     self.player.sign.click()
            #     new_mode = len(Mode._modes) - 1
            case 'remote_reverse':
                self.direction *= -1
            case _:
                raise Exception
        return new_mode

    def execute(self):
        """"""
        super().execute()
        # assert self.execute_func is not None
        self.execute_func()

class SelectMode(Mode):
    """"""

    def __init__(
        self,
        player: Any,  # Player
        name: str,
        preset_dimmers: bool = False,
        preset_relays: bool = False,
    ):
        super().__init__(player, name, preset_dimmers, preset_relays)
        self.desired_mode = -1

    def button_action(self, button: Button):
        """"""
        assert self.desired_mode is not None
        match button.name:
            case 'body_mode_select' | 'remote_mode_select' | 'remote_mode_down':
                self.desired_mode = self.mode_index(self.desired_mode, +1)
            case 'remote_mode_up':
                self.desired_mode = self.mode_index(self.desired_mode, -1)
            case 'remote_demo_mode':
                # self.desired_mode = 2  # ALL_OFF
                return 222  # Quick change to mode ALL_OFF
            case _:
                raise Exception
        return None

    def execute(self):
        """User presses the button to select 
           the next mode to execute."""
        super().execute()
        new_mode = None
        if self.player.pass_count == 1:
            #print("A")
            # Just now entering selection mode
            # !!!! Set dimmers all high - maybe remember and restore current state
            self.desired_mode = self.player.previous_mode
            self.previous_desired_mode = -1
        if self.desired_mode != self.previous_desired_mode:
            #print("B")
            # Not last pass.
            # Show user what desired mode number is currently selected.
            self.player.sign.set_lights(ALL_OFF)
            time.sleep(0.5)
            self.player.play_sequence(
                lambda: seq_rotate_build_flip(self.desired_mode), # type: ignore
                pace=0.20, post_delay=4.0,
            )
            self.previous_desired_mode = self.desired_mode
        else:
            #print("C")
            # Last pass.
            # Time elapsed without a button being pressed.
            # Play the selected mode.
            new_mode = self.desired_mode
        return new_mode

class RotateReversible(PlayMode):
    """"""
    def __init__(
        self,
        player: Any,  # Player
        name: str,
        pattern: str,
        pace: float,
    ):
        super().__init__(
            player=player, 
            name=name, 
            execute_func=lambda: None, 
            preset_dimmers=True, 
        )
        self.pattern = pattern
        self.player.wait(pace)

    def execute(self):
        self.player.sign.set_lights(self.pattern)
        self.pattern = (
            self.pattern[self.direction:] + self.pattern[:self.direction]
        )
