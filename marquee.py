"""Marquee Lighted Sign Project - main"""

# Test rhythm demo small change

import time
import types

from modes import *
from sequences import *
import signs
from signs import LIGHT_COUNT

def do_sequence(sequence, count=1, pace=0, stop=None, post_delay=None):
    """Execute sequence count times, with pace seconds in between.
       If stop is specified, end the sequence just before the nth pattern.
       Pause for post_delay seconds before exiting."""
    for _ in range(count):
        for i, lights in enumerate(sequence()):
            if stop is not None and i == stop:
                break
            sign.set_lights(lights)
            sign.wait_for_interrupt(pace)
    if post_delay is not None:
        sign.wait_for_interrupt(post_delay)

def simple_mode(sequence, pace=None):
    """Execute sequence indefinitely, with pace seconds in between.
       Pace=None is an infinite pace, so in this case
       the sequence should have only 1 step."""
    def template():
        while True:
            do_sequence(sequence, 1, pace)
    return template

def indicate_mode_desired():
    """Show user what desired mode number is currently selected."""
    assert MODE_COUNT <= LIGHT_COUNT, "Cannot indicate this many modes"
    do_sequence(seq_all_off)
    time.sleep(0.6)
    do_sequence(seq_rotate_build, pace=0.2, stop=mode.desired)

def mode_selection():
    """User presses the button to select 
       the next mode to execute."""
    while True:
        # Button was pressed
        sign.interrupt_reset()
        if mode.desired is None:
            # Just now entering selection mode
            mode.desired = mode.previous
        else:
            mode.desired += 1
            if mode.desired == MODE_COUNT:
                mode.desired = 1
        indicate_mode_desired()
        try:
            sign.wait_for_interrupt(5)
        except signs.ButtonPressed:
            pass
        else:
            # If we get here, the time elapsed
            # without the button being pressed.
            mode.current = mode.desired
            mode.desired = None
            sign.interrupt_reset()
            break

def setup():
    """Set up devices and initial state."""
    global mode
    global sign
    mode = types.SimpleNamespace()
    mode.current = 4
    mode.desired = None
    sign = signs.Sign()

def execute():
    """Outermost application loop."""
    while True:
        try:
            MODES[mode.current]()
        except signs.ButtonPressed:
            # Enter selection mode
            mode.previous = mode.current
            mode.current = 0

def cleanup():
    """Close devices."""
    sign.close()

def main():
    """Execute Marquee application."""
    # HACK - give Pi Zero time for relay board to show up during boot
    time.sleep(1)
    #
    setup()
    execute()
    cleanup()

MODES = [
    mode_selection, # Must be first
    simple_mode(seq_all_on),
    simple_mode(seq_even_on),
    simple_mode(seq_even_off),
    simple_mode(seq_all_off),
    simple_mode(seq_blink_all, pace=1),
    simple_mode(seq_blink_alternate, pace=1),
    lambda: mode_rhythmic_demo(do_sequence),
]
MODE_COUNT = len(MODES)

if __name__ == "__main__":
    main()
