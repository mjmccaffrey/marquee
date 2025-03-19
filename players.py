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
        """Set up devices and initial state."""
        print("Initializing player")
        self.modes = modes
        self.sign = sign
        self.speed_factor = speed_factor
        self.current_mode = None
        self.previous_mode = None

    def close(self):
        """Close."""

    def play_mode(self, starting_mode_index: int):
        """"""
        self.current_mode = starting_mode_index
        for pass_count in itertools.count(start = 1):
            mode = self.modes[self.current_mode]
            print(f"Executing mode {mode.index} {mode.name}")
            try:
                new_mode = mode.execute(pass_count)
                if new_mode is not None:
                    self.previous_mode = self.current_mode
                    self.current_mode = new_mode
            except ButtonPressed as press:
                button, = press.args
                #print(f"Button Pressed: {button}")
                Button.reset()
                mode.button_action(button)

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
        """"""
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
