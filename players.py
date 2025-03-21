"""Marquee Lighted Sign Project - players"""

from collections.abc import Callable
import itertools
import time

from buttons import Button, ButtonPressed
from dimmers import RelayOverride
from modes import Mode
from signs import Sign

class Player:
    """Executes one mode at a time."""
    def __init__(
            self, 
            modes: dict[int, Mode],
            sign: Sign, 
            speed_factor: float,
        ):
        """Set up initial state."""
        print("Initializing player")
        self.modes = modes
        self.sign = sign
        self.speed_factor = speed_factor
        self.current_mode = -1
        self.previous_mode = None

    def close(self):
        """Close."""

    def execute(self, starting_mode_index: int):
        """Play the specified mode and all subsequently selected modes."""
        self.current_mode = starting_mode_index
        while True:
            new_mode = self.play_mode_until_changed(self.current_mode)
            assert new_mode is not None
            if new_mode == 222:
                new_mode = 2
            self.previous_mode = self.current_mode
            self.current_mode = new_mode

    def play_mode_until_changed(self, mode_index: int):
        """Play the specified mode until another mode is selected."""
        mode = self.modes[mode_index]
        self.pass_count = 0
        new_mode = None
        print(f"Executing mode {mode_index} {mode.name}")
        while new_mode is None:
            try:
                self.pass_count += 1
                new_mode = mode.execute()
            except ButtonPressed as press:
                button, = press.args
                Button.reset()
                new_mode = mode.button_action(button)
        return new_mode

    def play_sequence(
            self, 
            sequence: Callable, 
            count: int = 1, 
            pace: tuple[float, ...] | float | None = None,
            stop: int | None = None, 
            post_delay: float = 0, 
            override: RelayOverride | None = None,
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
            for i, lights in enumerate(sequence()):
                if stop is not None and i == stop:
                    break
                p = next(pace_iter)
                before = time.time()
                if p is not None:
                    if override is not None:
                        override.speed_factor = self.speed_factor
                self.sign.set_lights(
                    lights, 
                    override=override,
                )
                after = time.time()
                self.wait(p, after - before)
        self.wait(post_delay)

    def sequence_player_func(
        self,
        sequence: Callable,
        pace: tuple[float, ...] | float | None = None,
        override: RelayOverride | None = None,
    ) -> Callable:
        """Returns a function with the supplied parameters via closure."""
        def sequence_player():
            while True:
                self.play_sequence(sequence,
                    pace=pace,
                    override=override,
                )
        return sequence_player

    def wait(self, seconds: float | None, elapsed: float = 0):
        """Wait the specified seconds after adjusting for
           speed_factor and time already elapsed."""
        if seconds is not None:
            seconds = seconds * self.speed_factor - elapsed
            if seconds <= 0:
                return
        Button.wait(seconds)
