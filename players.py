""" """

import time
import types

from sequences import seq_all_off, seq_rotate_build
import signs

class Player:
    """ """
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

    def add_mode(self, index, name, function, simple=False, pace=2):
        """Register the mode function, identified by index and name."""
        assert all(
            str(k) not in self.mode_id_to_index for k in (index, name)
            ), "Duplicate mode index or name"
        assert all(
            k in self.modes for k in range(index)
            ), "Non-sequential mode index"
        if simple:
            function = self._simple_mode(function, pace)
        self.modes[index] = types.SimpleNamespace(
            name=name,
            function=function,
        )
        self.mode_id_to_index[str(index)] = index
        self.mode_id_to_index[name] = index

    def _simple_mode(self, sequence, pace):
        """Return closure to execute sequence indefinitely, 
           with pace seconds in between.
           Pace=None is an infinite pace, so in this case
           the sequence should have only 1 step."""
        def template():
            while True:
                self.do_sequence(sequence, 1, pace)
        return template

    @property
    def current_pattern(self):
        """Wrapper for Sign.current_pattern."""
        return self._sign.current_pattern

    def do_sequence(self, *args, **kwargs):
        """Wrapper for Sign.do_sequence."""
        return self._sign.do_sequence(*args, **kwargs)

    def is_valid_light_pattern(self, *args, **kwargs):
        """Wrapper for Sign.is_valid_light_pattern."""
        return self._sign.is_valid_light_pattern(*args, **kwargs)

    def set_lights(self, *args, **kwargs):
        """Wrapper for Sign.set_lights."""
        return self._sign.set_lights(*args, **kwargs)

    def execute(self, mode=None, pattern=None):
        """ """
        if pattern is not None:
            self._sign.set_lights(pattern)
            return
        if mode is not None:
            self.mode_current = mode
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
        assert len(self.modes) <= signs.LIGHT_COUNT, \
               "Cannot indicate this many modes"
        self._sign.do_sequence(seq_all_off, pace=0)
        time.sleep(0.6)
        self._sign.do_sequence(seq_rotate_build, pace=0.2, stop=self.mode_desired)

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
