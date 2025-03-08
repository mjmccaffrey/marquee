"""Marquee Lighted Sign Project - players"""

from collections.abc import Callable
from dataclasses import dataclass
import itertools
import time

from dimmers import Dimmer, RelayOverride, TRANSITION_DEFAULT
from sequences import seq_rotate_build
from signs import (
    ALL_HIGH, ALL_OFF, ALL_ON, ButtonPressed, 
    LIGHT_COUNT, EXTRA_COUNT, Sign,
)

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
        self.speed_factor: float = 1.0
        self.mode_id_to_index = {}
        self.commands = {
            'calibrate_dimmers': self.calibrate_dimmers,
            'configure_dimmers': self.configure_dimmers,
            'off': self.off,
        }
        self.modes: dict[int, Mode] = {}
        self.add_mode(0, "selection", self._mode_selection)
        self.sign: Sign = Sign()

    def close(self):
        """Close devices."""
        self.sign.close()

    def calibrate_dimmers(self):
        """Calibrate dimmers."""
        Dimmer.calibrate_all()

    def configure_dimmers(self):
        """Configure dimmers."""
        Dimmer.configure_all()

    def off(self):
        """Turn off all relays and potentially other devices."""
        self.sign.set_lights(ALL_OFF, '0' * EXTRA_COUNT)
        print("Marquee is partially shut down.")
        print()

    def add_mode(
            self, 
            index: int, 
            name: str, 
            function: Callable,
        ):
        """Register the mode, identified by index and name."""
        assert (
                index not in self.modes
            and str(index) not in self.mode_id_to_index 
            and name not in self.mode_id_to_index 
        ), "Duplicate mode index or name"
        assert all(
            k in self.modes for k in range(index)
        ), "Non-sequential mode index"
        self.modes[index] = Mode(
            name=name,
            function=function,
        )
        if index > 0:
            self.mode_id_to_index[str(index)] = index
            self.mode_id_to_index[name] = index
            
    def add_sequence_mode(
            self,
            index: int, 
            name: str, 
            sequence: Callable,
            pace: tuple[float, ...] | float | None = None,
            override: RelayOverride | None = None,
        ):
        """"""

        def sequence_doer():
            # If using only dimmers, turn relays on, and vice versa
            if override is not None:
                self.sign.set_lights(ALL_ON)
            else:
                self.sign.set_dimmers(ALL_HIGH)
            while True:
                self.do_sequence(sequence,
                    pace=pace,
                    override=override,
                )

        if override is not None:
            default_trans = (
                pace if isinstance(pace, float) else
                TRANSITION_DEFAULT
            )
            if override.transition_off is None:
                override.transition_off = default_trans
            if override.transition_on is None:
                override.transition_on = default_trans
        self.add_mode(
            index=index,
            name=name,
            function = sequence_doer
        )

    def wait(self, seconds: float, elapsed: float=0):
        """Wait the specified seconds after adjusting for
           speed_factor and time already elapsed."""
        seconds = seconds * self.speed_factor - elapsed
        if seconds > 0:
            self.sign.button_interrupt_wait(seconds)

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

    def execute(
            self, 
            command: str | None = None, 
            mode_index: int | None = None, 
            speed_factor: float | None = None,
            light_pattern: str | None = None, 
            brightness_pattern: str | None = None,
        ):
        """Effects the specified command, mode or pattern(s)."""
        Dimmer.finish_setup()
        if command is not None:
            self._execute_command(command)
        elif mode_index is not None:
            assert speed_factor is not None
            self._execute_mode(mode_index, speed_factor)
        else:
            self._execute_pattern(light_pattern, brightness_pattern)

    def _execute_command(self, command):
        """"""
        self.commands[command]()

    def _execute_mode(self, mode_index, speed_factor: float):
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
            self.sign.button_interrupt_wait(TRANSITION_DEFAULT)
        if light_pattern is not None:
            print(f"Setting lights {light_pattern}")
            self.sign.set_lights(light_pattern)

    def _indicate_mode_desired(self):
        """Show user what desired mode number is currently selected."""
        # self.sign.set_lights(ALL_ON)
        time.sleep(0.6)
        assert self.mode_desired is not None
        for _ in range(self.mode_desired // LIGHT_COUNT):
            self.do_sequence(
                seq_rotate_build, pace=0.2, stop=self.mode_desired % LIGHT_COUNT,
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
                self.sign.button_interrupt_wait(5)
            except ButtonPressed:
                pass
            else:
                # If we get here, the time elapsed
                # without the button being pressed.
                self.mode_current = self.mode_desired
                self.mode_desired = None
                self.sign.button_interrupt_reset()
                break
