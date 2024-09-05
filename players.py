""" """

import signs
from signs import LIGHT_COUNT

class Player:
    """ """
    def __init__(self):
        """Set up devices and initial state."""
        self.mode_desired = None
        self.mode_current = 1
        self.mode.id_to_index = {}
        self.mode_table = {}
        self.add_mode(0, "selection", _mode_selection)
        self.sign = signs.Sign()

    def close(self):
        """Close devices."""
        self.sign.close()

    def add_mode(index, name, function):
        """Register the mode function, identified by index and name."""
        assert all(k not in mode.id_to_index for k in (index, name)), \
               "Duplicate mode ID"
        assert all(k in self.mode_table for k in range(index)), \
               "Missing mode ID"
        self.mode_table[index] = types.SimpleNamespace(
            name=name,
            function=function,
        )
        mode.count = len(self.mode_table)
        mode.id_to_index[str(index)] = index
        mode.id_to_index[name] = index

    def execute(self, mode=None, pattern=None):
        """ """
        if pattern is not None:
            self.sign.set_lights(pattern)
            return
        if mode is not None:
            self.current_mode = mode
            while True:
                try:
                    self.mode_table[self.mode_current].function()
                except signs.ButtonPressed:
                    # Enter selection mode
                    self.mode_previous = self.mode_current
                self.mode_current = 0
        raise ValueError("Nothing to do.")

    def simple_mode(self, sequence, pace=None):
        """Return closure to execute sequence indefinitely, 
           with pace seconds in between.
           Pace=None is an infinite pace, so in this case
           the sequence should have only 1 step."""
        def template():
            while True:
                self.sign.do_sequence(sequence, 1, pace)
        return template

    def _indicate_mode_desired(self):
        """Show user what desired mode number is currently selected."""
        assert mode.count <= LIGHT_COUNT, \
               "Cannot indicate this many modes"
        self.sign.do_sequence(seq_all_off)
        time.sleep(0.6)
        self.sign.do_sequence(seq_rotate_build, pace=0.2, stop=self.mode_desired)

    def _mode_selection():
        """User presses the button to select 
           the next mode to execute."""
        while True:
            # Button was pressed
            self.sign.interrupt_reset()
            if self.mode_desired is None:
                # Just now entering selection mode
                self.mode_desired = self.mode_previous
            else:
                if self.mode_desired == mode.count:
                    self.mode_desired = 1
                else:
                    self.mode_desired += 1
            self._indicate_mode_desired()
            try:
                self.sign.wait_for_interrupt(5)
            except signs.ButtonPressed:
                pass
            else:
                # If we get here, the time elapsed
                # without the button being pressed.
                self.mode_current = self.mode_desired
                self.mode_desired = None
                self.sign.interrupt_reset()
                break
