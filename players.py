"""Marquee Lighted Sign Project - players"""

import contextlib
import time
import types

from sequences import seq_all_off, seq_all_on, seq_rotate_build
import signs

class Player:
    """Manages execution at a high level."""
    def __init__(self):
        """Set up devices and initial state."""
        self.mode_current = None
        self.mode_desired = None
        self.mode_previous = None
        self.mode_id_to_index = {}
        self.modes = {}
        self.add_mode(0, "selection", self._mode_selection)
        self._sign = signs.Sign()

    def close(self):
        """Close devices."""
        self._sign.close()

    def add_mode(
            self, index, name, function, 
            simple=False, pace=2,
            use_dimmers=False, transition_on=None, transition_off=None,
        ):
        """Register the mode, identified by index and name."""
        assert all(
            str(k) not in self.mode_id_to_index for k in (index, name)
            ), "Duplicate mode index or name"
        assert all(
            k in self.modes for k in range(index)
            ), "Non-sequential mode index"
        if simple:
            function = self._simple_mode(
                sequence=function, 
                pace=pace,
                use_dimmers=use_dimmers, 
                transition_on=transition_on,
                transition_off=transition_off,
            )
        self.modes[index] = types.SimpleNamespace(
            name=name,
            function=function,
        )
        self.mode_id_to_index[str(index)] = index
        self.mode_id_to_index[name] = index

    def _simple_mode(self, sequence, **kwargs):
        """Return closure to execute sequence indefinitely.
           with pace seconds in between.
           !!! Pace=None is an infinite pace, so in this case
           the sequence should have only 1 step."""
        def template():
            while True:
                self.do_sequence(sequence, **kwargs)
        return template

    def do_sequence(
            self, 
            sequence, count=1, pace=2, 
            stop=None, post_delay=None,
            use_dimmers=False,
            transition_on=None, transition_off=None,
        ):
        """Execute sequence count times, with pace seconds in between.
           If stop is specified, end the sequence 
           just before the nth pattern.
           Pause for post_delay seconds before exiting."""
        if use_dimmers:
            self.do_sequence(
                seq_all_on, pace=0
            )
        for _ in range(count):
            for i, lights in enumerate(sequence()):
                if stop is not None and i == stop:
                    break
                self._sign.set_lights(
                    lights, use_dimmers, transition_on, transition_off,
                )
                self._sign.wait_for_interrupt(pace)
        if post_delay is not None:
            self.sign.wait_for_interrupt(post_delay)

    def execute(self, mode_index=None, light_pattern=None, brightness_pattern=None):
        """Effects the specified mode or pattern(s)."""
        if light_pattern is not None:
            self._sign.set_lights(light_pattern)
            self._sign.set_dimmers(brightness_pattern)
            return
        if mode_index is not None:
            self.mode_current = mode_index
            while True:
                try:
                    self.modes[self.mode_current].function()
                except signs.ButtonPressed:
                    # Enter selection mode
                    self.mode_previous = self.mode_current
                    self.mode_current = 0
        raise ValueError("Nothing to do.")

    def _indicate_mode_desired(self):
        """Show user what desired mode number is currently selected."""
        self.do_sequence(
            seq_all_off, pace=0
        )
        time.sleep(0.6)
        for _ in range(self.mode_desired // 10):
            self.do_sequence(
                seq_rotate_build, pace=0.2, stop=self.mode_desired % 10,
            )

    def _mode_selection(self):
        """User presses the button to select 
           the next mode to execute."""
        while True:
            # Button was pressed
            self._sign.interrupt_reset()
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
                self._sign.wait_for_interrupt(5)
            except signs.ButtonPressed:
                pass
            else:
                # If we get here, the time elapsed
                # without the button being pressed.
                self.mode_current = self.mode_desired
                self.mode_desired = None
                self._sign.interrupt_reset()
                break
