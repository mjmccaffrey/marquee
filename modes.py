"""Marquee Lighted Sign Project - modes"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from sequence_defs import *
from signs import ALL_HIGH, ALL_ON
import time

from buttons import Button
from players import Player

class Mode(ABC):
    """"""

    _modes: list["Mode"] = []
    
    def __init__(
        self,
        player: Player,
        index: int,
        name: str,
        execute: Callable | None = None,
        preset_dimmers: bool = False,
        preset_relays: bool = False,
    ):
        Mode._modes.append(self)
        self.player = player
        self.index = index
        self.name = name
        if execute is not None:
            self.execute = execute
        self.preset_dimmers = preset_dimmers
        self.preset_relays = preset_relays
        self.pass_count: int = 0

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

    def execute(self, pass_count):
        """"""
        if pass_count == 1:
            if self.preset_dimmers:
                self.player.sign.set_dimmers(ALL_HIGH)
            if self.preset_relays:
                self.player.sign.set_lights(ALL_ON)
 
class PlayMode(Mode):
    """"""

    def button_action(self, button: Button):
        """"""
        # assert self.current_mode is not None
        new_mode: int | None = None
        match button.name:
            case 'body_mode_select' | 'remote_mode_select':
                print("Entering selection mode")
                self.previous_mode = self.index
                self.current_mode = 0
            case 'remote_mode_up':
                self.player.sign.click()
                new_mode = self.mode_index(self.index, -1)
            case 'remote_mode_down':
                self.player.sign.click()
                new_mode = self.mode_index(self.index, +1)
            case 'remote_demo_mode':
                self.player.sign.click()
                new_mode = len(Mode._modes) - 1
            case _:
                raise Exception
        return new_mode
    
class SelectMode(Mode):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.desired_mode = None

    def button_action(self, button: Button):
        """"""
        assert self.desired_mode is not None
        match button.name:
            case 'body_mode_select' | 'remote_mode_select' | 'remote_mode_down':
                self.desired_mode = self.mode_index(self.desired_mode, +1)
            case 'remote_mode_up':
                self.desired_mode = self.mode_index(self.desired_mode, -1)
            case 'remote_demo_mode':
                self.desired_mode = 2  # ALL_OFF
            case _:
                raise Exception

    def execute(self, pass_count):
        """User presses the button to select 
           the next mode to execute."""
        super().execute(pass_count)
        new_mode = self.index
        if self.pass_count == 1:
            print("A")
            # Just now entering selection mode
            # !!!! Set dimmers all high - maybe remember and restore current state


            self.desired_mode = self.player.previous_mode  # ??? or pass this in ???
            self.previous_desired_mode = None
        if self.desired_mode != self.previous_desired_mode:
            print("B")
            # Not last pass.
            # Show user what desired mode number is currently selected.
            self.player.sign.set_lights(ALL_OFF)
            time.sleep(0.5)
            self.player.play_sequence(
                lambda: seq_rotate_build_flip(self.desired_mode),  # type: ignore
                pace=0.2, post_delay=5.0,
            )
            self.previous_desired_mode = self.desired_mode
        else:
            print("C")
            # Last pass.
            # Time elapsed without a button being pressed.
            # Play the selected mode.
            new_mode = self.desired_mode
        return new_mode
