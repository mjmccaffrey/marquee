"""Marquee Lighted Sign Project - main"""

# Video of variety with steady cam
# Modify back cover
# Picture with back cover
# Paint touch-up w/ brush?
# Video to kevin and paul
# Test cleanup()
# 4 step sequence - 4 horizontal rows
# Test seq_rotate_build
# Future: remember current light state, ability to flip lights
# # # 0 1 + (identity) - (negation)


import time
import types

from sequences import *
import signs
from signs import LIGHT_COUNT

def do_sequence(sequence, count=1, delay=0, stop=None):
    """Execute sequence count times, with delay seconds in between.
       If stop is specified, end the sequence just before the nth pattern."""
    for _ in range(count):
        for i, lights in enumerate(sequence()):
            if stop is not None and i == stop:
                break
            sign.set_lights(lights)
            sign.wait_for_interrupt(delay)

def simple_mode(sequence, delay=None):
    """Execute sequence indefinitely, with delay seconds in between.
       Delay=None is an infinite delay, so in this case
       the sequence should have only 1 step."""
    def template():
        while True:
            do_sequence(sequence, 1, delay)
    return template

def indicate_mode_desired():
    """Show user what desired mode number is currently selected."""
    assert MODE_COUNT <= LIGHT_COUNT, "Cannot indicate this many modes"
    do_sequence(seq_all_on)
    time.sleep(0.6)
    do_sequence(seq_rotate_build, delay=0.2, stop=mode.desired)

def mode_selection():
    """User presses the button to select 
       the next mode to execute."""
    while True:
        # Button was pressed
        if mode.desired is None:
            # Just now entering selection mode
            mode.desired = mode.previous
        else:
            mode.desired += 1
            if mode.desired == MODE_COUNT:
                mode.desired = 1
        indicate_mode_desired()
        sign.interrupt_reset()
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

def mode_rhythmic_demo():
    """Perform a rhythmic demonstration."""
    while True:

        do_sequence(seq_all_on)



        do_sequence(
            lambda: seq_build_rows(pattern="1", from_top=True),
            count=4,
            delay=1,
        )
        do_sequence(
            lambda: seq_build_rows(pattern="1", from_top=False),
            count=4,
            delay=1,
        )
        do_sequence(
            lambda: seq_build_rows(pattern="0", from_top=True),
            count=4,
            delay=1,
        )
        do_sequence(
            lambda: seq_build_rows(pattern="0", from_top=False),
            count=4,
            delay=1,
        )
        
        do_sequence(
            seq_blink_alternate, 
            count=2, 
            delay=0.8,
        )
        do_sequence(
            seq_blink_all,
            count=2, 
            delay=0.8,
        )

        do_sequence(
            lambda: seq_move(from_left=True),
            count=2, 
            delay=0.4,
            stop=4,
        )
        do_sequence(
            lambda: seq_move(from_left=False),
            count=2, 
            delay=0.4,
            stop=4,
        )
        do_sequence(
            lambda: seq_build(from_left=True),
            count=2, 
            delay=0.4,
            stop=4,
        )
        do_sequence(
            lambda: seq_build(from_left=False),
            count=2, 
            delay=0.4,
            stop=4,
        )
        do_sequence(
            lambda: seq_rotate('1000000000', clockwise=True), 
            count=2, 
            delay=0.2,
            stop=4,
        )
        do_sequence(
            lambda: seq_rotate('0000000001', clockwise=False), 
            count=2, 
            delay=0.2,
            stop=4,
        )
        do_sequence(
            lambda: seq_rotate('0111111111', clockwise=True), 
            count=2, 
            delay=0.2,
            stop=4,
        )
        do_sequence(
            lambda: seq_rotate('1111111110', clockwise=False), 
            count=2, 
            delay=0.2,
            stop=4,
        )
        do_sequence(
            lambda: seq_rotate('1100000000', clockwise=True),
            count=2, 
            delay=0.1,
            stop=8,
        )
        do_sequence(
            lambda: seq_rotate('1111111100', clockwise=False),
            count=2,
            delay=0.1,
            stop=8,
        )
        
        #
        do_sequence(
            seq_rotate,
            count=8,
            delay=0.04,
        )

        # !!!! OR, just rotate 8 lights per beat, rather than 10

        # !!!! do_sequence(seq_rotate, 7, 0.04, stop=9)

        do_sequence(seq_all_on)
        sign.wait_for_interrupt(6.4)
        do_sequence(seq_all_off)
        sign.wait_for_interrupt(900)

        do_sequence(ft.partial(seq_rotate, '1100000000'), 4, 0.2)
        do_sequence(ft.partial(seq_rotate, '1101000000'), 4, 0.2)
        do_sequence(ft.partial(seq_rotate, '1101010000'), 4, 0.2)
        do_sequence(ft.partial(seq_rotate, '1101010100'), 4, 0.2)
        do_sequence(ft.partial(seq_rotate, '1111111110'), 4, 0.2)
        sign.wait_for_interrupt(900)

def setup():
    """Set up devices and initial state."""
    global mode
    global sign
    mode = types.SimpleNamespace()
    mode.current = 7
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
    simple_mode(seq_blink_all, delay=1),
    simple_mode(seq_blink_alternate, delay=1),
    mode_rhythmic_demo,
]
MODE_COUNT = len(MODES)

if __name__ == "__main__":
    main()
