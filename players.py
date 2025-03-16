"""Marquee Lighted Sign Project - players"""

from collections.abc import Callable
import itertools
import time

from buttons import ButtonPressed
from dimmers import RelayOverride
from modes import Mode
from sequences import seq_rotate_build_flip
from signs import LIGHT_COUNT, Sign

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
        lower, upper = 1, len(self.modes)
        value = current + delta % (upper - lower + 1)
        if (dif := value - upper) > 0:
            value = lower + dif - 1
        elif (dif := value - lower) < 0:
            value = upper + dif + 1
        return value


    def start(self, mode_index):
        """"""
        self.mode_current = mode_index
        print(f"Start Top - The current mode is now {self.mode_current}")
        while True:
            print(f"Executing mode {self.modes[self.mode_current].name}")
            try:
                function = self.modes[self.mode_current].function
                assert function is not None
                function()
            except ButtonPressed as press:
                button, = press.args
                print(f"Button Pressed: {button}")
                match button.name:
                    case 'body_mode_select' | 'remote_mode_select':
                        print("Entering selection mode")
                        self.mode_previous = self.mode_current
                        self.mode_current = 0
                    case 'remote_mode_up':
                        self.mode_current = self.change_mode(self.mode_current, +1)
                    case 'remote_mode_down':
                        self.mode_current = self.change_mode(self.mode_current, -1)
                    case 'remote_demo_mode':
                        self.mode_current = len(self.modes) - 1
                    case _:
                        raise Exception

    def do_sequence(
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
        if isinstance(pace, float) or pace is None:
            pace_iter = itertools.repeat(pace)
        else:
            assert isinstance(pace, tuple)
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
                if p is not None:
                    self.wait(p, after - before)
        self.wait(post_delay)

    def wait(self, seconds: float, elapsed: float=0):
        """Wait the specified seconds after adjusting for
           speed_factor and time already elapsed."""
        seconds = seconds * self.speed_factor - elapsed
        if seconds > 0:
            self.sign.button_interrupt_wait(seconds)

    def _indicate_mode_desired(self):
        """Show user what desired mode number is currently selected."""
        # self.sign.set_lights(ALL_ON)
        time.sleep(0.6)

        #rotate to mode_desired, toggling lights off in 20s etc.
        #rotate faster

        self.do_sequence(
            lambda: seq_rotate_build_flip(self.mode_desired), # type: ignore ???
            pace=0.15, post_delay=0.3,
        )

    def _mode_selection(self):
        """User presses the button to select 
           the next mode to execute."""
        while True:
            # Button was pressed
            print(1)
            self.sign.button_interrupt_reset()
            print(2)
            if self.mode_desired is None:
                # Just now entering selection mode
                self.mode_desired = self.mode_previous
            else:
                # Was already in selection mode
                self.mode_desired = self.change_mode(self.mode_desired, +1)
            self._indicate_mode_desired()
            try:
                self.sign.button_interrupt_wait(5)
            except ButtonPressed as press:
                button, = press.args
                print(f"Button Pressed: {button}")
                pass
            else:
                # If we get here, the time elapsed
                # without the button being pressed.
                self.mode_current = self.mode_desired
                print(f"Mode Selection - The current mode is now {self.mode_current}")
                self.mode_desired = None
                print(3)
                # self.sign.button_interrupt_reset()
                print(4)
                break
