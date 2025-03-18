"""Marquee Lighted Sign Project - players"""

from collections.abc import Callable
import itertools
import time

from buttons import Button, ButtonPressed
from dimmers import RelayOverride
from modes import Mode
from sequences import seq_rotate_build_flip
from signs import ALL_ON, ALL_HIGH, Sign

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
        self.mode_current = None
        self.mode_desired = None
        self.mode_previous = None

    def close(self):
        """Close."""

    def change_mode(self, current: int, delta: int) -> int:
        """"""
        lower, upper = 1, len(self.modes) - 1
        value = current + delta % (upper - lower + 1)
        if (dif := value - upper) > 0:
            value = lower + dif - 1
        elif (dif := value - lower) < 0:
            value = upper + dif + 1
        return value

    def play_mode(self, mode_index):
        """"""
        self.mode_current = mode_index
        while True:
            mode = self.modes[self.mode_current]
            print(f"Executing mode {mode.index} {mode.name}")
            try:
                if mode.preset_dimmers:
                    self.sign.set_dimmers(ALL_HIGH)
                if mode.preset_relays:
                    self.sign.set_lights(ALL_ON)
                assert mode.function is not None
                mode.function()
            except ButtonPressed as press:
                button, = press.args
                print(f"Button Pressed: {button}")
                Button.reset()
                match button.name:
                    case 'body_mode_select' | 'remote_mode_select':
                        print("Entering selection mode")
                        self.mode_previous = self.mode_current
                        self.mode_current = 0
                    case 'remote_mode_up':
                        self.sign.make_click()
                        self.mode_current = self.change_mode(self.mode_current, -1)
                    case 'remote_mode_down':
                        self.sign.make_click()
                        self.mode_current = self.change_mode(self.mode_current, +1)
                    case 'remote_demo_mode':
                        self.sign.make_click()
                        self.mode_current = len(self.modes) - 1
                    case _:
                        raise Exception

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

    def _mode_selection(self):
        """User presses the button to select 
           the next mode to execute."""
        # !!!! Set dimmers all high - maybe remember and restore current state
        while True:
            # Button was pressed
            Button.reset()
            if self.mode_desired is None:
                # Just now entering selection mode
                self.mode_desired = self.mode_previous
            else:
                # Was already in selection mode
                match button.name:
                    case (
                          'body_mode_select' | 'remote_mode_select'
                        | 'remote_mode_down' | 'remote_demo_mode'
                    ):
                        self.mode_desired = self.change_mode(self.mode_desired, +1)
                    case 'remote_mode_up':
                        self.mode_desired = self.change_mode(self.mode_desired, -1)
                    case _:
                        raise Exception
            # Show user what desired mode number is currently selected.
            time.sleep(0.6)
            self.play_sequence(
                lambda: seq_rotate_build_flip(self.mode_desired),  # type: ignore
                pace=0.15, post_delay=0.3,
            )
            # Wait for user to press button again, or not.
            try:
                Button.wait(5)
            except ButtonPressed as press:
                button, = press.args
                print(f"Button Pressed: {button}")
                #pass
            else:
                # If we get here, the time elapsed
                # without a button being pressed.
                self.mode_current = self.mode_desired
                self.mode_desired = None
                break
