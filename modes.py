"""Marquee Lighted Sign Project - modes"""

from abc import ABC, abstractmethod
from collections.abc import Callable
import time
from typing import Any

from buttons import Button
from sequence_defs import *
from signs import ALL_HIGH, ALL_ON

class Mode(ABC):
    """Base for all playing modes and the select mode."""

    _modes: list["Mode"] = []
    
    def __init__(
        self,
        player: Any,  # Player
        name: str,
        preset_dimmers: bool = False,
        preset_relays: bool = False,
    ):
        """"""
        Mode._modes.append(self)
        self.player = player
        self.name = name
        self.preset_dimmers = preset_dimmers
        self.preset_relays = preset_relays

    @classmethod
    def mode_index(cls, current: int, delta: int) -> int:
        """Return a new mode index, wrapping in both directions."""
        lower, upper = 1, len(cls._modes) - 1
        value = current + delta % (upper - lower + 1)
        if (dif := value - upper) > 0:
            value = lower + dif - 1
        elif (dif := value - lower) < 0:
            value = upper + dif + 1
        return value

    @abstractmethod
    def button_action(self, button: Button):
        """Respond to the button press."""

    def execute(self):
        """Play the mode."""
        if self.player.pass_count == 1:
            if self.preset_dimmers:
                self.player.sign.set_dimmers(ALL_HIGH)
            if self.preset_relays:
                # print("presetting relays")
                self.player.sign.set_lights(ALL_ON)
 
class PlayMode(Mode):
    """Supports all sequence- and function-based modes.
       Base for custom modes."""

    def __init__(
        self,
        player: Any,  # Player
        name: str,
        execute_func: Callable,
        preset_dimmers: bool = False,
        preset_relays: bool = False,
    ):
        """"""
        super().__init__(player, name, preset_dimmers, preset_relays)
        self.execute_func = execute_func
        self.direction = +1

    def button_action(self, button: Button):
        """Respond to the button press."""
        new_mode = None
        match button.name:
            case 'remote_a' | 'body_back':
                new_mode = 0
            case 'remote_c':
                self.player.sign.click()
                self.direction *= -1
            case 'remote_b':
                self.player.sign.click()
                new_mode = self.mode_index(self.player.current_mode, -1)
            case 'remote_d':
                self.player.sign.click()
                new_mode = self.mode_index(self.player.current_mode, +1)
            case _:
                raise Exception
        return new_mode

    def execute(self):
        """Play the mode."""
        super().execute()
        # assert self.execute_func is not None
        self.execute_func()

class SelectMode(Mode):
    """Supports the select mode."""

    def __init__(
        self,
        player: Any,  # Player
        name: str,
    ):
        super().__init__(player, name, preset_dimmers=True)
        self.desired_mode = -1

    def button_action(self, button: Button):
        """Respond to the button press."""
        assert self.desired_mode is not None
        match button.name:
            case 'body_back' | 'remote_a' | 'remote_d':
                self.desired_mode = self.mode_index(self.desired_mode, +1)
            case 'remote_b':
                self.desired_mode = self.mode_index(self.desired_mode, -1)
            case 'remote_c':
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
    """Rotate a pattern, reversing direction in response to a button press."""
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
        self.pace = pace

    def execute(self):
        """Display a single pattern.
           Called repeatedly until the mode is changed."""
        self.player.sign.set_lights(self.pattern)
        self.player.wait(self.pace)
        self.pattern = (
            self.pattern[self.direction:] + self.pattern[:self.direction]
        )
