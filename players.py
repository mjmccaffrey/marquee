"""Marquee Lighted Sign Project - players"""

from collections.abc import Iterable
import itertools
import time
from typing import Any

from buttons import Button, ButtonPressed
from definitions import (
    ActionParams, DimmerParams, SpecialParams,
    ModeConstructor, ModeInterface,
)
from signs import Sign

class Player:
    """Executes one mode at a time."""
    def __init__(
            self, 
            modes: dict[int, ModeConstructor],
            sign: Sign, 
            speed_factor: float,
        ):
        """Set up initial state."""
        print("Initializing player")
        self.modes = modes
        self.sign = sign
        self.speed_factor = speed_factor
        self.current_mode = -1

    def close(self):
        """Close."""

    def replace_kwarg_values(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Replace variables with current runtime values."""
        new = {}
        for k, v in kwargs.items():
            match v:
                case 'LIGHT_PATTERN':
                    new[k] = self.sign.light_pattern
                case 'PREVIOUS_MODE':
                    new[k] = self.current_mode
                case _:
                    new[k] = v
        return new        

    def execute(self, starting_mode_index: int):
        """Play the specified mode and all subsequently selected modes."""
        new_mode = starting_mode_index
        while True:
            mode = self.modes[new_mode]
            mode = mode.mode_class(
                player=self, 
                name=mode.name, 
                **self.replace_kwarg_values(mode.kwargs),
            )
            self.current_mode = new_mode
            print(f"Executing mode {self.current_mode} {mode.name}")
            new_mode = self.play_mode_until_changed(mode)
            if new_mode == 222:
                new_mode = 2

    def play_mode_until_changed(self, mode: ModeInterface):
        """Play the specified mode until another mode is selected."""
        new_mode = None
        while new_mode is None:
            try:
                new_mode = mode.execute()
            except ButtonPressed as press:
                button, = press.args
                Button.reset()
                new_mode = mode.button_action(button)
        return new_mode

    def play_sequence(
            self, 
            sequence: Iterable, 
            count: int = 1, 
            pace: tuple[float, ...] | float | None = None,
            stop: int | None = None, 
            post_delay: float = 0, 
            special: SpecialParams | None = None,
        ):
        """Execute sequence count times, with pace seconds in between.
           If stop is specified, end the sequence 
           just before the nth pattern.
           Pause for post_delay seconds before exiting."""
        if isinstance(pace, (int, float)) or pace is None:
            pace_iter = itertools.repeat(pace)
        else:
            pace_iter = itertools.cycle(pace)
        for _ in range(count):
            for i, lights in enumerate(sequence):
                if stop is not None and i == stop:
                    break
                p = next(pace_iter)
                before = time.time()
                if p is not None:
                    if isinstance(special, DimmerParams):
                        special.speed_factor = self.speed_factor
                if isinstance(special, ActionParams):
                    special.action(lights)
                else:
                    self.sign.set_lights(
                        lights, 
                        special=special,
                    )
                after = time.time()
                self.wait(p, after - before)
        self.wait(post_delay)

    def wait(self, seconds: float | None, elapsed: float = 0):
        """Wait the specified seconds after adjusting for
           speed_factor and time already elapsed."""
        if seconds is None:
            duration = None
        else:
            duration = seconds * self.speed_factor - elapsed
            if duration <= 0:
                #print("!!!!!", seconds, elapsed, duration)
                return
        Button.wait(duration)
