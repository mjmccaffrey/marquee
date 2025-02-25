"""Marquee Lighted Sign Project - players"""

from collections.abc import Callable
from dataclasses import dataclass
import itertools
import time

from dimmers import Dimmer, RelayOverride, TRANSITION_DEFAULT
from sequences import seq_rotate_build
from signs import ALL_HIGH, ALL_ON, ButtonPressed, Sign

@dataclass
class Mode:
    name: str
    function: Callable

class Player:
    """Manages execution at a high level."""
    def __init__(self):
        """Set up devices and initial state."""
        print("Initializing player")
        self.mode_current = None
        self.mode_desired = None
        self.mode_previous = None
        self.speed_factor = 1.0
        self.mode_id_to_index = {}
        self.commands = {'calibrate_dimmers': self.calibrate}
        self.modes: dict[int, Mode] = {}
        self.add_mode(0, "selection", self._mode_selection)
        self.sign: Sign = Sign()

    def close(self):
        """Close devices."""
        self.sign.close()

    def calibrate(self):
        """"""
        Dimmer.calibrate_all()

    def add_mode(
            self, 
            index: int, 
            name: str, 
            mode: Callable = None,
            sequence: Callable = None,
            pace: float = None,
            relay_override: RelayOverride = None,
        ):
        """Register the mode, identified by index and name."""
        assert not (mode and sequence), "Specify either mode or sequence."
        assert (
                index not in self.modes
            and str(index) not in self.mode_id_to_index 
            and name not in self.mode_id_to_index 
        ), "Duplicate mode index or name"
        assert all(
            k in self.modes for k in range(index)
            ), "Non-sequential mode index"
        if sequence:
            function = self._sequence_mode(
                sequence=sequence, 
                pace=pace,
                relay_override=relay_override, 
            )
        else:
            function = mode
        self.modes[index] = Mode(
            name=name,
            function=function,
        )
        if index > 0:
            self.mode_id_to_index[str(index)] = index
            self.mode_id_to_index[name] = index

    def _sequence_mode(
            self, 
            sequence: Callable, 
            pace: float,
            relay_override: RelayOverride,
        ):
        """Return closure to execute sequence indefinitely.
           with pace seconds in between.
           Pace=None produces an infinite wait, so in this case
           the sequence should have only 1 step."""
        def template():
            # If using only dimmers, turn relays on, and vice versa
            if relay_override is not None:
                self.sign.set_lights(ALL_ON)
            else:
                self.sign.set_dimmers(ALL_HIGH)
            while True:
                self.do_sequence(sequence, **kwargs)
                print("after")
        return template

    def wait(self, seconds: float):
        """"""
        if seconds is not None:
            seconds *= self.speed_factor
        self.sign.wait_for_button_interrupt(seconds)

    def do_sequence(
            self, 
            sequence: Callable, 
            count: int = 1, 
            pace: float = None, 
            stop: int = None, 
            post_delay: float = None,
            relay_override: RelayOverride = None,
        ):
        """Execute sequence count times, with pace seconds in between.
           If stop is specified, end the sequence 
           just before the nth pattern.
           Pause for post_delay seconds before exiting."""
        if isinstance(pace, (float, int)) or pace is None:
            pace = itertools.repeat(pace)
        else:
            pace = itertools.cycle(pace)
        for _ in range(count):
            print("top outer")
            for i, lights in enumerate(sequence()):
                if stop is not None and i == stop:
                    break
                p = next(pace)
                if p is not None:
                    if relay_override is not None:
                        relay_override.speed_factor = self.speed_factor
                print(lights)
                self.sign.set_lights(
                    lights, 
                    relay_override=relay_override,
                )
                self.wait(p)
        if post_delay is not None:
            self.wait(post_delay)

    def execute(
            self, 
            command: str = None, 
            mode_index: int = None, 
            speed_factor: float = None,
            light_pattern: str = None, 
            brightness_pattern: str = None,
        ):
        """Effects the specified command, mode or pattern(s)."""
        Dimmer.finish_setup()
        if command is not None:
            self._execute_command(command)
        elif mode_index is not None:
            self._execute_mode(mode_index, speed_factor)
        else:
            self._execute_pattern(light_pattern, brightness_pattern)

    def _execute_command(self, command):
        """"""
        self.commands[command]()

    def _execute_mode(self, mode_index, speed_factor):
        """"""
        self.mode_current = mode_index
        self.speed_factor = speed_factor
        while True:
            print(f"Executing mode {self.modes[self.mode_current].name}")
            try:
                self.modes[self.mode_current].function()
            except ButtonPressed:
                print(f"Entering selection mode")
                self.mode_previous = self.mode_current
                self.mode_current = 0

    def _execute_pattern(self, light_pattern, brightness_pattern):
        """"""
        # ??? flip order and remove wait?
        if brightness_pattern is not None:
            print(f"Setting dimmers {brightness_pattern}")
            self.sign.set_dimmers(brightness_pattern)
            self.sign.wait_for_button_interrupt(TRANSITION_DEFAULT)
        if light_pattern is not None:
            print(f"Setting lights {light_pattern}")
            self.sign.set_lights(light_pattern)

    def _indicate_mode_desired(self):
        """Show user what desired mode number is currently selected."""
        # self.sign.set_lights(ALL_ON)
        time.sleep(0.6)
        for _ in range(self.mode_desired // 10):
            self.do_sequence(
                seq_rotate_build, pace=0.2, stop=self.mode_desired % 10,
                post_delay=0.3,
            )

    def _mode_selection(self):
        """User presses the button to select 
           the next mode to execute."""
        while True:
            # Button was pressed
            self.sign.button_interrupt_reset()
            if self.mode_desired is None:
                # Just now entering selection mode
                self.mode_desired = self.mode_previous
            else:
                if self.mode_desired == len(self.modes) - 1:
                    self.mode_desired = 1
                else:
                    self.mode_desired += 1
            self._indicate_mode_desired()
            try:
                self.sign.wait_for_button_interrupt(5)
            except ButtonPressed:
                pass
            else:
                # If we get here, the time elapsed
                # without the button being pressed.
                self.mode_current = self.mode_desired
                self.mode_desired = None
                self.sign.button_interrupt_reset()
                break
