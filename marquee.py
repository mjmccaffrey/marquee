"""Marquee Lighted Sign Project - main"""

import sys
import time
import types

from modes import *
from sequences import *
import signs
from signs import LIGHT_COUNT

class ApplicationExit(Exception):
    """Runtime argument, or lack thereof, necessitates an early exit."""

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
    assert mode.count <= LIGHT_COUNT, "Cannot indicate this many modes"
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
            if mode.desired == mode.count:
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

def add_mode(index, name, function, private=False):
    """Register the mode function, identified by index and name."""
    assert all(k not in mode.id_to_index for k in (str(index), name)), \
           "Duplicate mode ID"
    mode.table[index] = types.SimpleNamespace(name=name, function=function)
    mode.count = len(mode.table)
    if not private:
        mode.id_to_index[str(index)] = index
        mode.id_to_index[name] = index

def display_help():
    """"Display the command-line syntax."""
    print()
    print("Usage: marquee.py {mode_index | mode_name | light_pattern}")
    print()
    print("Examples:")
    print("  marquee.py 5")
    print("  marquee.py blink_all")
    print("  marquee.py 0000000000")
    print()
    print("Modes:")
    for index, entry in mode.table.items():
        if index != 0:
            print(f'{index: >2}  {entry.name}')
    print()

def register_modes():
    """Register the operating modes as part of setup."""
    mode.id_to_index = {}
    mode.table = {}
    add_mode(0, "selection", mode_selection, private=True)  # Must be first
    add_mode(1, "all_on", simple_mode(seq_all_on))
    add_mode(2, "even_on", simple_mode(seq_even_on))
    add_mode(3, "even_off", simple_mode(seq_even_off))
    add_mode(4, "all_off", simple_mode(seq_all_off))
    add_mode(5, "blink_all", simple_mode(seq_blink_all, pace=1))
    add_mode(6, "blink_alternate", simple_mode(seq_blink_alternate, pace=1))
    add_mode(7, "demo", lambda: mode_rhythmic_demo(do_sequence))

def process_runtime_argument(argv):
    """Validate the runtime argument as part of setup.
       If a light pattern is specified, set the lights accordingly
       and initiate exit."""
    if len(argv) != 2:
        display_help()
        raise ApplicationExit
    arg = argv[1]
    if sign.is_valid_light_pattern(arg):
        sign.set_lights(arg)
        raise ApplicationExit
    if arg not in mode.id_to_index:
        display_help()
        raise ApplicationExit
    mode.current = mode.id_to_index[arg]
    return True

def setup(argv):
    """Set up devices and initial state."""
    global mode
    global sign
    mode = types.SimpleNamespace()
    mode.desired = None
    sign = signs.Sign()
    register_modes()
    process_runtime_argument(argv)

def execute():
    """Outermost application loop."""
    while True:
        try:
            mode.table[mode.current].function()
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
    # time.sleep(1)
    #
    try:
        setup(sys.argv)
    except ApplicationExit:
        pass
    else:
        execute()
    cleanup()

if __name__ == "__main__":
    main()
